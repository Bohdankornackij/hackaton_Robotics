import rclpy
from rclpy.node import Node

class SanyaRobotNode(Node):
    def __init__(self):
        super().__init__('sanya_robot_node')
        self.get_logger().info('Base infrastructure')

def main(args=None):
    rclpy.init(args=args)
    node = SanyaRobotNode()
    # Це змусить ноду працювати і чекати команд
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()