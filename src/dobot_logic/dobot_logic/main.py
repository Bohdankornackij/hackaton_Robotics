import rclpy
import math 
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class DobotTaskController(Node):
    def __init__(self):
        super().__init__('dobot_task_controller')
        self.traj_pub = self.create_publisher(JointTrajectory, '/mg400_arm_controller/joint_trajectory', 10)
        self.timer = self.create_timer(0.1, self.update_logic)
        self.step = 0
        self.current_joints = [0.0] * 5
        self.target_joints = [0.0] * 5
        self.joint_names = ['mg400_j1', 'mg400_j2_1', 'mg400_j3_1', 'mg400_j4_1', 'mg400_j5']
        self.lerp_speed = 0.3
        self.waiting = False
        self.pause_duration = 3.0
        self._last_time = None
        self.execute_task()

    def update_logic(self):
        now = self.get_clock().now().nanoseconds / 1e9
        if self._last_time is None: self._last_time = now
        dt = min(now - self._last_time, 0.2)
        self._last_time = now
        arrived = True
        for i in range(len(self.current_joints)):
            diff = self.target_joints[i] - self.current_joints[i]
            step = self.lerp_speed * dt
            if abs(diff) > step:
                self.current_joints[i] += math.copysign(step, diff)
                arrived = False
            else:
                self.current_joints[i] = self.target_joints[i]
        self.send_trajectory(self.current_joints)
        if arrived and not self.waiting:
            self.waiting = True
            self.pause_start_time = now
        if self.waiting and (now - self.pause_start_time >= self.pause_duration):
            self.waiting = False
            self.execute_task()

    def send_trajectory(self, joints):
        msg = JointTrajectory()
        msg.header.stamp.sec = 0
        msg.header.stamp.nanosec = 0
        msg.joint_names = self.joint_names
        point = JointTrajectoryPoint()
        point.positions = [float(j) for j in joints]
        point.time_from_start.nanosec = 500000000
        msg.points.append(point)
        self.traj_pub.publish(msg)

    def execute_task(self):
        points = [
            [0.0,     1.2973,  0.1382,  -1.4355, 0.0],  # Червоний
            [1.5508,  1.2935,  0.4416,  -1.7350, 0.0],  # Зелений
            [-2.3457, 1.3683, -0.1824,  -1.1860, 0.0],  # Синій
            [0.0,     0.0,     0.0,      0.0,    0.0],  # Додому
        ]
        self.target_joints = points[self.step]
        self.get_logger().info(f"Moving to step {self.step}")
        self.step = (self.step + 1) % len(points)
        

def main(args=None):
    rclpy.init(args=args)
    node = DobotTaskController()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally:
        node.destroy_node()
        if rclpy.ok(): rclpy.shutdown()

if __name__ == '__main__': main()