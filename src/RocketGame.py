import pygame
import sys
import numpy as np

# Initialize Pygame
pygame.init()

# Screen dimensions and colors
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Rocket settings
gravity = 0.5  # Gravity force
mass = 1

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rocket Landing Game")
clock = pygame.time.Clock()

class Rocket:
    def __init__(self, state):
        # state: ['x', 'y', 'vx', 'vy', 'theta', 'w']
        # Cmd: ['Thrust', 'delta']
        self.width = 20  
        self.height = 60

        # State Init
        self.x, self.y, self.vx, self.vy, self.theta, self.w = state

        # Cmd Init
        self.thruster_angle = 0
        self.thrust = 0

        # Thrust position from direct kinemtatic
        self.thrust_x = self.x + np.sin(np.radians(self.theta)) * self.height/2
        self.thrust_y = self.y + np.cos(np.radians(self.theta)) * -self.height/2

        # Kinematic params
        self.mass = mass
        self.g = -gravity
        self.I = 100
        
        self.thrust_on = False

    def update_state(self, cmd):
        T, delta = np.array(cmd)

        self.thruster_angle = self.theta - delta
        self.thrust = T

        # Forces applied by thrust
        Fx = np.sin(np.radians(self.thruster_angle)) * T
        Fy = np.cos(np.radians(self.thruster_angle)) * T

        # Acceleration from thrust
        ax = Fx / self.mass
        ay = -Fy / self.mass - self.g

        ## Update linear states
        # Update speed
        self.vx += ax
        self.vy += ay

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Angular acceleration due to thrust
        self.thrust_x = self.x + np.sin(np.radians(self.theta)) * -self.height/2
        self.thrust_y = self.y + np.cos(np.radians(self.theta)) * self.height/2

        lever_arm_x = self.thrust_x - self.x
        lever_arm_y = self.thrust_y - self.y

        alpha = (lever_arm_x * Fy + lever_arm_y * Fx) / self.I

        ## Update angular states
        # Update speed
        self.w += alpha

        # Update angle
        self.theta += self.w


    def draw(self):
        # Rocket
        rocket_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(rocket_surface, (0, 0, 0), (0, 0, self.width, self.height))
        rotated_rocket = pygame.transform.rotate(rocket_surface, -self.theta)
        new_rocket_rect = rotated_rocket.get_rect(center=(self.x, self.y))
        screen.blit(rotated_rocket, new_rocket_rect.topleft)

        # Trust Line
        thrust_length = self.thrust * 50
        thrust_x = self.thrust_x - thrust_length * np.sin(np.radians(self.thruster_angle))
        thrust_y = self.thrust_y + thrust_length * np.cos(np.radians(self.thruster_angle))

        pygame.draw.line(screen, (255, 0, 0), (self.thrust_x, self.thrust_y), (thrust_x, thrust_y), 3)

    def check_collision(self):
        # Floor
        floor_y = HEIGHT - 20
        pygame.draw.rect(screen, (139, 69, 19), (0, floor_y, WIDTH, 20))  # Brown-colored floor

        # Ground collision
        if self.y + self.height / 2 >= floor_y:
            self.y = floor_y - self.height / 2  # Set position to ground level
            self.vy = 0  # Stop vertical movement
            self.vx *= 0.9  # Simulate friction by reducing horizontal velocity

        # Target
        pygame.draw.rect(screen, (0, 255, 0), (WIDTH // 2 - 50, floor_y - 10, 100, 10))


# Game loop
init_state = np.array([WIDTH//2, HEIGHT//4, 0, 0, 0, 0]) # Initial state: [x, y vx, vy, theta, w]

rocket = Rocket(init_state)  

running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    trust_input = 0
    delta_input = 0

    # Cmd
    if keys[pygame.K_UP]:
        if not rocket.thrust_on: 
            rocket.thrust_on = True
    else:
        rocket.thrust_on = False 

    if rocket.thrust_on:
        trust_input = gravity*mass + 0.1
    else:
        trust_input = 0

    if keys[pygame.K_LEFT]:
        delta_input = -15
    if keys[pygame.K_RIGHT]:
        delta_input =  15 

    cmd = np.array([trust_input, delta_input])

    rocket.update_state(cmd)

    rocket.draw()

    rocket.check_collision()

    pygame.display.flip()
    clock.tick(30)  

pygame.quit()
sys.exit()
