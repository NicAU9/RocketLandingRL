import pygame
import sys
import numpy as np

pygame.init()

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

gravity = 0.5 
mass = 1

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rocket Landing Game")
clock = pygame.time.Clock()
fps = 30

class Rocket:
    def __init__(self, state):
        # state: ['x', 'y', 'vx', 'vy', 'theta', 'w']
        # Cmd: ['Thrust', 'delta']

        self.image = pygame.image.load("rocket.png")
        # self.width, self.height = self.image.get_size()
        self.width = 20  
        self.height = 60

        # State Init
        self.state = state

        # Cmd Init
        self.thruster_angle = 0
        self.thrust = 0

        # Thrust position from direct kinematic
        self.thrust_x = self.state[0] + np.sin(np.radians(self.state[4])) * self.height / 2
        self.thrust_y = self.state[1] + np.cos(np.radians(self.state[4])) * -self.height / 2

        # Kinematic params
        self.mass = mass
        self.g = -gravity
        self.I = 50
        
        self.thrust_on = False

    def update_state(self, cmd):
        dt = 1/fps
        x, y, vx, vy, theta, w = self.state      
        T, delta = np.array(cmd)

        self.thruster_angle = theta - delta
        self.thrust = T

        # Forces applied by thrust
        Fx = np.sin(np.radians(self.thruster_angle)) * T
        Fy = np.cos(np.radians(self.thruster_angle)) * T

        # Acceleration from thrust
        ax = Fx / self.mass
        ay = -Fy / self.mass - self.g

        ## Update linear states
        # Update speed
        vx += ax * dt  * 30
        vy += ay * dt * 30

        # Update position
        x += vx * dt * 30
        y += vy * dt * 30

        # Angular acceleration due to thrust
        self.thrust_x = x + np.sin(np.radians(theta)) * -self.height / 2
        self.thrust_y = y + np.cos(np.radians(theta)) * self.height / 2

        lever_arm_x = self.thrust_x - x
        lever_arm_y = self.thrust_y - y

        alpha = (lever_arm_x * Fy + lever_arm_y * Fx) / self.I

        ## Update angular states
        # Update speed
        w += alpha * dt * 30

        # Update angle
        theta += w * dt * 30

        self.state = np.array([x, y, vx, vy, theta, w])

    def get_state(self):
        return self.state

    def draw(self, screen):
        x, y, _, _, theta, _ = self.state

        rotated_image = pygame.transform.rotate(self.image, -theta)
        new_rect = rotated_image.get_rect(center=(x, y))
        screen.blit(rotated_image, new_rect.topleft)

        thrust_length = self.thrust * 50
        thrust_x = self.thrust_x - thrust_length * np.sin(np.radians(self.thruster_angle))
        thrust_y = self.thrust_y + thrust_length * np.cos(np.radians(self.thruster_angle))

        pygame.draw.line(screen, (255, 0, 0), (self.thrust_x, self.thrust_y), (thrust_x, thrust_y), 3)

    def check_collision(self, screen):
        x, y, vx, vy, theta, _ = self.state

        # Floor
        floor_y = HEIGHT - 20
        pygame.draw.rect(screen, (139, 69, 19), (0, floor_y, WIDTH, 20))  # Brown-colored floor

        # Target
        target_x, target_y, target_width, target_height = WIDTH // 2 - 50, floor_y - 10, 100, 10
        pygame.draw.rect(screen, (0, 255, 0), (target_x, target_y, target_width, target_height))

        # Ground collision
        if y + self.height / 2  >= floor_y:
            y = floor_y - self.height / 2
            # self.vy = 0
            # self.vx *= 0.9
            
            if (target_x <= x <= target_x + target_width) and abs(theta) < 5 and abs(vx) < 5 and abs(vy) < 5:
                return "win"  
            else:
                return "lose"  
        
        return "continue"

# Game loop
init_state = np.array([WIDTH//4, HEIGHT//4, 0, 0, 0, 0])  # Initial state: [x, y vx, vy, theta, w]

rocket = Rocket(init_state)

game_state = "continue"
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if game_state != "continue":
        # Display the appropriate screen
        font = pygame.font.SysFont("Arial", 36)
        if game_state == "win":
            game_over_text = font.render("You Win!", True, (0, 255, 0))
        elif game_state == "lose":
            game_over_text = font.render("Game Over", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        continue

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
        trust_input = gravity * mass + 0.2
    else:
        trust_input = 0

    if keys[pygame.K_LEFT]:
        delta_input = -15
    if keys[pygame.K_RIGHT]:
        delta_input = 15

    cmd = np.array([trust_input, delta_input])

    rocket.update_state(cmd)

    game_state = rocket.check_collision(screen)

    rocket.draw(screen)

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
sys.exit()
