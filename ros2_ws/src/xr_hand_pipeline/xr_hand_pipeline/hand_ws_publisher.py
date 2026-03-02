import asyncio
import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import websockets

HOST = "0.0.0.0"
PORT = 8765

class HandWSPublisher(Node):

    def __init__(self):
        super().__init__('hand_ws_publisher')
        self.publisher_ = self.create_publisher(String, '/hand_pose', 10)
        self.get_logger().info("WebSocket ROS Publisher started")

        # Start websocket server in separate thread
        thread = threading.Thread(target=self.start_websocket_server)
        thread.daemon = True
        thread.start()

    def start_websocket_server(self):
        asyncio.run(self.websocket_main())

    async def websocket_main(self):
        self.get_logger().info(f"🚀 WebSocket server running on ws://{HOST}:{PORT}")
        async with websockets.serve(self.handle_client, HOST, PORT):
            await asyncio.Future()  # run forever

    async def handle_client(self, websocket):
        self.get_logger().info("✅ Quest connected")

        try:
            async for message in websocket:
                msg = String()
                msg.data = message
                self.publisher_.publish(msg)
        except websockets.exceptions.ConnectionClosed:
            self.get_logger().info("❌ Quest disconnected")

def main(args=None):
    rclpy.init(args=args)
    node = HandWSPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()