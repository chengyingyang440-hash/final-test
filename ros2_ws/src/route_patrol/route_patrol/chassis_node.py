import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class ChassisNode(Node):

    def __init__(self):
        super().__init__('chassis_node')

        self.vx = 0.0
        self.vy = 0.0

        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.velocity_callback,
            10
        )

    def velocity_callback(self, msg):
        self.vx = msg.linear.x
        self.vy = msg.linear.y

        self.get_logger().info(
            f'Received velocity: vx={self.vx:.2f}, vy={self.vy:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = ChassisNode()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()