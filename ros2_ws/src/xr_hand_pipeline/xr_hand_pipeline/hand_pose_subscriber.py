import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class HandPoseSubscriber(Node):

    def __init__(self):
        super().__init__('hand_pose_subscriber')
        self.subscription = self.create_subscription(
            String,
            '/hand_pose',
            self.listener_callback,
            10
        )
        self.get_logger().info("Subscriber ready")

    def listener_callback(self, msg):
        data = json.loads(msg.data)
        print("Left:", data["left_hand"]["pos"])
        print("Right:", data["right_hand"]["pos"])
        print("-" * 30)
        print("Whole Data: ", data)
        print("-" * 30)


def main(args=None):
    rclpy.init(args=args)
    node = HandPoseSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()