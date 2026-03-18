import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
import time

class DobotLogicNode(Node):
    def __init__(self):
        super().__init__('dobot_logic_node')
    
        self.publisher_ = self.create_publisher(Pose, 'mg400/target_pose', 10)
        
        self.targets = [
            {'x': 0.3, 'y': 0.0, 'z': 0.0, 'name': 'Червоний'},   # Куб 1 
            {'x': 0.0, 'y': 0.25, 'z': 0.0, 'name': 'Зелений'},  # Куб 2 
            {'x': 0.25, 'y': 0.25, 'z': 0.0, 'name': 'Синій'}    # Куб 3 
        ]
        self.current_target_idx = 0
        
        self.timer = self.create_timer(5.0, self.move_to_next_target)
        self.get_logger().info('Вузол dobot_logic успішно запущено. Починаємо рух...')

    def move_to_next_target(self):
        if self.current_target_idx < len(self.targets):
            target = self.targets[self.current_target_idx]
            
            msg = Pose()
            msg.position.x = target['x']
            msg.position.y = target['y']
            msg.position.z = target['z']
            
            msg.orientation.x = 0.0
            msg.orientation.y = 0.0
            msg.orientation.z = 0.0
            msg.orientation.w = 1.0 
            
            self.publisher_.publish(msg)
            self.get_logger().info(f'Рухаємось до куба {target["name"]}: x={target["x"]}, y={target["y"]}, z={target["z"]}')
            
            self.current_target_idx += 1
        else:
            self.get_logger().info('Всі куби успішно пройдено! Місія виконана.')
            self.timer.cancel()

def main(args=None):
    rclpy.init(args=args)
    node = DobotLogicNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Зупинено користувачем (Ctrl+C)')
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()