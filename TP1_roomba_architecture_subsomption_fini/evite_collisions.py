#!/usr/bin/env python

import rospy
from subsomption.msg import Channel 
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
import numpy as np

import random

bumper_l=0
bumper_r=0
lasers=LaserScan()
speed=2
threshold=50
timer=10



def callback_right_bumper(data):
    global bumper_r
    bumper_r=data.data
    #rospy.loginfo(rospy.get_caller_id()+"Right bumper %d",data.data)

def callback_left_bumper(data):
    global bumper_l
    bumper_l=data.data
    #rospy.loginfo(rospy.get_caller_id()+"Left bumper %d",data.data)


def callback_lasers(data):
    global lasers
    lasers=data
    #rospy.loginfo(rospy.get_caller_id()+" Lasers %s"," ".join(map(str,lasers)))


# replace 'my_behavior' by the name of your behavior
def evite_collision():
    rospy.init_node('my_behavior', anonymous=True)

    # remove the subscriptions you don't need.
    rospy.Subscriber("/simu_fastsim/laser_scan", LaserScan, callback_lasers)
    #rospy.Subscriber("/simu_fastsim/right_bumper", Bool, callback_right_bumper)
    #rospy.Subscriber("/simu_fastsim/left_bumper", Bool, callback_left_bumper)
 
    # replace /subsomption/channel0 by /subsomption/channeli where i is the number of the channel you want to publish in
    pub = rospy.Publisher('/subsomption/channel1', Channel , queue_size=10)
    r = rospy.Rate(10) # 10hz
    v=Channel()
    v.activated=False
    v.speed_left=-1
    v.speed_right=-1
    count=0
    timer_bumper=0 #added
    flag_right = False
    flag_left = False
    while not rospy.is_shutdown():
        # compute the value of v that will be sent to the subsomption channel. 
	ranges = np.array(lasers.ranges)
	minrange = +1000
	if ranges.size > 0:
		minrange = np.amin(ranges)
		#print(minrange , np.argmin(ranges), "/", ranges.size)

		if minrange < 50:
    			v.activated=True
			print(">>>", minrange)
			speed = 0.5
			if np.argmin(ranges) < (ranges.size//2) and not flag_left: #mur left
				v.speed_left=-speed
		    		v.speed_right=+speed
				flag_right = True
				flag_left = False
			elif not flag_right: #mur right
				v.speed_left=+speed
	    			v.speed_right=-speed
				flag_left = True
				flag_right = False
		else:
			v.activated=False
			flag_right = False
			flag_left = False
	else:
		v.activated=False
		flag_right = False
		flag_left = False

	

	"""
	if flag_bumper and timer_bumper<10:
		v.speed_left=-1
    		v.speed_right=-1
    		v.activated=True
		timer_bumper += 1
        elif flag_bumper and timer_bumper<15: #a ajuster
		v.speed_left=+1
    		v.speed_right=-1
    		v.activated=True
		timer_bumper += 1
	elif flag_bumper:
		v.activated=False
		timer_bumper = 0
		flag_lasers= False
	"""
		
	#publish v
        pub.publish(v)
        r.sleep()   
    


if __name__ == '__main__':
    random.seed()
    try:
        evite_collision()
    except rospy.ROSInterruptException: pass
