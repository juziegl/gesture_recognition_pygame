'''checkout requirements textfile for same versions'''

import pygame
import sys
import cv2
import mediapipe as mp
import random

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
COUNTER_PLAYGROUND = 0
WINDOW_HEIGHT = 480
WINDOW_WIDTH = 640
GAME_END = False
GAMEPOINTS = 0

#my webcam size
HEIGHT = 480
WIDTH = 640

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

def calculateCoo(XPose, YPose, height, width):
    '''calculate coordinates based on your webcam format'''
    XCoo, YCoo = int(XPose * width), int(YPose * height)
    return XCoo, YCoo

def initialize():
    '''initialize pygame playground '''
    global SCREEN, CLOCK
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()
    SCREEN.fill(BLACK)
    drawGrid()

def drawGrid():
    '''draw pygame format'''
    blockSize = 32 #Set the size of the grid block
    for x in range(0, WINDOW_WIDTH, blockSize):
        for y in range(0, WINDOW_HEIGHT, blockSize):
            rect = pygame.Rect(x, y, blockSize, blockSize)
            pygame.draw.rect(SCREEN, WHITE, rect, 1)

def drawPlayground():
    '''create random hitmarker'''
    randomX = random.randint(0,18)
    randomY = random.randint(0,13)

    pygame.draw.rect(SCREEN, RED, pygame.Rect( (randomX*32)+1, (randomY*32)+1, 30, 30))
    pygame.draw.rect(SCREEN, RED, pygame.Rect(( (randomX+1)*32)+1, (randomY*32)+1, 30, 30))
    pygame.draw.rect(SCREEN, RED, pygame.Rect( (randomX*32)+1, ((randomY+1)*32)+1, 30, 30))
    pygame.draw.rect(SCREEN, RED, pygame.Rect(( (randomX+1)*32)+1, ((randomY+1)*32)+1, 30, 30))

    #ausgabe für collisiondetector
    return randomX, randomY

def resetPlayground(randomX, randomY):
    '''reset random hitmarker'''
    pygame.draw.rect(SCREEN, BLACK, pygame.Rect( (randomX*32)+1, (randomY*32)+1, 30, 30))
    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(( (randomX+1)*32)+1, (randomY*32)+1, 30, 30))
    pygame.draw.rect(SCREEN, BLACK, pygame.Rect( (randomX*32)+1, ((randomY+1)*32)+1, 30, 30))
    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(( (randomX+1)*32)+1, ((randomY+1)*32)+1, 30, 30))

    
if __name__ == "__main__":

    initialize()

    start_ticks = pygame.time.get_ticks()
    saverandomX, saverandomY = drawPlayground()

    rect = pygame.Rect(1, 1, 30, 30)
    pygame.draw.rect(SCREEN, BLACK , pygame.Rect(1, 1, 30, 30))

    oldXCoo = 0
    oldYCoo = 0

    cap = cv2.VideoCapture(0)

    with mp_pose.Pose(

        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:

        while cap.isOpened():
            
            success, image = cap.read()
            image = cv2.flip(image, 1)

            #mask = np.zeros_like(image)

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try: 
                landmarks = results.pose_landmarks.landmark

                '''attention! because of image flip right and left is flipped as well'''
                #right_shoulder_x, right_shoulder_y = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x , landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
                #left_shoulder_x, left_shoulder_y = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x , landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y
                nose_x, nose_y = landmarks[mp_pose.PoseLandmark.NOSE.value].x, landmarks[mp_pose.PoseLandmark.NOSE.value].y

                #RXcoo, RYcoo = calculateCoo(right_shoulder_x, right_shoulder_y, height, width)
                #LXcoo, LYcoo = calculateCoo(left_shoulder_x, left_shoulder_y, height, width)
                NXcoo, NYcoo = calculateCoo(nose_x, nose_y, HEIGHT, WIDTH)

                #cv2.putText(image, str(RXcoo), (RXcoo, RYcoo), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA)
                #cv2.putText(image, str(LXcoo), (LXcoo, LYcoo), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA)
                #cv2.putText(image, str(NXcoo), (NXcoo, NYcoo), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA)
                cv2.putText(image, str("HITS: ") + str(COUNTER_PLAYGROUND), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA)
                cv2.putText(image, str("TIME: ") + str(GAMEPOINTS), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA)
                
                #cv2.circle(mask, (RXcoo, RYcoo), 15, (255, 0, 255), cv2.FILLED)
                #cv2.circle(mask, (LXcoo, LYcoo), 15, (0, 0, 255), cv2.FILLED)

                RedMinX = (saverandomX*32)+1
                RedMinY = (saverandomY*32)+1
                RedMaxX = ((saverandomX+1)*32)+31
                RedMaxY = ((saverandomY+1)*32)+31

                if (NXcoo >= RedMinX) & (NXcoo <= RedMaxX) & (NYcoo >= RedMinY) & (NYcoo <= RedMaxY):
                    COUNTER_PLAYGROUND += 1
                    resetPlayground(saverandomX, saverandomY)
                    saverandomX, saverandomY = drawPlayground()

                if (COUNTER_PLAYGROUND == 1):
                    start_ticks = pygame.time.get_ticks()

                if (COUNTER_PLAYGROUND == 5) & (GAME_END == False):
                    seconds = (pygame.time.get_ticks()-start_ticks)/1000
                    GAMEPOINTS = round(seconds, 3)
                    GAME_END = True
                    #break

                newNXcoo = int(NXcoo/32)*32
                newNYcoo = int(NYcoo/32)*32
                
                pygame.draw.rect(SCREEN, BLACK , pygame.Rect(oldXCoo+1, oldYCoo+1, 30, 30))
                pygame.draw.rect(SCREEN, WHITE, pygame.Rect(newNXcoo+1, newNYcoo+1, 30, 30))
                pygame.display.update()

                oldXCoo = newNXcoo
                oldYCoo = newNYcoo

            except:
                pass

            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            
            # Flip the image horizontally for a selfie-view display.
            cv2.imshow('MediaPipe Pose', image)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            '''press q to shut software'''
            if cv2.waitKey(5) & 0xFF == ord('q'):
                cap.release()
                cv2.waitKey()
                cv2.destroyAllWindows()
                pygame.quit()
                sys.exit()
