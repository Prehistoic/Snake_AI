import pygame
import neat
import time
import os
import random
import math

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
        self.time_since_eat = 0

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

    def distance_to_fruit(self,x,y):
        head = self.get_head()
        head_x = head[0]
        head_y = head[1]
        return math.sqrt(math.pow(abs(x-head_x),2)+math.pow(abs(y-head_y),2))

    def distance_to_danger(self,direction):
        head = self.get_head()
        head_x = head[0]
        head_y = head[1]
        distance = 10000
        if direction == "RIGHT" or direction == "LEFT":
            distance = abs(WIN_WIDTH-head_x)
        elif direction == "UP" or direction == "DOWN":
            distance = abs(WIN_HEIGHT-head_y)
        if len(self.position) == 1:
            return distance
        for i in range(0,len(self.position)-2):
            x = self.position[i][0]
            y = self.position[i][1]
            if direction == "RIGHT" and y == head_y and x > head_x:
                distance_i = abs(x-head_x)
                if distance_i < distance:
                    distance = distance_i
            elif direction == "LEFT" and y == head_y and x < head_x:
                distance_i = abs(x-head_x)
                if distance_i < distance:
                    distance = distance_i
            elif direction == "UP" and x == head_x and y < head_y:
                distance_i = abs(y-head_y)
                if distance_i < distance:
                    distance = distance_i
            elif direction == "DOWN" and x == head_x and y > head_y:
                distance_i = abs(y-head_y)
                if distance_i < distance:
                    distance = distance_i
        return distance

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

def draw_window(win,snake,fruit,score):
    win.blit(BG_IMG,(0,0))
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    snake.draw(win)
    fruit.draw(win)
    pygame.display.update()

def main(genomes, config):
    nets=[]
    ge=[]
    snakes=[]

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        snakes.append(Snake([[0,0]]))
        g.fitness = 0
        ge.append(g)

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0
    fruit = Fruit(CASE*random.randrange(0,BOARD_WIDTH-1),CASE*random.randrange(0,BOARD_HEIGHT-1))

    snake_id = 0
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        if len(snakes)-1 == snake_id:
            run = False
            break

        snake = snakes[snake_id]

        draw_window(win,snake,fruit,ge[snake_id].fitness)
        
        distance_before_moving = snake.distance_to_fruit(fruit.x,fruit.y)
        snake.move()
        distance_after_moving = snake.distance_to_fruit(fruit.x,fruit.y)
        if(distance_after_moving < distance_before_moving):
            ge[snake_id].fitness += 1
        else:
            ge[snake_id].fitness -= 1

        inputs = (
            (snake.get_head()[0]-fruit.x), 
            (snake.get_head()[1]-fruit.y), 
            (snake.distance_to_danger(snake.direction))
        )
        outputs = nets[snake_id].activate(inputs)
        
        previous_direction = snake.direction
        if outputs[0] > 0.5 and previous_direction != "LEFT":
            snake.direction = "RIGHT"
        if outputs[1] > 0.5 and previous_direction != "RIGHT":
            snake.direction = "LEFT"
        if outputs[2] > 0.5 and previous_direction != "DOWN":
            snake.direction = "UP"
        if outputs[3] > 0.5 and previous_direction != "UP":
            snake.direction = "DOWN"

        if fruit.eaten(snake.get_head()):
            fruit = Fruit(CASE*random.randrange(0,BOARD_WIDTH-1),CASE*random.randrange(0,BOARD_HEIGHT-1))
            score += 1
            ge[snake_id].fitness += 100 - snake.time_since_eat
            snake.time_since_eat = 0
        else:
            snake.get_smaller()
            snake.time_since_eat += 1

        if snake.collide() or snake.time_since_eat > 100:
            ge[snake_id].fitness -= 10
            snake_id += 1
            score = 0

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                config_path)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neat-config.txt")
    run(config_path)
