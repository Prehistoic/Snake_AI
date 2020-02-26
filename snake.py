import pygame
import neat
import time
import os
import random

pygame.font.init()

BOARD_WIDTH = 24
BOARD_HEIGHT = 12
CASE = 32
WIN_WIDTH = BOARD_WIDTH * CASE
WIN_HEIGHT = BOARD_HEIGHT * CASE

HEAD_IMG = pygame.image.load(os.path.join("imgs","head.png"))
TAIL_IMG = pygame.image.load(os.path.join("imgs","body.png"))
BODY_IMG = pygame.image.load(os.path.join("imgs","body.png"))
FRUIT_IMG = pygame.image.load(os.path.join("imgs","fruit.png"))
BG_IMG = pygame.image.load(os.path.join("imgs","bg.png"))

STAT_FONT = pygame.font.SysFont("comicsans", CASE)
LOST_FONT = pygame.font.SysFont("comicsans", CASE*2)

class Snake:
    def __init__(self,position):
        self.position = position
        self.direction = "RIGHT"

    def move(self):
        head = self.get_head()
        x = head[0]
        y = head[1]
        if self.direction == "RIGHT":
            self.position.append([x+CASE,y])
        elif self.direction == "LEFT":
            self.position.append([x-CASE,y])
        elif self.direction == "UP":
            self.position.append([x,y-CASE])
        elif self.direction == "DOWN":
            self.position.append([x,y+CASE])

    def get_smaller(self):
        self.position.pop(0)

    def collide(self):
        head = self.get_head()
        x = head[0]
        y = head[1]
        if x >= WIN_WIDTH or y >= WIN_HEIGHT:
            return True

        if x < 0 or y < 0:
            return True

        for i in range(len(self.position)-1):
            pos_x = self.position[i][0]
            pos_y = self.position[i][1]
            if x == pos_x and y == pos_y:
                return True

        return False

    def get_head(self):
        return self.position[len(self.position)-1]

    def draw(self,win):
        for i in range(len(self.position)):
            x = self.position[i][0]
            y = self.position[i][1]
            if i == len(self.position)-1:
                if self.direction == "RIGHT":
                    rotated_image = pygame.transform.rotate(HEAD_IMG,270)
                elif self.direction == "LEFT":
                    rotated_image = pygame.transform.rotate(HEAD_IMG,90)
                elif self.direction == "UP":
                    rotated_image = pygame.transform.rotate(HEAD_IMG,0)
                elif self.direction == "DOWN":
                    rotated_image = pygame.transform.rotate(HEAD_IMG,180)
                win.blit(rotated_image,(x,y))
            elif i == 0:
                win.blit(TAIL_IMG,(x,y))
            else:
                win.blit(BODY_IMG,(x,y))

class Fruit:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.IMG = FRUIT_IMG

    def eaten(self,head):
        head_x = head[0]
        head_y = head[1]
        if head_x == self.x and head_y == self.y:
            return True

        return False

    def draw(self,win):
        win.blit(self.IMG, (self.x, self.y))

def draw_window(win,snake,fruit,score,status):
    win.blit(BG_IMG,(0,0))
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    if status == False:
        text = LOST_FONT.render("YOU LOST !", 1, (255,255,255))
        win.blit(text, (WIN_WIDTH/2 - text.get_width()/2, WIN_HEIGHT/2))
    else:
        snake.draw(win)
    fruit.draw(win)
    pygame.display.update()

def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0
    snake = Snake([[0,0]])
    fruit = Fruit(CASE*random.randrange(0,BOARD_WIDTH-1),CASE*random.randrange(0,BOARD_HEIGHT-1))

    moving = True
    run = True
    while run:
        clock.tick(15)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key).upper()
                snake.direction = key

        draw_window(win,snake,fruit,score,moving)

        if moving :

            snake.move()

            if snake.collide():
                moving = False

            if fruit.eaten(snake.get_head()):
                fruit = Fruit(CASE*random.randrange(0,BOARD_WIDTH-1),CASE*random.randrange(0,BOARD_HEIGHT-1))
                score += 1
            else:
                snake.get_smaller()

if __name__=="__main__":
    main()
