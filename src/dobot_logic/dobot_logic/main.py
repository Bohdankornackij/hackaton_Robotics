import rclpy # type: ignore
from rclpy.node import Node # type: ignore
from visualization_msgs.msg import Marker, MarkerArray # type: ignore

class DobotTaskController(Node):
    def __init__(self):
        #ініціалзація вузла з ім'ям 'dobot_task_controller'
        super().__init__('dobot_task_controller')

        #створення публішера для відправки масиву маркерів на тему '/visualization_marker_array' з розміром черги 10
        self.marker_pub = self.create_publisher(MarkerArray, '/visualization_marker_array', 10)

        self.timer = self.create_timer(1.0, self.publish_scene)  #створення таймера для виклику функції publish_scene кожну секунду

        self.get_logger().info("Dobot Task Controller has been started.")

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
