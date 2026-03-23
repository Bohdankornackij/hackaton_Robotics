import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from std_msgs.msg import Header
from sensor_msgs.msg import Image
import cv2
import numpy as np

class VisionCubeToucher(Node):
    def __init__(self):
        super().__init__('cube_detector')
        
        self.publisher_ = self.create_publisher(
            JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10)
        
        self.image_sub = self.create_subscription(
            Image, '/hand_camera/image_raw', self.image_callback, 10)
        
        self.step = 0
        self.current_image = None
        self.cube_confirmed = False
        self.waiting_for_confirmation = False
        self.confirmation_count = 0

        self.positions = [
            [0.0000, 1.2973, 1.2973, 0.1382, -1.2973, -1.4355, 1.4355, 0.0],
            [1.5508, 1.2935, 1.2935, 0.4416, -1.2935, -1.7350, 1.7350, 0.0],
            [-2.3457, 1.3683, 1.3683, -0.1824, -1.3683, -1.1860, 1.1860, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ]

        self.cube_colors = ['RED', 'GREEN', 'BLUE']

        self.color_ranges = {
            'RED':   [([0, 120, 70], [10, 255, 255]), ([170, 120, 70], [180, 255, 255])],
            'GREEN': [([35, 50, 50], [90, 255, 255])],
            'BLUE':  [([85, 30, 30], [155, 255, 255])],
        }

        # Таймер руху — кожні 7 секунд
        self.move_timer = self.create_timer(7.0, self.move_to_next)
        # Таймер відображення — 30 Гц
        self.display_timer = self.create_timer(0.033, self.show_image)
        
        self.get_logger().info('Vision Cube Toucher запущено!')

    def image_callback(self, msg):
        img_array = np.frombuffer(msg.data, dtype=np.uint8)
        img = img_array.reshape((msg.height, msg.width, 3))
        self.current_image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        if self.waiting_for_confirmation and 0 < self.step <= len(self.cube_colors):
            color = self.cube_colors[self.step - 1]
            found, cx, cy = self.detect_color(color)
            if found:
                self.confirmation_count += 1
                if self.confirmation_count == 6:
                    self.get_logger().info(f'Досяг {color} куба!')
                elif self.confirmation_count > 6:
                    self.get_logger().info(f'Знайдено {color} куб: піксель [{cx}, {cy}]')

    def detect_color(self, color_name):
        if self.current_image is None:
            return False, 0, 0
        
        hsv = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2HSV)
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        for (low, high) in self.color_ranges[color_name]:
            mask |= cv2.inRange(hsv, np.array(low), np.array(high))

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > 50:
                M = cv2.moments(largest)
                if M['m00'] > 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    return True, cx, cy
        return False, 0, 0

    def show_image(self):
        if self.current_image is None:
            return

        display = self.current_image.copy()
        color_name = self.cube_colors[self.step - 1] if 0 < self.step <= len(self.cube_colors) else None

        if color_name:
            found, cx, cy = self.detect_color(color_name)
            if found:
                cv2.circle(display, (cx, cy), 10, (255, 255, 255), -1)
                cv2.putText(display, color_name, (cx - 20, cy - 15),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow('Зір робота', display)
        cv2.waitKey(1)

    def move_to_next(self):
        if self.step >= len(self.positions):
            self.get_logger().info('Завдання виконано!')
            self.move_timer.cancel()
            cv2.destroyAllWindows()
            return

        if self.step < len(self.cube_colors):
            self.get_logger().info(f'Рухаюсь до {self.cube_colors[self.step]} куба...')
        else:
            self.get_logger().info('Повертаюсь додому...')

        msg = JointTrajectory()
        msg.header = Header()
        msg.header.frame_id = ''
        msg.header.stamp.sec = 0
        msg.header.stamp.nanosec = 0
        msg.joint_names = ['mg400_j1', 'mg400_j2_1', 'mg400_j2_2',
                           'mg400_j3_1', 'mg400_j3_2', 'mg400_j4_1', 'mg400_j4_2', 'mg400_j5']

        point = JointTrajectoryPoint()
        point.positions = self.positions[self.step]
        point.velocities = [0.0] * 8
        point.time_from_start = Duration(sec=4, nanosec=0)

        msg.points = [point]
        self.publisher_.publish(msg)
        
        self.step += 1
        self.waiting_for_confirmation = True
        self.confirmation_count = 0

def main(args=None):
    rclpy.init(args=args)
    node = VisionCubeToucher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    cv2.destroyAllWindows()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()