ROS to-dos

each vehicle reqs:
	1. publish:
		* current operations
		* camera vision
		* sensor
	2. controls:
		* adjust camera
		* movements
	3. subscribe:
		* Override commands
		* sensors


Steps to building a project
1. mkdir  /catkin_ws/src
2. catkin_make
3. catkin_create_kg pkg_name dep0 dep1 dep2 ... depN
	eg catkin_create build079 roscpp rospy std_msg
4. source /devel/setup.bash #configures ros cmds and paths
5. roscd pkg
6. mkdir msg # msg folder contains .msg file to be built in ROS
7. mkdir srv   # contains .srv for defining service structures
8. mkdir scripts # contain the python 2.7 scripts
9. mkdir src # contains the cpp source codes
10. write code
11. sudo nano CMakeLists.txt # configure build dependencies
12. sudo nano package.xml # configure dep metadata
13. catkin_make #remake 
14. source /devel/setup.bash # update paths 


ROS structure
The primary components in ROS are "Nodes".
Nodes can be executed both locally and externally.
Nodes are used to encapsulate a purpose such as sensor reading or movement
A node communicates with another node via "topics" and "services"
A node can subscribe to a topic which allows it to receive updates
or it can publish a topic that other nodes can receive.
Picture this as a constructs for a graph
ROS requires that a master node is running that manages these nodes
