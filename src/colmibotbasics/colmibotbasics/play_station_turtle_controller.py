import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist

AXIS_X = 3
AXIS_Y = 4

MAX_LINEAR = 2.0
MAX_ANGULAR = 2.0

class PlayStationTurtleController(Node):
    def __init__(self):
        super().__init__('play_station_turtle_controller')
        
        self.subscription_ = self.create_subscription(
            Joy,
            '/joy',
            self.ps_joystick_callback,
            10
        )
        
        self.publisher_ = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )
        
        self.get_logger().info('Play station turtle controller ha iniciado')
        
    def ps_joystick_callback(self, msg):
        twist = Twist()
        
        x = msg.axes[AXIS_X]
        y = msg.axes[AXIS_Y]
        
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
        
