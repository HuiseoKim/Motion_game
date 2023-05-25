import pygame
import numpy as np
import threading
import time, os, sys
import sys, math, wave
from pygame.locals import *
from scipy.fftpack import dct
from socket import *


w = 80*5
h = 128*5

N = 30 # num of bars
HEIGHT = 100 # height of a bar
WIDTH = 10 # width of a bar
FPS = 10

HOST = '10.32.93.212'
PORT = 20000
BUFSIZE = 1024
ADDR = (HOST, PORT)

clientSocket = socket(AF_INET, SOCK_STREAM)

try:
    clientSocket.connect(ADDR)
except Exception as e:
    print('서버(%s:%s)에 연결할 수 없습니다'%(ADDR))
    sys.exit()
print('서버(%s:%s)에 연결되었습니다'%(ADDR))

def sendData(d):
    clientSocket.send(bytes(d+'\n', 'utf-8'))
    getData = ''
    getData = clientSocket.recv(1024)
    return str(getData)[2:-1]
    
# process wave data

lastnote = -10

def datarecv():
    
    try:
        cmd='1'
        data = sendData(cmd)

    except KeyboardInterrupt:
        clientSocket.close()
        sys.exit()

    return data

def rungame(file_name):
    global gamepad, notes, score, sf, num, starttime, wave_data, nframes, framerate

    f = wave.open('musics/'+file_name, 'rb')
    params = f.getparams()
    framerate, nframes = params[2:4]
    str_data  = f.readframes(nframes)  
    f.close()
    
    num = nframes
    
    wave_data = np.frombuffer(str_data, dtype = np.short)
    wave_data.shape = -1,2
    wave_data = wave_data.T
    
    score=0
    
    crashed = False
    
    framenum = 1

    mstart = 0
    name = sf.render(file_name.replace('.wav','').replace('_',' '), True, (0,0,0))

    key = 0
    while not crashed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
            
        if time.time() - starttime >= 1.9 and mstart == 0:
            pygame.mixer.music.load('musics/'+file_name)
            pygame.mixer.music.play()
            pygame.mixer.music.set_endevent()
            mstart = 1

        while time.time()-starttime >= 0.1*framenum:
            vis()
            framenum += 1
            if num <= 0:
                crashed = True

        data = datarecv()
        key = int(data[0])
        pos = int(data[1])
        if key != 0:
            for i in range(len(notes)):
                if notes[i][2]>128*4 and notes[i][2]<64*9 and notes[i][3] == 0 and notes[i][1] == pos:

                    if key == notes[i][0]:
                        score += 1000
                        notes[i][3] = 1
                
        gamepad.fill((255,255,255))
        
        for i in range(len(notes)):
            if notes[i][3] == 1:
                notes[i][4] -= 1
                
            if notes[i][4] >= 1:
                a = notes[i][0]
                x = notes[i][1]
                y = notes[i][2]
                m = notes[i][3]
                if m == 0:
                    note = pygame.image.load('images/'+str(a)+'.png')
                if m == 1:
                    if notes[i][4] >= 8:
                        note = pygame.image.load('images/match.png')
                    else:
                        note = pygame.image.load('images/match2.png')
                if m == 2:
                    note = pygame.image.load('images/wrong.png')

                if notes[i][4] <8:
                    gamepad.blit(note,(x*120+20,y-10))
                else:
                    gamepad.blit(note,(x*120+10,y))

        text = sf.render("SCORE : "+str(score), True, (0,0,0))
        gamepad.blit(text, (10,10))
        gamepad.blit(name, (10,30))
        pygame.display.update()

    notes = []

def movenote(note,x,y,m,l):
    global notes
    
    notes[l][2]=y
    m = notes[l][3]
    thread = threading.Timer(0.1,movenote,args=[note,x,y+20,m,l])
    thread.start()
    if y >= 128*5:
        notes[l][4] = 0
        thread.cancel()
    if m == 1:
        notes[l][4] = 16
        thread.cancel()

def makenote():
    global gamepad, notes
    x = np.random.randint(3)
    a = np.random.randint(4)+1
    
    while len(notes) != 0 and notes[len(notes)-1][0] == a:
        a = np.random.randint(4)+1
    notes.append([a,x,0,0,1])
    movenote(a,x,0,0,len(notes)-1)

