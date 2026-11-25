"""Convierte los LaserScan de los 3 ToF simulados en sensor_msgs/Range.

El VL53L1X real entrega UNA distancia por lectura; el ESP32 mandara un
Range por sensor. En Gazebo cada ToF es un gpu_lidar de 9 rayos, asi que
aqui se reduce cada scan a un solo valor: el minimo de los rayos validos
(el obstaculo mas cercano dentro del cono de 27 grados).

Convencion REP 117 para el campo range:
  +inf -> nada detectado dentro del alcance (libre)
  -inf -> algo mas cerca que min_range (demasiado cerca: obstaculo)
  min_range..max_range -> distancia medida

Entradas:  /tof/<nombre>/scan   (sensor_msgs/LaserScan)
Salidas:   /tof/<nombre>/range  (sensor_msgs/Range)
Parametro: sensors (lista de nombres) [center, left, right]
"""
import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan, Range


def scan_to_range_value(ranges, range_min, range_max):
    """Reduce los rayos de un scan a un solo valor segun REP 117."""
    validos = []
    for r in ranges:
        if math.isnan(r):
            continue                    # lectura invalida: se ignora
        if r == -math.inf or r < range_min:
            return -math.inf            # algo pegado al sensor: gana siempre
        if r <= range_max:
            validos.append(r)           # +inf o > max_range = rayo libre
    return min(validos) if validos else math.inf


class TofToRange(Node):
    def __init__(self):
        super().__init__('tof_to_range')
        self.declare_parameter('sensors', ['center', 'left', 'right'])
        nombres = self.get_parameter('sensors').value

        self.pubs = {}
        for nombre in nombres:
            self.pubs[nombre] = self.create_publisher(
                Range, f'/tof/{nombre}/range', 10)
            # El lambda "congela" el nombre para saber de que sensor viene
            self.create_subscription(
                LaserScan, f'/tof/{nombre}/scan',
                lambda msg, n=nombre: self.scan_callback(msg, n),
                qos_profile_sensor_data)

        self.get_logger().info(f'tof_to_range activo para: {nombres}')

    def scan_callback(self, scan, nombre):
        msg = Range()
        msg.header = scan.header                 # mismo tiempo y frame
        msg.radiation_type = Range.INFRARED      # el VL53L1X es laser IR
        msg.field_of_view = scan.angle_max - scan.angle_min  # ~0.471 rad = 27 grados
        msg.min_range = scan.range_min
        msg.max_range = scan.range_max
        msg.range = scan_to_range_value(
            scan.ranges, scan.range_min, scan.range_max)
        self.pubs[nombre].publish(msg)


def main(args=None):
    rclpy.init(args=args)
    nodo = TofToRange()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()