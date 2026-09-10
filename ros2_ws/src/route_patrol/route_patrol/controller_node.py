import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Point
import time
import math


class ControllerNode(Node):

    def __init__(self):
        super().__init__('controller_node')

        self.x = None
        self.y = None

        self.target_x = 4.0
        self.target_y = 3.0

        self.position_subscription = self.create_subscription(
            Point,
            'position',
            self.position_callback,
            10
        )

        self.publisher = self.create_publisher(
            Twist,
            'cmd_vel',
            10
        )

        self.timer = self.create_timer(
            0.05, self.publish_velocity
            )

    def publish_velocity(self):

        if self.x is None or self.y is None:
            return  # Position not yet received

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        msg = Twist()

        if distance <= 0.01:
            msg.linear.x = 0.0
            msg.linear.y = 0.0
        else:
            msg.linear.x = 0.5 * dx
            msg.linear.y = 0.5 * dy

            if abs(msg.linear.x) > 2.0 or abs(msg.linear.y) > 2.0:
                msg.linear.x = 2.0 * (dx / distance)
                msg.linear.y = 2.0 * (dy / distance)

        self.publisher.publish(msg)

        self.get_logger().info(
            f'Sent velocity: vx={msg.linear.x:.2f}, vy={msg.linear.y:.2f}'
            f' | Distance to target: {distance:.3f} m'
        )

    def position_callback(self, msg):
        self.x = msg.x
        self.y = msg.y

        self.get_logger().info(
            f'Received position: x={self.x:.3f}, y={self.y:.3f}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = ControllerNode()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()