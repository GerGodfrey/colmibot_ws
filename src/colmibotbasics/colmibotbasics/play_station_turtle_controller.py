import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist

# Definir los indices de axes que mandan la información del joystick
AXIS_X = 3
AXIS_Y = 4

# Definir maximas velocidades
MAX_LINEAR = 4.0
MAX_ANGULAR = 2.0

class PlayStationTurtleController(Node):
    def __init__(self):
        super().__init__('play_station_turtle_controller')
        
        # Suscripción al nodo joy para leer los valores que manda el control (joy_node) en el tópico joy
        self.subscription_ = self.create_subscription(
            Joy,
            '/joy',
            self.ps_joystick_callback,
            10
        )
        
        # Publica mensajes de tipo twist en cmd_vel para modificar la posición de la tortuga
        self.publisher_ = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )
        
        self.get_logger().info('Play station turtle controller ha iniciado')
        
    def ps_joystick_callback(self, msg):
        twist = Twist()
        
        # Extraer valores de x (angular) y y (lineal)
        x = msg.axes[AXIS_X]
        y = msg.axes[AXIS_Y]
        
        # Multiplicar por la velocidad máxima (para que incremente según la posción del joystick)
        twist.linear.x = y * MAX_LINEAR
        twist.angular.z = x * MAX_ANGULAR
            
        self.publisher_.publish(twist)
        
def main(args=None):

    rclpy.init(args=args)

    node = PlayStationTurtleController()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
        
