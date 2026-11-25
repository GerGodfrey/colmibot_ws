"""Freno de seguridad por obstaculo (H3).

Se coloca ENTRE la fuente de velocidad y los motores:

    /cmd_vel_mux  -->  safety_stop  -->  /cmd_vel  -->  Gazebo (DiffDrive) / ESP32
                          ^
    /tof/{center,left,right}/range (sensor_msgs/Range)

Reglas (se evaluan 20 veces por segundo, con el reloj de la simulacion):
  1. Si algun ToF marca menos que el umbral, o -inf (REP 117: demasiado
     cerca), o lleva mas de `range_timeout` s sin publicar -> BLOQUEADO.
  2. BLOQUEADO solo anula el avance (linear.x > 0). Girar y retroceder
     siguen permitidos para que el robot pueda salir.
  3. Histeresis: frena a `stop_distance` y solo vuelve a dejar avanzar
     cuando TODOS los ToF marcan mas de `resume_distance`. Evita que el
     robot "tartamudee" (frena/avanza/frena) justo en el umbral.
  4. Si la fuente de velocidad deja de publicar por mas de `cmd_timeout`
     s, se manda velocidad cero: el DiffDrive de Gazebo no tiene timeout y
     seguiria con la ultima orden para siempre.

Publica siempre en /cmd_vel (aunque sea cero) y el estado en
/safety/obstacle (std_msgs/Bool).
"""
import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import Range
from std_msgs.msg import Bool


def sensor_bloquea(rango, edad, umbral, range_timeout):
    """Devuelve el motivo por el que un sensor bloquea, o None si esta libre."""
    if rango is None or edad > range_timeout:
        return 'sin datos'
    if math.isnan(rango):
        return 'lectura invalida'
    if rango == -math.inf:
        return 'demasiado cerca (-inf)'
    if rango < umbral:              # +inf nunca es < umbral: libre
        return f'{rango:.3f} m'
    return None


class SafetyStop(Node):
    def __init__(self):
        super().__init__('safety_stop')
        self.declare_parameter('sensors', ['center', 'left', 'right'])
        self.declare_parameter('stop_distance', 0.28)    # m: frena por debajo
        self.declare_parameter('resume_distance', 0.33)  # m: libera por encima
        self.declare_parameter('range_timeout', 0.3)     # s sin datos de un ToF
        self.declare_parameter('cmd_timeout', 0.5)       # s sin ordenes -> cero
        self.declare_parameter('rate', 20.0)             # Hz del ciclo

        p = lambda n: self.get_parameter(n).value
        self.stop_distance = p('stop_distance')
        self.resume_distance = p('resume_distance')
        self.range_timeout = p('range_timeout')
        self.cmd_timeout = p('cmd_timeout')
        sensores = p('sensors')

        # Ultima lectura de cada ToF: nombre -> (rango, tiempo en que llego)
        self.lecturas = {n: (None, None) for n in sensores}
        self.ultimo_cmd = Twist()
        self.t_ultimo_cmd = None
        self.bloqueado = False

        for n in sensores:
            self.create_subscription(
                Range, f'/tof/{n}/range',
                lambda msg, n=n: self.range_callback(msg, n), 10)
        self.create_subscription(Twist, '/cmd_vel_mux', self.cmd_callback, 10)

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.obst_pub = self.create_publisher(Bool, '/safety/obstacle', 10)

        self.create_timer(1.0 / p('rate'), self.ciclo)
        self.get_logger().info(
            f'safety_stop activo: frena < {self.stop_distance} m, '
            f'libera > {self.resume_distance} m, sensores {sensores}')

    def ahora(self):
        return self.get_clock().now().nanoseconds * 1e-9   # segundos (sim)

    def range_callback(self, msg, nombre):
        self.lecturas[nombre] = (msg.range, self.ahora())

    def cmd_callback(self, msg):
        self.ultimo_cmd = msg
        self.t_ultimo_cmd = self.ahora()

    def ciclo(self):
        t = self.ahora()

        # 1. Evaluar los sensores (umbral segun el estado: histeresis)
        umbral = self.resume_distance if self.bloqueado else self.stop_distance
        motivos = {}
        for nombre, (rango, t_rango) in self.lecturas.items():
            edad = math.inf if t_rango is None else t - t_rango
            motivo = sensor_bloquea(rango, edad, umbral, self.range_timeout)
            if motivo:
                motivos[nombre] = motivo
        bloqueado = bool(motivos)

        if bloqueado != self.bloqueado:      # avisar solo cuando cambia
            if bloqueado:
                self.get_logger().warn(f'OBSTACULO -> avance bloqueado: {motivos}')
            else:
                self.get_logger().info('Camino libre -> avance permitido')
            self.bloqueado = bloqueado

        # 2. Construir la orden de salida
        cmd = Twist()
        orden_vigente = (self.t_ultimo_cmd is not None
                         and t - self.t_ultimo_cmd <= self.cmd_timeout)
        if orden_vigente:
            cmd.linear.x = self.ultimo_cmd.linear.x
            cmd.angular.z = self.ultimo_cmd.angular.z
            if self.bloqueado and cmd.linear.x > 0.0:
                cmd.linear.x = 0.0           # solo se anula el avance

        self.cmd_pub.publish(cmd)
        self.obst_pub.publish(Bool(data=self.bloqueado))


def main(args=None):
    rclpy.init(args=args)
    nodo = SafetyStop()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            nodo.cmd_pub.publish(Twist())    # al cerrar, dejar el robot quieto
        nodo.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()