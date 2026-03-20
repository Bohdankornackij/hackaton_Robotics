import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from visualization_msgs.msg import Marker, MarkerArray
import math
import time


class DobotTaskController(Node):
    def __init__(self):
        #ініціалзація вузла з ім'ям 'dobot_task_controller'
        super().__init__('dobot_task_controller')

        #створення публішера для відправки масиву маркерів на тему '/visualization_marker_array' з розміром черги 10
        self.marker_pub = self.create_publisher(MarkerArray, '/visualization_marker_array', 10)

        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10) #створення клієнта для сервісу PTP з ім'ям 'mg400_interface/PTP'

        self.get_logger().info('Running in Simulation Mode')  #очікування доступності сервісу PTP

        self.timer_rviz = self.create_timer(0.00001, self.update_rviz) #створення таймера для виклику функції publish_scene кожну секунду

        self.step = 0

        self.moving = False  #прапорець що робот рухається
        self.move_start_time = None  #час початку руху

        self.current_joints = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  #змінна для збереження поточних значень суглобів
        self.joint_names = [
            'mg400_j1', 'mg400_j2_1', 'mg400_j2_2', 'mg400_j3_1', 
            'mg400_j3_2', 'mg400_j4_1', 'mg400_j4_2', 'mg400_j5'
        ]  #змінна для збереження імен суглобів

        self.target_joints = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.lerp_speed = 2.0  # радіан/секунда
        self.arrival_threshold = 0.01  # радіан — точність "досяг цілі"
        self.pause_duration = 1.5       # секунд паузи після досягнення точки
        self.pause_start_time = None
        self.waiting = False
        self._last_rviz_time = None

        self.execute_task()

    def update_rviz(self):
        now = self.get_clock().now().nanoseconds / 1e9

        if self._last_rviz_time is None:
            self._last_rviz_time = now

        dt = now - self._last_rviz_time
        self._last_rviz_time = now
        dt = min(dt, 0.005)

        # Інтерполяція поточних суглобів до цільових
        for i in range(len(self.current_joints)):
            diff = self.target_joints[i] - self.current_joints[i]
            step = self.lerp_speed * dt
            if abs(diff) <= step:
                self.current_joints[i] = self.target_joints[i]
            else:
                self.current_joints[i] += math.copysign(step, diff)

        # Перевірка чи досягнуто ціль
        arrived = all(
            abs(self.current_joints[i] - self.target_joints[i]) < self.arrival_threshold
            for i in range(len(self.current_joints))
        )

        if self.moving and arrived:
            self.moving = False
            self.waiting = True
            self.pause_start_time = now

        # Пауза після досягнення точки
        if self.waiting:
            if now - self.pause_start_time >= self.pause_duration:
                self.waiting = False
                self.execute_task()

        self.publish_scene()
        self.simulate_move(*self.current_joints)

    #функція для малювання сцени
    def publish_scene(self):
        msg = MarkerArray()  #створення об'єкта типу MarkerArray

        def create_cube(id, x, y, z, r, g, b):
            marker = Marker()  #створення об'єкта типу Marker
            marker.header.frame_id = "mg400_base_link"  #встановлення ідентифікатора кадру
            marker.header.stamp = self.get_clock().now().to_msg()  #встановлення часу

            marker.id = id  #встановлення ідентифікатора маркера
            marker.type = Marker.CUBE  #встановлення типу маркера як куб
            marker.action = Marker.ADD  #встановлення дії як додавання

            marker.pose.position.x = x  #встановлення позиції по осі x
            marker.pose.position.y = y  #встановлення позиції по осі y
            marker.pose.position.z = z  #встановлення позиції по осі z

            marker.pose.orientation.w = 1.0  #встановлення орієнтації (без повороту)

            marker.scale.x = 0.05  #встановлення масштабу по осі x
            marker.scale.y = 0.05  #встановлення масштабу по осі y
            marker.scale.z = 0.05  #встановлення масштабу по осі z

            marker.color.r = float(r)  #встановлення кольору червоного каналу
            marker.color.g = float(g)  #встановлення кольору зеленого каналу
            marker.color.b = float(b)  #встановлення кольору синього каналу
            marker.color.a = 1.0  #встановлення прозорості (1.0 - непрозорий)

            return marker
        
        #створення кубів з різними позиціями та кольорами
        msg.markers.append(create_cube(0, 0.3, 0.0, 0.025, 1, 0, 0)) # Червоний
        msg.markers.append(create_cube(1, 0.0, 0.25, 0.025, 0, 1, 0)) # Зелений
        msg.markers.append(create_cube(2, -0.25, -0.25, 0.025, 0, 0, 1)) # Синій 
        self.marker_pub.publish(msg)  #публікація масиву маркерів


    def simulate_move(self, *joints):
        msg = JointState()  #створення об'єкта типу JointState
        msg.header.stamp = self.get_clock().now().to_msg()  #встановлення часу
        msg.name = self.joint_names #встановлення імен суглобів
        msg.position = [float(j) for j in joints]  #встановлення позицій суглобів
        self.joint_pub.publish(msg)  #публікація повідомлення з позиціями суглобів

    def execute_task(self):
        if self.step == 0:
            self.target_joints = [0.0000, 1.2973, 1.2973, 0.1382, -1.2973, -1.4355, 1.4355, 0.0]
            self.get_logger().info("Moving to Point 1 (Red Cube)")
            self.step = 1
            self.moving = True

        elif self.step == 1:
            self.target_joints = [1.5508, 1.2935, 1.2935, 0.4416, -1.2935, -1.7350, 1.7350, 0.0]
            self.get_logger().info("Moving to Point 2 (Green Cube)")
            self.step = 2
            self.moving = True

        elif self.step == 2:
            self.target_joints = [-2.3457, 1.3683, 1.3683, -0.1824, -1.3683, -1.1860, 1.1860, 0.0]
            self.get_logger().info("Moving to Point 3 (Blue Cube)")
            self.step = 3
            self.moving = True

        elif self.step == 3:
            self.target_joints = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            self.get_logger().info("Returning home, restarting loop")
            self.step = 0
            self.moving = True

        
def main(args=None):
    #ініціалізація ROS 2
    rclpy.init(args=args)
    node = DobotTaskController()  #створення екземпляра класу DobotTaskController

    try:
        rclpy.spin(node)  #запуск циклу обробки повідомлень для вузла
    except KeyboardInterrupt:
        pass  #завершення роботи при отриманні сигналу переривання (Ctrl+C)

    node.destroy_node()  #знищення вузла
    rclpy.shutdown()  #завершення роботи ROS 2

if __name__ == '__main__':
    main()  #виклик функції main для запуску програми
