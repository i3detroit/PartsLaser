import	servo
import	time

def	draw_box(location,h,v,size,delay):
	angle_x=location[0]
	angle_y=location[1]

	#mid-top
	v.servo_set_direct(angle_y+size/2)
	time.sleep(delay)
	h.servo_set_direct(angle_x+size/2)
	time.sleep(delay)
	v.servo_set_direct(angle_y-size/2)
	time.sleep(delay)
	h.servo_set_direct(angle_x-size/2)
	time.sleep(delay)
	v.servo_set_direct(angle_y+size/2)
	time.sleep(delay)
	h.servo_set_direct(angle_x)
	time.sleep(delay)
	v.servo_set_direct(angle_y)
