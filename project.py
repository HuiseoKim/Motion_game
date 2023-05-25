import pygame
import numpy as np
import threading
import time, os
import sys, math, wave
from pygame.locals import *
from scipy.fftpack import dct

w = 80*5
h = 128*5

N = 30 # num of bars
HEIGHT = 100 # height of a bar
WIDTH = 10 # width of a bar
FPS = 10

# process wave data

lastnote = -10

def keymaker():
    key = np.random.randint(4)+1
    return key

def position():
    pos = np.random.randint(3)+1
    return pos


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

        prekey = key
        key = keymaker()
        pos = position()
        if prekey == 0 and key != 0:
            chk = 0
            
            for i in range(len(notes)):
                if notes[i][2]>128*4 and notes[i][2]<64*9 and notes[i][3] == 0 and notes[i][1] == pos:
                    chk = 1
                    if key == notes[i][0]:
                        score += 1000
                        notes[i][3] = 1
                        
                    else:
                        score -= 5
                        notes[i][3] = 2
                        
            if chk == 0:
                score -= 5
                
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
    a = np.random.randint(9)+1
    notes.append([a,x,0,0,1])
    movenote(a,x,0,0,len(notes)-1)

def vis():
    global num, lastnote, starttime, wave_data, nframes, framerate
    num -= framerate/FPS
    if num > 0:
        num = int(num)
        h = abs(dct(wave_data[0][nframes - num:nframes - num + N]))
        h = [min(HEIGHT,int(i **(1 / 2.5) * HEIGHT / 100)) for i in h]
        if h[15]>30 and h[14]>30 and time.time() - starttime - lastnote >= 0.2:
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
    key3 = 0
    key4 = 0  
    key = keymaker()
    '''
    while key1 != 3 or key2 != 0 or key3 != 7 or key4 != 0 or key != 8:
        key1 = key2
        key2 = key3
        key3 = key4
        key4 = key
        while key != key4:
            key = keymaker()
    '''

    music_list = os.listdir('musics')

    cursor = pygame.image.load('images/cursor.png')
    
    cur_y = 1
    first = 1
    
    while True:
        n = 0
        menu = pygame.image.load('images/menu.png')
        gamepad.blit(menu,(0,0))
        for i in music_list:
            n += 1
            text = sf.render(i.replace(".wav",""), True, (0,0,0))
            gamepad.blit(text, (20,n*20+30))

        key = keymaker()
        mstart = 1
        
        if key == 1 and cur_y > 1:
            cur_y -= 1
            mstart = 1
            
        elif key == 2 and cur_y < len(music_list):
            cur_y += 1
            mstart = 1

        elif key == 3:
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
