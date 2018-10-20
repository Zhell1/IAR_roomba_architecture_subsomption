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
def suivi_murs():
    rospy.init_node('my_behavior', anonymous=True)

    # remove the subscriptions you don't need.
    rospy.Subscriber("/simu_fastsim/laser_scan", LaserScan, callback_lasers)
    #rospy.Subscriber("/simu_fastsim/right_bumper", Bool, callback_right_bumper)
    #rospy.Subscriber("/simu_fastsim/left_bumper", Bool, callback_left_bumper)
 
    # replace /subsomption/channel0 by /subsomption/channeli where i is the number of the channel you want to publish in
    pub = rospy.Publisher('/subsomption/channel2', Channel , queue_size=10)
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
		
		exteriorlasersleft = ranges[0:int(ranges.size*0.3)]
		exteriorlasersright = ranges[int(ranges.size*0.7):ranges.size*1]

		"""
		seuilmur = 0.5
		validmurgauche = ranges[0] - ranges[2] > seuilmur
		validmurdroite = ranges[ranges.size-1] - ranges[ranges.size-3]  > seuilmur
"""

		minexteriorlaserleft = np.amin(exteriorlasersleft)
		minexteriorlaserright = np.amin(exteriorlasersright)

		centerlasers = ranges[int(ranges.size*0.3):int(ranges.size*0.7)] #20% central
		mincenterlaser = np.amin(centerlasers)
		#print(minrange , np.argmin(ranges), "/", ranges.size)

		seuilcentre = 50
		seuilcote = 40
		seuilmax = 100 #pour se rapprocher du mur si on s'en eloigne sans avoir d'obstacle
		speed = 0.2
		print(minexteriorlaserleft, mincenterlaser, minexteriorlaserright)
		#print(validmurgauche, validmurdroite)


		if mincenterlaser < seuilcentre or minexteriorlaserleft < seuilcote or minexteriorlaserright < seuilcote: # or not (validmurgauche or validmurdroite): #mur trop proche = desactive ce comportement
			print("DESACTIVE")
			v.activated=False
			flag_left = False
			flag_right = False			
		elif minexteriorlaserleft < seuilmax and not flag_right : #suit mur a gauche
			print("SUIVI DE MUR GAUCHE")
			v.speed_left=+1
    			v.speed_right=+1
			flag_left = True
			flag_right = False
			v.activated=True
		elif flag_left and minexteriorlaserleft > seuilmax : #s'eloigne trop
			print("RAPPROCHE MUR GAUCHE")
			#tourne a gauche un peu
			v.speed_left=+speed
    			v.speed_right=-speed
		elif minexteriorlaserright < seuilmax and not flag_left: #suit mur a droite 
			print("SUIVI DE MUR DROIT")
			v.speed_left=+1
    			v.speed_right=+1
			flag_right = True
			flag_left = False
			v.activated=True
		elif flag_right and minexteriorlaserright > seuilmax : #s'eloigne trop
			print("RAPPROCHE MUR DROIT")
			#tourne a droite un peu
			v.speed_left=-speed
    			v.speed_right=+speed
		else:
			print("ERROR")
			v.activated=False
			flag_right = False
			flag_left = False
	else:
		print("RANGES SIZE == 0")
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
        suivi_murs()
    except rospy.ROSInterruptException: pass
