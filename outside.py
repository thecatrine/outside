import pygame
import sys, random
import math

pygame.init()

size = width, height = 1080, 768

speed = [1, 1]
black = 0, 0, 0
white = 255, 255, 255
red = 255, 0, 0

screen = pygame.display.set_mode(size)

old_ticks = ticks = pygame.time.get_ticks()

ball_size = 5
num_balls = 5000
speed = .1

transmission_rate = 0.2

sick_rate = 0.001

death_rate = 0.01
hospital_rate = 0.1

game_theory_threshold = 0.01
game_theory_rate = 0.00

govt_threshold = 0.05
govt_max_threshold = 0.10
govt_rate = 0.95

GAME_THEORY = 1
NORMAL = 2
RECKLESS = 3

NUM_GROUPS = 16
TOTAL_GROUPS = NUM_GROUPS**2

X_GRAN = width / NUM_GROUPS + 1
Y_GRAN = height / NUM_GROUPS + 1

def group_from_pos(x, y):
    x_coord = math.floor(x / X_GRAN)
    y_coord = math.floor(y / Y_GRAN)

    group = y_coord*NUM_GROUPS + x_coord
    if group > TOTAL_GROUPS:
        print("WHAT", group, x_coord, y_coord, X_GRAN, Y_GRAN)
        import pdb; pdb.set_trace()
    return group
#  x, y, dx, dy, sick, type, hiding, dead, immune, collision_group, hiding_threshold, r0
# 200, 300, 0.1, NORMAL, False, False, 0, 0

PI = 3.1415

VISUALIZE = True

num_runs = 2
avg_dead = 0
for run in range(0, num_runs):
    # Set up collision groups
    collision_groups = {}
    for i in range(0, TOTAL_GROUPS):
        collision_groups[i] = []

    # Set up population

    ball_0_x = width/2
    ball_0_y = width/2
    ball_0_group = group_from_pos(ball_0_x, ball_0_y)

    balls = [[ball_0_x, ball_0_y, speed, 0, 0.1, NORMAL, False, False, False, ball_0_group, 0.2, 0]]
    collision_groups[ball_0_group].append(0)

    for i in range(1, num_balls):
        x = random.randint(0, width)
        y = random.randint(0, height)
        angle = 2*PI*random.random()
        dx = speed*math.sin(angle)
        dy = speed*math.cos(angle)

        roll = random.random()
        ball_type = RECKLESS
        hiding_threshold = 1
        if roll < game_theory_rate:
            ball_type = GAME_THEORY
            hiding_threshold = game_theory_threshold
        else:
            ball_type = NORMAL
            hiding_threshold = random.random()*(govt_max_threshold-govt_threshold)+govt_threshold
        group = group_from_pos(x,y)
        ball = [x, y, dx, dy, 0.0, ball_type, False, False, False, group, hiding_threshold, 0]
        collision_groups[group].append(i)

        balls.append(ball)
    sick = 1
    hiding = 0
    dead = 0

    max_sick = 1

    tick = 0

    while sick > 0:
        tick += 1
        #if tick % 100 == 0:
        #    print("Tick", tick, "Sick",sick,"Hiding",hiding,"Dead",dead,"")
        ticks = pygame.time.get_ticks()
        delta = 10
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
                        if i in collision_groups[balls[i][9]]:
                            collision_groups[balls[i][9]].remove(i)
                    else:
                        balls[i][8] = True
                        balls[i][4] = 0.0

            if balls[i][6] or balls[i][7]:
                continue

            # hide inside
            if (sick*1.0)/num_balls > balls[i][10]:
                balls[i][6] = True
                hiding += 1
                if i in collision_groups[balls[i][9]]:
                    collision_groups[balls[i][9]].remove(i)

            if balls[i][6] or balls[i][7]:
                continue

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

            # maybe move to new collision group
            old_group = balls[i][9]
            new_group = group_from_pos(balls[i][0], balls[i][1])
            if new_group != old_group:
                try:
                    collision_groups[old_group].remove(i)
                except:
                    import pdb; pdb.set_trace()
                collision_groups[new_group].append(i)
                balls[i][9] = new_group

        for group in range(0, TOTAL_GROUPS):
            # The group has a list of balls that can collide
            for group_i in range(0, len(collision_groups[group])):
                for group_j in range(group_i+1, len(collision_groups[group])):
                    i = collision_groups[group][group_i]
                    j = collision_groups[group][group_j]

                    x_dist = balls[j][0] - balls[i][0]
                    y_dist = balls[j][1] - balls[i][1]

                    if x_dist**2 + y_dist**2 < ball_size**2:
                        theta = random.random()*2*PI
                        final_dx = speed * math.cos(theta)
                        final_dy = speed * math.sin(theta)
                
                        balls[i][2] = -final_dx
                        balls[i][3] = -final_dy
                        balls[j][2] = final_dx
                        balls[j][3] = final_dy

                        # do transmission risk
                        if balls[i][4] > 0 and balls[j][4] == 0 and not balls[j][8]:
                            if random.random() < transmission_rate:
                                balls[j][4] = 0.1
                                sick += 1
                                max_sick += 1
                                balls[i][11] += 1
                        elif balls[j][4] > 0 and balls[i][4] == 0 and not balls[i][8]:
                            if random.random() < transmission_rate:
                                balls[i][4] = 0.1
                                sick += 1
                                max_sick += 1
                                balls[j][11] += 1


        if VISUALIZE:
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
    # Do math
    # get r0
    total_r0 = 0
    num_transmitters = 0
    for ball in balls:
        if ball[11] != 0:
            total_r0 += ball[11]
            num_transmitters += 1
    r0 = total_r0/num_transmitters
    print("Run complete, ","Dead",dead,"Max sick", max_sick, "Hiding", hiding, "r0", r0)
    avg_dead += dead
print("Experiment complete", "Rate", game_theory_rate, "Threshold", game_theory_threshold, "Dead", avg_dead*1.0/num_runs)