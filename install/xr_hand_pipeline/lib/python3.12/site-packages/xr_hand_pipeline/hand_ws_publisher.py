import asyncio
import json
import math
import threading

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import websockets

HOST = "0.0.0.0"
PORT = 8765


def qmul(a, b):
    """Hamilton product of two quaternions (x, y, z, w)."""
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    )


def euler_yxz_deg_to_quaternion(rx_deg: float, ry_deg: float, rz_deg: float):
    """Convert Euler angles (degrees, Godot YXZ extrinsic order) to quaternion (x, y, z, w).

    Godot's Basis.get_euler() defaults to EulerOrder.YXZ, meaning the basis is
    reconstructed as R = Ry * Rx * Rz.  We replicate that product in quaternion space.
    """
    rx = math.radians(rx_deg)
    ry = math.radians(ry_deg)
    rz = math.radians(rz_deg)

    # Individual axis quaternions (x, y, z, w)
    qx = (math.sin(rx / 2), 0.0, 0.0, math.cos(rx / 2))
    qy = (0.0, math.sin(ry / 2), 0.0, math.cos(ry / 2))
    qz = (0.0, 0.0, math.sin(rz / 2), math.cos(rz / 2))

    # R = Ry * Rx * Rz  →  q = qy * qx * qz
    return qmul(qmul(qy, qx), qz)


# Fixed rotation quaternion: Godot world frame → ROS REP-103 world frame
#
#   Godot axes:  X = right,   Y = up,      Z = backward
#   ROS axes:    X = forward, Y = left,    Z = up
#
#   Position mapping:  ros_x = -godot_z
#                      ros_y = -godot_x
#                      ros_z =  godot_y
#
#   This rotation matrix converts to quaternion (x=0.5, y=-0.5, z=-0.5, w=0.5)
_Q_GODOT_TO_ROS = (0.5, -0.5, -0.5, 0.5)


def make_pose_stamped(node: 'HandWSPublisher', hand: dict) -> PoseStamped:
    msg = PoseStamped()
    msg.header.stamp = node.get_clock().now().to_msg()
    msg.header.frame_id = 'world'

    # Remap position: Godot Y-up → ROS Z-up
    gx, gy, gz = float(hand['pos'][0]), float(hand['pos'][1]), float(hand['pos'][2])
    msg.pose.position.x = -gz   # forward  = -godot_z (godot Z is backward)
    msg.pose.position.y = -gx   # left     = -godot_x (godot X is right)
    msg.pose.position.z =  gy   # up       =  godot_y (godot Y is up)

    # Convert Euler (Godot YXZ degrees) → quaternion in Godot frame,
    # then rotate into ROS frame: q_ros = Q_GODOT_TO_ROS * q_godot
    rot = hand['rot']
    q_godot = euler_yxz_deg_to_quaternion(rot[0], rot[1], rot[2])
    qx, qy, qz, qw = qmul(_Q_GODOT_TO_ROS, q_godot)
    msg.pose.orientation.x = qx
    msg.pose.orientation.y = qy
    msg.pose.orientation.z = qz
    msg.pose.orientation.w = qw

    return msg


class HandWSPublisher(Node):

    def __init__(self):
        super().__init__('hand_ws_publisher')
        self.left_pub = self.create_publisher(PoseStamped, '/left_hand_pose', 10)
        self.right_pub = self.create_publisher(PoseStamped, '/right_hand_pose', 10)
        self.get_logger().info('HandWSPublisher ready — publishing PoseStamped on '
                               '/left_hand_pose and /right_hand_pose')

        thread = threading.Thread(target=self.start_websocket_server, daemon=True)
        thread.start()

    def start_websocket_server(self):
        asyncio.run(self.websocket_main())

    async def websocket_main(self):
        self.get_logger().info(f'🚀 WebSocket server on ws://{HOST}:{PORT}')
        async with websockets.serve(self.handle_client, HOST, PORT):
            await asyncio.Future()  # run forever

    async def handle_client(self, websocket):
        self.get_logger().info('✅ Quest connected')
        try:
            async for raw in websocket:
                data = json.loads(raw)
                self.left_pub.publish(make_pose_stamped(self, data['left_hand']))
                self.right_pub.publish(make_pose_stamped(self, data['right_hand']))
        except websockets.exceptions.ConnectionClosed:
            self.get_logger().info('❌ Quest disconnected')


def main(args=None):
    rclpy.init(args=args)
    node = HandWSPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()