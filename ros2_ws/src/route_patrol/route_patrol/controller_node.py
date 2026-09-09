import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class ControllerNode(Node):

    def __init__(self):
        super().__init__('controller_node')

        self.publisher = self.create_publisher(
            Twist,
            'cmd_vel',
            10
        )

        self.timer = self.create_timer(
            0.5, self.publish_velocity
            )

    def publish_velocity(self):
        msg = Twist()
        msg.linear.x = 1.0
        msg.linear.y = -0.5

        self.publisher.publish(msg)

        self.get_logger().info(
            f'Sent velocity: vx={msg.linear.x:.2f}, vy={msg.linear.y:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = ControllerNode()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()