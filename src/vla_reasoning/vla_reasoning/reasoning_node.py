import rclpy
from rclpy.node import Node

from vla_interfaces.msg import DetectedObject, VLAPlan
from geometry_msgs.msg import PoseStamped


class ReasoningNode(Node):

    def __init__(self):
        super().__init__('reasoning_node')

        self.sub = self.create_subscription(
            DetectedObject,
            '/detected_object',
            self.callback,
            10
        )

        self.pub = self.create_publisher(
            VLAPlan,
            '/vla_plan',
            10
        )

        self.last_id = -1

    def callback(self, msg):

        if msg.id == self.last_id:
            return

        self.last_id = msg.id

        plan = VLAPlan()
        plan.action = "pick"
        plan.target = msg.label

        goal = PoseStamped()
        goal.header.frame_id = "panda_link0"
        goal.header.stamp = self.get_clock().now().to_msg()

        goal.pose.position.x = float(msg.x)
        goal.pose.position.y = float(msg.y)
        goal.pose.position.z = 0.2

        goal.pose.orientation.w = 1.0

        plan.goal_pose = goal

        self.pub.publish(plan)

        self.get_logger().info(
            f"PLAN: PICK {msg.label} at ({msg.x:.2f}, {msg.y:.2f})"
        )


def main():
    rclpy.init()
    node = ReasoningNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()