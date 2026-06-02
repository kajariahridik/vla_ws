import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from vla_interfaces.msg import VLAPlan

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import MotionPlanRequest, Constraints, PositionConstraint
from geometry_msgs.msg import PoseStamped
from shape_msgs.msg import SolidPrimitive


class ExecutorNode(Node):

    def __init__(self):
        super().__init__("vla_executor")

        self.client = ActionClient(self, MoveGroup, "/move_action")

        while not self.client.wait_for_server(timeout_sec=1.0):
            self.get_logger().info("Waiting for move_group action server...")

        self.get_logger().info("MoveGroup action ready")

        self.subscription = self.create_subscription(
            VLAPlan,
            "/vla_plan",
            self.plan_callback,
            10
        )

        self.state = "IDLE"

        self.place_map = {
            "bin": (0.2, -0.3, 0.4)
        }

        self.get_logger().info("Executor ready")

    def plan_callback(self, msg):

        if self.state != "IDLE":
            return

        self.get_logger().info(f"Received: {msg.action} {msg.target}")

        self.state = "BUSY"

        if msg.action.lower() == "pick":
            self.go_to_pose(msg.goal_pose)

        elif msg.action.lower() == "place":
            if msg.target in self.place_map:
                x, y, z = self.place_map[msg.target]
                self.go_to_pose_simple(x, y, z)
            else:
                self.get_logger().error("Unknown place target")
                self.state = "IDLE"

    def go_to_pose(self, pose: PoseStamped):
        self.send_goal(pose)

    def go_to_pose_simple(self, x, y, z):
        pose = PoseStamped()
        pose.header.frame_id = "panda_link0"
        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.position.z = float(z)
        pose.pose.orientation.w = 1.0
        self.send_goal(pose)

    def send_goal(self, pose: PoseStamped):

        goal = MoveGroup.Goal()

        req = MotionPlanRequest()
        req.group_name = "panda_arm"
        req.num_planning_attempts = 5
        req.allowed_planning_time = 5.0

        pc = PositionConstraint()
        pc.header.frame_id = "panda_link0"
        pc.link_name = "panda_hand"

        box = SolidPrimitive()
        box.type = SolidPrimitive.SPHERE
        box.dimensions = [0.01]

        pc.constraint_region.primitives.append(box)
        pc.constraint_region.primitive_poses.append(pose.pose)
        pc.weight = 1.0

        constraints = Constraints()
        constraints.position_constraints.append(pc)

        req.goal_constraints.append(constraints)
        goal.request = req

        self.get_logger().info("Sending MoveGroup goal...")

        send_future = self.client.send_goal_async(goal)
        send_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error("Goal rejected")
            self.state = "IDLE"
            return

        self.get_logger().info("Goal accepted")

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().result

        self.get_logger().info(f"Result: {result.error_code.val}")

        self.state = "IDLE"


def main():
    rclpy.init()
    node = ExecutorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()