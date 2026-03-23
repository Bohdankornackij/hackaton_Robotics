import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from std_msgs.msg import Header

class CubeToucher(Node):
    def __init__(self):
        super().__init__('cube_toucher')
        self.publisher_ = self.create_publisher(JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10)
        self.timer = self.create_timer(5.0, self.timer_callback)
        self.step = 0

        # Позиції з твого робочого main.py (тільки 5 суглобів які контролер знає)
        self.positions = [
            [0.0000, 1.2973, 1.2973, 0.1382, -1.2973, -1.4355, 1.4355, 0.0],
            [1.5508, 1.2935, 1.2935, 0.4416, -1.2935, -1.7350, 1.7350, 0.0],
            [-2.3457, 1.3683, 1.3683, -0.1824, -1.3683, -1.1860, 1.1860, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ]

    def timer_callback(self):
        if self.step >= len(self.positions):
            self.get_logger().info('Всі куби пройдено!')
            self.timer.cancel()
            return

        msg = JointTrajectory()
        msg.header = Header()
        msg.header.frame_id = ''
        msg.header.stamp.sec = 0
        msg.header.stamp.nanosec = 0
        msg.joint_names = ['mg400_j1', 'mg400_j2_1', 'mg400_j2_2', 'mg400_j3_1', 'mg400_j3_2', 'mg400_j4_1', 'mg400_j4_2', 'mg400_j5']

        point = JointTrajectoryPoint()
        point.positions = self.positions[self.step]
        point.velocities = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        point.time_from_start = Duration(sec=4, nanosec=0)

        msg.points = [point]
        self.publisher_.publish(msg)
        self.get_logger().info(f'Рухаюсь до позиції {self.step + 1}...')
        self.step += 1

def main(args=None):
    rclpy.init(args=args)
    node = CubeToucher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()