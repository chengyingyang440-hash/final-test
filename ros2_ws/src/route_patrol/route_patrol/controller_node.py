import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Point
import time
import math

from route_patrol.route_data import WAYPOINTS, build_route ,build_patrol_route

class ControllerNode(Node):

    def __init__(self):
        super().__init__('controller_node')

        self.declare_parameter('mode', 'point')
        self.declare_parameter('start', 1)
        self.declare_parameter('end', 5)

        mode = self.get_parameter('mode').value
        start = self.get_parameter('start').value
        end = self.get_parameter('end').value

        self.x = None
        self.y = None

        if mode == 'patrol':
            self.route = build_patrol_route(start)
        elif mode == 'point':
            self.route = build_route(start, end)
        else:
            raise ValueError('模式必须是 "point" 或 "patrol"')

        if len(self.route) == 1:
            self.target_index = 0
            self.finished = True
        else:
            self.target_index = 1
            self.finished = False

        target_id = self.route[self.target_index]
        self.target_x, self.target_y = WAYPOINTS[target_id]

        self.get_logger().info(f'Route: {self.route}')

        if self.finished:
            self.get_logger().info(
                f'Task completed: No movement needed, already at the target waypoint {self.route[0]}'
            )

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

        if self.finished:
            msg.linear.x = 0.0
            msg.linear.y = 0.0
        elif distance <= 0.01:
            reached_id = self.route[self.target_index]
            self.get_logger().info(f'Reached waypoint: {reached_id}')

            self.target_index += 1

            if self.target_index >= len(self.route):
                self.finished = True
                self.get_logger().info(
                    f'Task completed: end = {self.route[-1]}'
                    f' | Final position: x={self.x:.3f}, y={self.y:.3f}'
                )
            else:
                target_id = self.route[self.target_index]
                self.target_x, self.target_y = WAYPOINTS[target_id]
                self.get_logger().info(f'Next waypoint: {target_id}')

        else:
            msg.linear.x = 0.5 * dx
            msg.linear.y = 0.5 * dy

            if abs(msg.linear.x) > 2.0 or abs(msg.linear.y) > 2.0:
                msg.linear.x = 2.0 * dx / distance
                msg.linear.y = 2.0 * dy / distance

        self.publisher.publish(msg)
        self.get_logger().debug(
            f'Sent velocity: vx={msg.linear.x:.2f}, vy={msg.linear.y:.2f}'
            f' | Distance to target: {distance:.3f} m'
        )

    def position_callback(self, msg):
        self.x = msg.x
        self.y = msg.y

        self.get_logger().debug(
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