import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class GazeboBridge(Node):
    def __init__(self):
        super().__init__('gazebo_bridge')
        self.pub = self.create_publisher(JointTrajectory, '/set_joint_trajectory', 10)
        self.sub = self.create_subscription(JointState, '/joint_states', self.callback, 10)
        self.get_logger().info('!!! TRAJECTORY BRIDGE STARTED !!!')

    def callback(self, msg):
        traj = JointTrajectory()
        traj.header.frame_id = 'world'
        traj.header.stamp = self.get_clock().now().to_msg()
        traj.joint_names = list(msg.name)
        point = JointTrajectoryPoint()
        point.positions = [float(p) for p in msg.position]
        point.time_from_start.sec = 0
        point.time_from_start.nanosec = 0
        traj.points.append(point)
        self.pub.publish(traj)

def main():
    rclpy.init()
    node = GazeboBridge()
    rclpy.spin(node)
    rclpy.shutdown()