def vis():
    global num, lastnote, starttime, wave_data, nframes, framerate
    num -= framerate/FPS
    if num > 0:
        num = int(num)
        h = abs(dct(wave_data[0][nframes - num:nframes - num + N]))
        h = [min(HEIGHT,int(i **(1 / 2.5) * HEIGHT / 100)) for i in h]
        if h[15]>30 and h[14]>30 and time.time() - starttime - lastnote >= 0.5:
            makenote()
            lastnote = time.time() - starttime
  
def audiospectrum():
    global makespectrum, spframerate, spnframes, spwave_data, spnum
    spnum -= spframerate/FPS
    if spnum > 0:
        spnum = int(spnum)
        h = abs(dct(spwave_data[0][spnframes - spnum:spnframes - spnum + N]))
        h = [min(HEIGHT,int(i **(1 / 2.5) * HEIGHT / 100)) for i in h]
        draw_bars(h)
    thread = threading.Timer(0.1,audiospectrum)
    thread.start()
    if makespectrum == 0:
        thread.cancel()

def draw_bars(h):
    global gamepad
    bars = []
    for i in h:
        bars.append([len(bars) * WIDTH + 50,480 + HEIGHT-i,WIDTH - 1,i])
    pygame.draw.rect(gamepad,[255,255,255],[0,420,400,180],0)
    for i in bars:
        pygame.draw.rect(gamepad,[0,0,0],i,0)
    pygame.display.update()

def mainmenu():
    global gamepad, makespectrum, spframerate, spnframes, spwave_data, spnum, score
    main = pygame.image.load('images/main.png')
    gamepad.blit(main,(0,0))
    pygame.display.update()
    makespectrum = 1
    key1 = 0
    key2 = 0
    key = 0
    while key == 0:
        key = int(datarecv()[0])
    while key1 != 2 or key2 != 3 or key != 1:
        key1 = key2
        key2 = key
        while key == key2 or key == 0:
            key = int(datarecv()[0])

    music_list = os.listdir('musics')

    cursor = pygame.image.load('images/cursor.png')
    
    cur_y = 1
    first = 1
    key = 0
    while True:
        n = 0
        menu = pygame.image.load('images/menu.png')
        gamepad.blit(menu,(0,0))
        for i in music_list:
            n += 1
            text = sf.render(i.replace(".wav",""), True, (0,0,0))
            gamepad.blit(text, (20,n*20+30))

        prekey = key
        key = int(datarecv()[0])
        mstart = 1
        
        if key == 1 and cur_y > 1 and key != prekey:
            cur_y -= 1
            mstart = 1
            
        elif key == 4 and cur_y < len(music_list) and key != prekey:
            cur_y += 1
            mstart = 1

        elif key == 0 and key != prekey:
            mstart = 0
            makespectrum = 0
            rungame(music_list[cur_y-1])
            

        else:
            mstart = 0

        if mstart == 1 or first == 1:
            pygame.mixer.music.load('musics/'+music_list[cur_y-1])
            pygame.mixer.music.play()
            pygame.mixer.music.set_endevent()
            
            f = wave.open('musics/'+music_list[cur_y-1], 'rb')
            params = f.getparams()
            spframerate, spnframes = params[2:4]
            str_data  = f.readframes(spnframes)  
            f.close()  
            spwave_data = np.frombuffer(str_data, dtype = np.short)
            spwave_data.shape = -1,2
            spwave_data = spwave_data.T
            spnum = spnframes
            audiospectrum()
            first = 0
            
        if key != 3:
            gamepad.blit(cursor,(18,cur_y*20+30))
            makespectrum = 1

        pygame.display.update()
        

    pygame.quit()

def initgame():
    global gamepad, sf, starttime, notes

    notes = []

    pygame.init()

    starttime = time.time()

    sf = pygame.font.SysFont("Monospace", 20)
    
    gamepad = pygame.display.set_mode((w,h))
    pygame.display.set_caption('리듬게임')

    mainmenu()

initgame()
