import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Point
import time


class ChassisNode(Node):

    def __init__(self):
        super().__init__('chassis_node')

        self.vx = 0.0
        self.vy = 0.0

        self.x = 0.0
        self.y = 0.0
        self.last_update_time = time.monotonic()

        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.velocity_callback,
            10
        )

        self.position_publisher = self.create_publisher(
            Point,
            'position',
            10
        )

        self.timer = self.create_timer(
                    0.05, self.update_position
                    )

    def velocity_callback(self, msg):

        self.update_position()
        
        if msg.linear.x > 2.0:
            self.vx = 2.0
        elif msg.linear.x < -2.0:
            self.vx = -2.0
        else:
            self.vx = msg.linear.x

        if msg.linear.y > 2.0:
            self.vy = 2.0
        elif msg.linear.y < -2.0:
            self.vy = -2.0
        else:
            self.vy = msg.linear.y

        self.get_logger().info(
            f'Received velocity: vx={msg.linear.x:.2f}, vy={msg.linear.y:.2f}'
            f' | Clamped velocity: vx={self.vx:.2f}, vy={self.vy:.2f}'
        )

    def update_position(self):
        now = time.monotonic()
        dt = now - self.last_update_time

        self.x += self.vx * dt
        self.y += self.vy * dt

        self.last_update_time = now

        msg = Point()
        msg.x = self.x
        msg.y = self.y
        self.position_publisher.publish(msg)

        self.get_logger().info(
            f'Position: x={self.x:.3f}, y={self.y:.3f}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = ChassisNode()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()