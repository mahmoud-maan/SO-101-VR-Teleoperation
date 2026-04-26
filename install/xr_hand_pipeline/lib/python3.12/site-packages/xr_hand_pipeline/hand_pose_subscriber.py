import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped


class HandPoseSubscriber(Node):

    def __init__(self):
        super().__init__('hand_pose_subscriber')
        self.create_subscription(PoseStamped, '/left_hand_pose',
                                 self._left_cb, 10)
        self.create_subscription(PoseStamped, '/right_hand_pose',
                                 self._right_cb, 10)
        self.get_logger().info('Subscriber ready — listening on '
                               '/left_hand_pose and /right_hand_pose')

    @staticmethod
    def _fmt(pose_stamped: PoseStamped) -> str:
        p = pose_stamped.pose.position
        o = pose_stamped.pose.orientation
        return (
            f'pos=({p.x:.3f}, {p.y:.3f}, {p.z:.3f})'
            f'quat=({o.x:.3f}, {o.y:.3f}, {o.z:.3f}, {o.w:.3f})'
        )

    def _left_cb(self, msg: PoseStamped):
        print(f'[LEFT ] {self._fmt(msg)}')

    def _right_cb(self, msg: PoseStamped):
        print(f'[RIGHT] {self._fmt(msg)}')
        print('-' * 60)


def main(args=None):
    rclpy.init(args=args)
    node = HandPoseSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()