import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from geometry_msgs.msg import PointStamped

import cv2
import numpy as np
from cv_bridge import CvBridge
from vla_interfaces.msg import DetectedObject
class PerceptionNode(Node):

    def __init__(self):
        super().__init__("perception_node")
        self.bridge = CvBridge()

        self.subscription = self.create_subscription(
            Image,
            "/image_raw",
            self.image_callback,
            10
        )

        self.objects = {
            "red_block": [0.4, 0.0, 0.1],
            "blue_block": [0.5, 0.2, 0.1],
            "bin": [0.2, -0.3, 0.1]
        }
        self.pub = self.create_publisher(
            DetectedObject,
            "/detected_object",
            10
        )
        self.get_logger().info("Perception node ready")

    # def image_callback(self, msg):

    #     image = self.bridge.imgmsg_to_cv2(
    #         msg,
    #         desired_encoding="bgr8"
    #     )

    #     hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #     lower_red = np.array([0, 100, 100])
    #     upper_red = np.array([10, 255, 255])

    #     mask = cv2.inRange(hsv, lower_red, upper_red)

    #     M = cv2.moments(mask)

    #     if M["m00"] > 0:

    #         cx = int(M["m10"] / M["m00"])
    #         cy = int(M["m01"] / M["m00"])

    #         self.get_logger().info(
    #             f"Red object detected at pixel ({cx}, {cy})"
    #         )
    def image_callback(self, msg):

        self.get_logger().info("Frame received")

        image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])

        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

        mask = mask1 | mask2

        M = cv2.moments(mask)

        if M["m00"] > 0:

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            msg = DetectedObject()
            msg.label = "red_block"
            msg.x = float(cx)
            msg.y = float(cy)
            msg.confidence = 1.0

            self.pub.publish(msg)

            self.get_logger().info(
                f"Published DetectedObject: ({cx}, {cy})"
            )


def main():
    rclpy.init()
    node = PerceptionNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()