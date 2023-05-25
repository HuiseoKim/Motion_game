from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from socket import *
from threading import Thread

from pykinect2 import PyKinectRuntime
from socket import *

import time

import ctypes
import _ctypes
import pygame
import sys
from math import sqrt
import serial

prev_s=0
state=0
angle_rstate=0
angle_lstate=0
body_state=0
score=0
name="\\"
songname="WW_WWW"
if sys.hexversion >= 0x03000000:
    import _thread as thread
else:
    import thread

SKELETON_COLORS = [pygame.color.THECOLORS["red"], 
                  pygame.color.THECOLORS["blue"], 
                  pygame.color.THECOLORS["green"], 
                  pygame.color.THECOLORS["orange"], 
                  pygame.color.THECOLORS["purple"], 
                  pygame.color.THECOLORS["yellow"], 
                  pygame.color.THECOLORS["violet"]]

class BodyGameRuntime(object):
    def __init__(self):
        pygame.init()
        self._clock = pygame.time.Clock()
        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._infoObject.current_w >> 1, self._infoObject.current_h >> 1), 
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)

        pygame.display.set_caption("Kinect for Windows v2 Body Game")
        self._done = False
        self._clock = pygame.time.Clock()
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)
        self._bodies = None


    def draw_body_bone(self, joints, jointPoints, color, joint0, joint1):
        joint0State = joints[joint0].TrackingState;
        joint1State = joints[joint1].TrackingState;
        if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint1State == PyKinectV2.TrackingState_NotTracked): 
            return
        if (joint0State == PyKinectV2.TrackingState_Inferred) and (joint1State == PyKinectV2.TrackingState_Inferred):
            return 
        start = (jointPoints[joint0].x, jointPoints[joint0].y)
        end = (jointPoints[joint1].x, jointPoints[joint1].y)

        try:
            pygame.draw.line(self._frame_surface, color, start, end, 8)
        except:
            pass

    def draw_body(self, joints, jointPoints, color):
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft);
    
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_HandRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandRight, PyKinectV2.JointType_HandTipRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_ThumbRight);

        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_HandLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandLeft, PyKinectV2.JointType_HandTipLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_ThumbLeft);

        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleRight, PyKinectV2.JointType_FootRight);

        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleLeft, PyKinectV2.JointType_FootLeft);

    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()

    def printjoint(self, jointPoints):
        global state
        global body_state
        wr=PyKinectV2.JointType_WristRight
        wl=PyKinectV2.JointType_WristLeft
        er=PyKinectV2.JointType_ElbowRight
        el=PyKinectV2.JointType_ElbowLeft
        sr=PyKinectV2.JointType_ShoulderRight
        sl=PyKinectV2.JointType_ShoulderLeft
        
        spinebase=PyKinectV2.JointType_SpineBase
        
        wer=sqrt((jointPoints[wr].y-jointPoints[er].y)*(jointPoints[wr].y-jointPoints[er].y)+(jointPoints[wr].x-jointPoints[er].x)*(jointPoints[wr].x-jointPoints[er].x))
        wsr=sqrt((jointPoints[wr].y-jointPoints[sr].y)*(jointPoints[wr].y-jointPoints[sr].y)+(jointPoints[wr].x-jointPoints[sr].x)*(jointPoints[wr].x-jointPoints[sr].x))
        ser=sqrt((jointPoints[sr].y-jointPoints[er].y)*(jointPoints[sr].y-jointPoints[er].y)+(jointPoints[sr].x-jointPoints[er].x)*(jointPoints[sr].x-jointPoints[er].x))

        wel=sqrt((jointPoints[wl].y-jointPoints[el].y)*(jointPoints[wl].y-jointPoints[el].y)+(jointPoints[wl].x-jointPoints[el].x)*(jointPoints[wl].x-jointPoints[el].x))
        wsl=sqrt((jointPoints[wl].y-jointPoints[sl].y)*(jointPoints[wl].y-jointPoints[sl].y)+(jointPoints[wl].x-jointPoints[sl].x)*(jointPoints[wl].x-jointPoints[sl].x))
        sel=sqrt((jointPoints[sl].y-jointPoints[el].y)*(jointPoints[sl].y-jointPoints[el].y)+(jointPoints[sl].x-jointPoints[el].x)*(jointPoints[sl].x-jointPoints[el].x))

        cosrthetha=(ser*ser+wer*wer-wsr*wsr)/(2*ser*wer)
        coslthetha=(sel*sel+wel*wel-wsl*wsl)/(2*sel*wel)
        
        if cosrthetha<-0.9:
            angle_rstate=1
        else:
            angle_rstate=0
        
        if coslthetha<-0.9:
            angle_lstate=1
        else:
            angle_lstate=0
        
        if jointPoints[spinebase].x<800:
            body_state=0
        elif jointPoints[spinebase].x<1200:
            body_state=1
        else:
            body_state=2
        
        if jointPoints[wr].y > jointPoints[er].y:
            rightup=0
        else:
            rightup=1
            
        if jointPoints[wl].y > jointPoints[el].y:
            leftup=0
        else:
            leftup=1
        
        if rightup==1 and leftup==1 and angle_rstate==0 and angle_lstate==0:
            state=1
        elif rightup==0 and leftup==1 and angle_rstate==0 and angle_lstate==0:
            state=2
        elif rightup==1 and leftup==0 and angle_rstate==0 and angle_lstate==0:
            state=3
        elif rightup==0 and leftup==0 and angle_rstate==0 and angle_lstate==0:
            state=4
        else:
            state=0
            
        

        
    def run(self):
        # -------- Main Program Loop -----------
        while not self._done:
            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self._done = True # Flag that we are done so we exit this loop

                elif event.type == pygame.VIDEORESIZE: # window resized
                    self._screen = pygame.display.set_mode(event.dict['size'], 
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)
                    
            # --- Game logic should go here

            # --- Getting frames and drawing  
            # --- Woohoo! We've got a color frame! Let's fill out back buffer surface with frame's data 
            if self._kinect.has_new_color_frame():
                frame = self._kinect.get_last_color_frame()
                self.draw_color_frame(frame, self._frame_surface)
                frame = None

            # --- Cool! We have a body frame, so can get skeletons
            if self._kinect.has_new_body_frame(): 
                self._bodies = self._kinect.get_last_body_frame()

            # --- draw skeletons to _frame_surface
            if self._bodies is not None: 
                for i in range(0, self._kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    if not body.is_tracked: 
                        continue 
                    
                    joints = body.joints 
                    # convert joint coordinates to color space 
                    joint_points = self._kinect.body_joints_to_color_space(joints)
                    self.draw_body(joints, joint_points, SKELETON_COLORS[i])
                    self.printjoint(joint_points)

            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            pygame.display.update()

            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()
            
            # --- Limit to 60 frames per second
            self._clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        
        self._kinect.close()
        pygame.quit()


__main__ = "Kinect v2 Body Game"

def subfunc():
    global state
    global body_state
    #HOST='172.30.102.7'
    #HOST = '127.0.0.1'
    HOST = '192.168.0.102'
    PORT=20000
    BUFSIZE=1024
    ADDR=(HOST,PORT)
     
    serverSocket=socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(ADDR)
    serverSocket.listen(0)
     
    while True:
        print(state,body_state)
        print("[-] Listening...")
        try:
            conn,addr=serverSocket.accept()
        except Exception as e:
            print('(%s:%s)Not Connected.'%ADDR)
            sys.exit()
        print('(%s:%s) Now Connected.'%(conn,addr))
        while True:
            cmd=conn.recv(1024)     #b'1\n'
            c=str(cmd)[2]   #b'1\n'에서 1만 슬라이싱
            print(c)
            if c=='1':
                msg=str(state)+str(body_state)
                conn.send(bytes(str(msg),'UTF-8'))
    conn.close()
    serverSocket.close()
    print('close')
    
def mainfunc():
    game = BodyGameRuntime()
    game.run()
    
process2 = Thread(target=subfunc)
process2.start()
mainfunc()
process2.join()
