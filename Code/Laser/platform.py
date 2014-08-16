import servo

def draw_box(h,v,size,delay):
        angle_x=h.get_angle()
        angle_y=v.get_angle()

        #mid-top
        v.set_angle(angle_y+size/2)
        time.sleep(delay)
        h.set_angle(angle_x+size/2)
        time.sleep(delay)
        v.set_angle(angle_y-size/2)
        time.sleep(delay)
        h.set_angle(angle_x-size/2)
        time.sleep(delay)
        v.set_angle(angle_y+size/2)
        time.sleep(delay)
        h.set_angle(angle_x)
        time.sleep(delay)
        v.set_angle(angle_y)
