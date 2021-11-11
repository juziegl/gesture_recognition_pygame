import cv2
import mediapipe as mp
import numpy as np
import pygame
import random
from pygame.locals import *
import time
import math

StoneObjectList = list()

white = (255, 255, 255)
gamewindow_width = 720
gamewindow_height = 900

cursor_space_width = gamewindow_width - 5
cursor_space_height = gamewindow_height - 5

last_x_coo_cursor_saved = 5
last_y_coo_cursor_saved = 5

start_x_coo_cursor = 5
start_y_coo_cursor = 5

collusion_distance = 30


def loadify(imgname):
    return pygame.image.load(imgname).convert_alpha()


class Stone:
    def __init__(self, x_coo, y_coo, imagefile, velocity):
        self.shape = pygame.transform.scale(loadify(imagefile), (50, 35))
        self.velocity = velocity
        self.y_coo = y_coo
        self.x_coo = x_coo

    def Show(self, surface):
        self.y_coo += self.velocity
        surface.blit(self.shape, (self.x_coo, self.y_coo))


class Spaceship:
    def __init__(self, screenheight, screenwidth, imagefile):
        self.shape = pygame.transform.scale(loadify(imagefile), (50, 35))
        self.top = screenheight - self.shape.get_height()
        self.left = screenwidth - self.shape.get_width()

    def getwidth(self):
        return self.shape.get_width()

    def getheight(self):
        return self.shape.get_height()

    def Show(self, surface):
        surface.blit(self.shape, (self.left, self.top))

    def UpdateCoords(self, x, y):
        self.left = x
        self.top = y


def text_objects(text, font):
    textsurface = font.render(text, True, white)
    return textsurface, textsurface.get_rect()


def message_display(text):
    largeText = pygame.font.Font("freesansbold.ttf", 23)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = ((gamewindow_width / 2), (gamewindow_height / 2))
    screen.blit(TextSurf, TextRect)
    pygame.display.update()
    time.sleep(5)
    endgame = True
    # pygame.quit()


def checkforcrash(counter):
    message_display("You recieved {} points. R-estart or Q-uit?".format(counter))
    waitforkey()


def calculateDistance(x1, y1, x2, y2):
    dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist


def waitforkey():
    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_q:
                    pygame.quit()
                    cap.release()
                    cv2.waitKey()
                    cv2.destroyAllWindows()
                elif event.key == K_r:
                    main()


# initialize pygame and gesture
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((gamewindow_width, gamewindow_height))

bg = loadify("space.jpg")
bg = pygame.transform.scale(bg, (gamewindow_width, gamewindow_height))

pygame.mouse.set_visible(0)
pygame.display.set_caption('Space Dodge Game')

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture("video.mp4")

# initialize game objects
Spaceship = Spaceship(screenheight=cursor_space_height, screenwidth=cursor_space_width, imagefile="spaceship_red.png")

for _ in range(10):
    StoneAppend = Stone(x_coo=random.randint(0, gamewindow_width - 35), y_coo=-10, imagefile="rock.png",
                        velocity=random.randint(3, 4))
    StoneObjectList.append(StoneAppend)


def main():
    timecounter = 0
    gamepoints = 0

    for Stone in StoneObjectList:
        Stone.x_coo = random.randint(0, gamewindow_width - 35)
        Stone.y_coo = -10
        Stone.velocity = random.randint(3, 4)

    if not cap.isOpened():
        print("Error opening video stream")

    while cap.isOpened():
        timecounter += 1

        if timecounter % 20 == 0:
            gamepoints += 1
            # print(gamepoints)

        ret, img = cap.read()
        mask = np.zeros_like(img)

        if ret:
            # cv2.imshow("Video", img)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(imgRGB)

            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    id_coordinates_list = []
                    for id, lm in enumerate(handLms.landmark):
                        # print("id: {}\n lm: {} ".format(id, lm))
                        hight, width, color = img.shape
                        cx, cy = int(lm.x * width), int(lm.y * hight)
                        # print(" id: {}, cx: {}, cy: {}".format(id, cx, cy))
                        # print("-----------------------")

                        id_coordinates_list.append([id, cx, cy])

                        if id == 8:
                            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

                        mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

                cv2.circle(mask, (id_coordinates_list[8][1:]), 15, (255, 0, 255), cv2.FILLED)

            cv2.imshow("image", img)
            # cv2.imshow("position finger", mask)
        else:
            break

        if id_coordinates_list:
            x = id_coordinates_list[8][1]
            y = id_coordinates_list[8][2]

        for Stone in StoneObjectList:
            if Stone.y_coo <= gamewindow_height + 20:
                Stone.Show(screen)
            else:
                Stone.x_coo = random.randint(0, gamewindow_width - 35)
                Stone.y_coo = -10
                Stone.velocity = random.randint(1, 4)

        if (x <= cursor_space_width - Spaceship.getwidth()
                and y <= cursor_space_height - Spaceship.getheight()
                and x >= start_x_coo_cursor
                and y >= start_y_coo_cursor
        ):
            Spaceship.UpdateCoords(x, y)
            Spaceship.Show(screen)

            last_x_coo_cursor_saved, last_y_coo_cursor_saved = x, y

        else:
            Spaceship.UpdateCoords(last_x_coo_cursor_saved, last_y_coo_cursor_saved)
            Spaceship.Show(screen)

        for Stone in StoneObjectList:
            if calculateDistance(x, y, Stone.x_coo, Stone.y_coo) < collusion_distance:
                checkforcrash(gamepoints)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    cap.release()
                    cv2.waitKey()
                    cv2.destroyAllWindows()

        pygame.display.update()
        clock.tick(30)
        screen.blit(bg, (0, 0))


if __name__ == "__main__":
    main()
