"""ROS 2 node: runs the cardboard-box detector on camera images.

Subscribes to a sensor_msgs/Image topic (default /camera/image_raw, which
comes from the Gazebo camera through ros_gz_bridge, or later from the
real C920) and runs detect_boxes() from box_detector.py on each frame.

Parameters:
  image_topic  (str)  topic to subscribe to       [/camera/image_raw]
  show_windows (bool) show OpenCV windows         [true]
  tuning       (bool) show HSV sliders to tune    [false]
"""
import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image

from colmibotbasics import box_detector
from colmibotbasics.box_detector import detect_boxes


class BoxDetectorNode(Node):
    def __init__(self):
        super().__init__("box_detector")

        self.declare_parameter("image_topic", "/camera/image_raw")
        self.declare_parameter("show_windows", True)
        self.declare_parameter("tuning", False)

        topic = self.get_parameter("image_topic").value
        self.show_windows = self.get_parameter("show_windows").value
        self.tuning = self.get_parameter("tuning").value

        self.bridge = CvBridge()
        self.last_count = None

        if self.show_windows and self.tuning:
            box_detector.create_controls()

        # Sensor-data QoS (best effort) is compatible with both reliable
        # and best-effort camera publishers.
        self.subscription = self.create_subscription(
            Image, topic, self.image_callback, qos_profile_sensor_data
        )
        self.get_logger().info(f"Waiting for camera images on {topic} ...")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            if self.show_windows and self.tuning:
                low, high = box_detector.read_controls()
                annotated, mask, detections = detect_boxes(frame, low, high)
            else:
                annotated, mask, detections = detect_boxes(frame)
        except Exception as exc:
            self.get_logger().error(f"Image processing failed: {exc}")
            return

        if self.show_windows:
            cv2.imshow("Colmibot - Box Detection", annotated)
            cv2.imshow("Colmibot - Cardboard Mask", mask)
            cv2.waitKey(1)

        # Log only when the number of boxes changes (avoids 10 msgs/s spam).
        if len(detections) != self.last_count:
            self.last_count = len(detections)
            summary = [(d["center"], d["score"]) for d in detections]
            self.get_logger().info(f"{len(detections)} box(es): {summary}")


def main(args=None):
    rclpy.init(args=args)
    node = BoxDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
