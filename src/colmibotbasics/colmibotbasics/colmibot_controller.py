
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
import time

AXIS_X = 3
AXIS_Y = 4
BUTTON_X = 0

MAX_LINEAR = 0.15
MAX_ANGULAR = 0.8
DEADZONE = 0.1
TIMEOUT = 0.5


class ColmibotController(Node):

    def __init__(self):
        super().__init__('colmibot_controller')

        self.subscription = self.create_subscription(
            Joy, '/joy', self.joy_callback, 10
        )

        self.publisher = self.create_publisher(
            Twist, '/cmd_vel', 10
        )

        self.last_joy_time = time.monotonic()
        self.command = Twist()

        # Publica continuamente y detiene el robot
        # si se pierde la conexion con el control.
        self.timer = self.create_timer(0.05, self.publish_command)

        self.get_logger().info('Control PlayStation listo')

    def deadzone(self, value):
        return 0.0 if abs(value) < DEADZONE else value

    def joy_callback(self, msg):
        self.last_joy_time = time.monotonic()
        self.command = Twist()

        if len(msg.axes) <= max(AXIS_X, AXIS_Y):
            return

        if len(msg.buttons) <= BUTTON_X:
            return

        # Solo mover mientras se presiona X
        if msg.buttons[BUTTON_X] == 0:
            return

        x = self.deadzone(msg.axes[AXIS_X])
        y = self.deadzone(msg.axes[AXIS_Y])

        self.command.linear.x = y * MAX_LINEAR
        self.command.angular.z = x * MAX_ANGULAR

    def publish_command(self):
        if time.monotonic() - self.last_joy_time > TIMEOUT:
            self.command = Twist()

        self.publisher.publish(self.command)


def main(args=None):
    rclpy.init(args=args)
    node = ColmibotController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publisher.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
