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


def main(args=None):
    rclpy.init(args=args)

    node = ChassisNode()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()