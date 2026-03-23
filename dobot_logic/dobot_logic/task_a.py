import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class CubeToucher(Node):
    def __init__(self):
        super().__init__('cube_toucher')
        # Зміни топік на той, який використовується у твоєму Gazebo (часто це /joint_trajectory_controller/joint_trajectory)
        self.publisher_ = self.create_publisher(JointTrajectory, '/mg400_controller/joint_trajectory', 10)
        
        # Таймер буде викликати рух кожні 4 секунди
        self.timer = self.create_timer(4.0, self.timer_callback)
        self.step = 0
        
        # Орієнтовні кути поворотів суглобів для 3 кубів (в радіанах)
        self.positions = [
            [0.5, 0.2, 0.2, 0.0],   # Куб 1 (Червоний)
            [0.0, 0.4, 0.1, 0.0],   # Куб 2 (Зелений)
            [-0.5, 0.2, 0.2, 0.0],  # Куб 3 (Синій)
            [0.0, 0.0, 0.0, 0.0]    # Повернення в домашню позицію
        ]

    def timer_callback(self):
        if self.step >= len(self.positions):
            self.get_logger().info('Всі куби пройдено! Завершую роботу.')
            self.timer.cancel()
            return

        msg = JointTrajectory()
        # Назви суглобів для MG400
        msg.joint_names = ['joint1', 'joint2', 'joint3', 'joint4']
        
        point = JointTrajectoryPoint()
        point.positions = self.positions[self.step]
        point.time_from_start = Duration(sec=3, nanosec=0) # Рух триватиме 3 секунди
        
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
