import pygame
import sys, random
import math

pygame.init()

size = width, height = 640, 480

speed = [1, 1]
black = 0, 0, 0
white = 255, 255, 255
red = 255, 0, 0

screen = pygame.display.set_mode(size)

old_ticks = ticks = pygame.time.get_ticks()

ball_size = 10
num_balls = 200
speed = .1

transmission_rate = 0.2

sick_rate = 0.001

death_rate = 0.01
hospital_rate = 0.1

game_theory_threshold = 0.01
game_theory_rate = 0.02

govt_threshold = 0.10
govt_rate = 0.95

GAME_THEORY = 1
NORMAL = 2
RECKLESS = 3
#  x, y, dx, dy, sick, type, hiding, dead, immune
# 200, 300, 0.1, NORMAL, False, False

# set up population
balls = [[width/2, height/2, speed, 0, 0.1, NORMAL, False, False, False]]
PI = 3.1415
for i in range(0, num_balls):
    x = random.randint(0, width)
    y = random.randint(0, height)
    angle = 2*PI*random.random()
    dx = speed*math.sin(angle)
    dy = speed*math.cos(angle)

    roll = random.random()
    ball_type = RECKLESS
    if roll < game_theory_rate:
        ball_type = GAME_THEORY
    elif roll < govt_rate:
        ball_type = NORMAL

    ball = [x, y, dx, dy, 0.0, ball_type, False, False, False]
    balls.append(ball)


sick = 1
hiding = 0
dead = 0

#collision optimization stuff
collision_group_size = 10

while sick > 0:
    print("Sick",sick,"Hiding",hiding,"Dead",dead,"")
    ticks = pygame.time.get_ticks()
    delta = ticks - old_ticks
    old_ticks = ticks

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    for i in range(0, len(balls)):
        balls[i][0] += balls[i][2]*delta
        balls[i][1] += balls[i][3]*delta

        # sickness could resolve
        if balls[i][4] > 0:
            balls[i][4] += sick_rate
            if balls[i][4] >= 1.0:
                # Die or get better in hospital
                sick -= 1
                if random.random() < death_rate:
                    balls[i][7] = True
                    dead += 1
                else:
                    balls[i][8] = True
                    balls[i][4] = 0.0

        if balls[i][6] or balls[i][7]:
            continue

        # hide inside
        if balls[i][5] == GAME_THEORY:
            # These balls don't defect and hide immediately
            if (sick*1.0)/num_balls > game_theory_threshold:
                balls[i][6] = True
                hiding += 1
        if balls[i][5] == NORMAL:
            # These balls will hide if a govt order is issued
            if (sick*1.0)/num_balls > govt_threshold:
                balls[i][6] = True

        # collision with walls
        if balls[i][0] < 0:
            balls[i][2] = -balls[i][2]
            balls[i][0] = 0
        if balls[i][0] > width:
            balls[i][2] = -balls[i][2]
            balls[i][0] = width
        if balls[i][1] < 0:
            balls[i][3] = -balls[i][3]
            balls[i][1] = 0
        if balls[i][1] > height:
            balls[i][3] = -balls[i][3]
            balls[i][1] = height
        
        # collision with each other

        for j in range(i+1, len(balls)):
            if balls[i][6] or balls[i][7]:
                continue
            x_dist = balls[j][0] - balls[i][0]
            y_dist = balls[j][1] - balls[i][1]
            dist2 = x_dist**2 + y_dist**2
            if dist2 == 0:
                continue # dunno why this happens, fuck it
            if dist2 < (2*ball_size)**2:
                dist = math.sqrt(dist2)
                final_dx = speed * x_dist / dist
                final_dy = speed * y_dist / dist
        
                balls[i][2] = -final_dx
                balls[i][3] = -final_dy
                balls[j][2] = final_dx
                balls[j][3] = final_dy

                # do transmission risk
                if balls[i][4] > 0 and balls[j][4] == 0 and not balls[j][8]:
                    if random.random() < transmission_rate:
                        balls[j][4] = 0.1
                        sick += 1
                elif balls[j][4] > 0 and balls[i][4] == 0 and not balls[i][8]:
                    if random.random() < transmission_rate:
                        balls[i][4] = 0.1
                        sick += 1


    screen.fill(black)
    # draw all the balls
    for i in range(0, len(balls)):
        if balls[i][4] == 0:
            color = white
        else:
            color = red
        if not balls[i][6] and not balls[i][7]:
            pygame.draw.circle(screen, color, [int(balls[i][0]), int(balls[i][1])], ball_size)
    pygame.display.flip()