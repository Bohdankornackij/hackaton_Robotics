import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class CubeDetector(Node):
    def __init__(self):
        super().__init__('cube_detector')
        self.subscription = self.create_subscription(Image, '/hand_camera/image_raw', self.image_callback, 10)
        self.bridge = CvBridge()
        self.get_logger().info('Зір активовано! Шукаю кубики...')

    def image_callback(self, msg):
        # Конвертуємо зображення з ROS в OpenCV
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # Діапазони кольорів (HSV)
        colors = {
            'RED': ([0, 100, 100], [10, 255, 255]),
            'GREEN': ([40, 40, 40], [80, 255, 255]),
            'BLUE': ([100, 100, 100], [130, 255, 255])
        }

        for color_name, (lower, upper) in colors.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            moments = cv2.moments(mask)
            
            if moments['m00'] > 500: # Якщо знайшли достатньо велику пляму
                cx = int(moments['m10'] / moments['m00'])
                cy = int(moments['m01'] / moments['m00'])
                self.get_logger().info(f'Знайдено {color_name} куб: піксель [{cx}, {cy}]')
                
                # Малюємо коло для візуалізації
                cv2.circle(cv_image, (cx, cy), 10, (255, 255, 255), -1)
                cv2.putText(cv_image, color_name, (cx-20, cy-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        cv2.imshow("Зір робота", cv_image)
        cv2.waitKey(1)

def main():
    rclpy.init()
    node = CubeDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
