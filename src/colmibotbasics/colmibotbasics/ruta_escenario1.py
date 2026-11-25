import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, LaserScan, Image


def normalizar_angulo(angulo):
    while angulo > math.pi:
        angulo -= 2.0 * math.pi
    while angulo < -math.pi:
        angulo += 2.0 * math.pi
    return angulo


def quaternion_a_yaw(q):
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


class RutaEscenario1(Node):
    def __init__(self):
        super().__init__('ruta_escenario1')

        # Pose inicial en el mundo (coincide con gazebo_escenario1.launch.py)
        self.spawn_x = 6.5
        self.spawn_y = 4.5
        self.spawn_yaw = -1.5708

        # Waypoints centrados en los pasillos reales del almacen
        self.waypoints = [
            (6.5,   3.05),   # 1. Salir del almacen al centro del pasillo superior
            (-6.0,  3.05),   # 2. Recorrer pasillo superior hacia la izquierda
            (-6.0, -3.05),   # 3. Bajar por pasillo izquierdo
            (-3.0, -3.05),   # 4. Avanzar al pasillo entre Isla 1 e Isla 2
            (-3.0,  3.05),   # 5. Subir entre Isla 1 e Isla 2
            (-0.10, 3.05),   # 6. Cruzar al pasillo entre Isla 2 y Empaquetamiento
            (-0.10, -3.05),  # 7. Bajar hasta el centro del pasillo inferior
            (-3.0, -3.05),   # 8. Regresar brevemente a la izquierda
            (7.2,  -3.05),   # 9. Girar 180° sobre su eje y salir hacia la derecha
        ]

        self.indice_wp = 0
        self.estado = 'GIRAR'  # 'GIRAR', 'PAUSA', 'AVANZAR', 'FIN'
        self.contador_pausa = 0

        # Variables de estado de sensores
        self.odom_recibida = False
        self.imu_recibida = False
        self.imu_yaw_inicial = None
        self.yaw = self.spawn_yaw

        self.odom_x_prev = None
        self.odom_y_prev = None
        self.x = self.spawn_x
        self.y = self.spawn_y

        # Banderas listas para futuras integraciones (cámara / ToF)
        self.obstaculo_detectado = False
        self.distancia_min_tof = 4.0

        # Publicador y suscriptores
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_subscription(Imu, '/imu', self.imu_callback, 10)
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.create_subscription(LaserScan, '/tof/center/scan', self.tof_callback, 10)
        self.create_subscription(Image, '/camera/image_raw', self.camara_callback, 10)

        # Bucle de control a 20 Hz
        self.timer = self.create_timer(0.05, self.ciclo_control)
        self.get_logger().info('Nodo ruta_escenario1 iniciado (modo fusion IMU + Odometria).')

    def imu_callback(self, msg):
        yaw_crudo = quaternion_a_yaw(msg.orientation)
        if self.imu_yaw_inicial is None:
            self.imu_yaw_inicial = yaw_crudo
        delta_yaw = normalizar_angulo(yaw_crudo - self.imu_yaw_inicial)
        self.yaw = normalizar_angulo(self.spawn_yaw + delta_yaw)
        self.imu_recibida = True

    def odom_callback(self, msg):
        if not self.imu_recibida:
            return

        ox = msg.pose.pose.position.x
        oy = msg.pose.pose.position.y

        if self.odom_x_prev is None:
            self.odom_x_prev = ox
            self.odom_y_prev = oy
            self.odom_recibida = True
            return

        # Distancia recorrida en el ultimo paso segun encoders
        dx_odom = ox - self.odom_x_prev
        dy_odom = oy - self.odom_y_prev
        paso = math.hypot(dx_odom, dy_odom)

        # Detectar si el movimiento fue hacia adelante o hacia atras respecto al yaw de odom
        oyaw = quaternion_a_yaw(msg.pose.pose.orientation)
        direccion = math.cos(math.atan2(dy_odom, dx_odom) - oyaw) if paso > 1e-5 else 1.0
        signo = 1.0 if direccion >= 0 else -1.0

        # Proyectar el avance usando el rumbo real de la IMU (evita deriva angular)
        self.x += signo * paso * math.cos(self.yaw)
        self.y += signo * paso * math.sin(self.yaw)

        self.odom_x_prev = ox
        self.odom_y_prev = oy
        self.odom_recibida = True

    def tof_callback(self, msg):
        validos = [r for r in msg.ranges if msg.range_min < r < msg.range_max]
        if validos:
            self.distancia_min_tof = min(validos)
        # En el futuro se puede activar:
        # self.obstaculo_detectado = (self.distancia_min_tof < 0.35)

    def camara_callback(self, msg):
        # Espacio reservado para procesamiento de vision o captura de fotos
        pass

    def ciclo_control(self):
        if not (self.odom_recibida and self.imu_recibida) or self.estado == 'FIN':
            return

        cmd = Twist()

        if self.obstaculo_detectado:
            self.cmd_pub.publish(cmd)
            return

        objetivo_x, objetivo_y = self.waypoints[self.indice_wp]
        dx = objetivo_x - self.x
        dy = objetivo_y - self.y
        distancia = math.hypot(dx, dy)
        angulo_deseado = math.atan2(dy, dx)
        error_angular = normalizar_angulo(angulo_deseado - self.yaw)

        if self.estado == 'GIRAR':
            if abs(error_angular) > 0.025:  # Tolerancia ~1.4 grados con IMU
                vel_angular = max(min(1.4 * error_angular, 0.55), -0.55)
                if abs(vel_angular) < 0.20:
                    vel_angular = 0.20 if vel_angular > 0 else -0.20
                cmd.angular.z = vel_angular
            else:
                self.estado = 'PAUSA'
                self.contador_pausa = 5  # 0.25 s de estabilizacion antes de avanzar
                self.get_logger().info(
                    f'Alineado (IMU) hacia WP {self.indice_wp + 1}: ({objetivo_x}, {objetivo_y})'
                )

        elif self.estado == 'PAUSA':
            if self.contador_pausa > 0:
                self.contador_pausa -= 1
            else:
                self.estado = 'AVANZAR'

        elif self.estado == 'AVANZAR':
            if distancia > 0.07:
                # Si en un tramo largo el rumbo se desvia >12°, re-alinear en el sitio
                if abs(error_angular) > 0.21:
                    self.estado = 'GIRAR'
                else:
                    cmd.linear.x = min(0.30, max(0.14, 0.55 * distancia))
                    cmd.angular.z = max(min(1.5 * error_angular, 0.35), -0.35)
            else:
                self.get_logger().info(
                    f'Waypoint {self.indice_wp + 1} alcanzado en ({self.x:.2f}, {self.y:.2f})'
                )
                self.indice_wp += 1
                if self.indice_wp >= len(self.waypoints):
                    self.estado = 'FIN'
                    self.get_logger().info('Ruta completada con exito.')
                else:
                    self.estado = 'GIRAR'

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    nodo = RutaEscenario1()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.cmd_pub.publish(Twist())
        nodo.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()