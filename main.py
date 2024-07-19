import pygame
import random
import os.path
import neat


pygame.init()
ground_scroll = 0
scroll_speed = 4  # Pixels
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
font = pygame.font.SysFont('Bauhaus 93', 60)
white = (255 , 255 , 255)
screen_width = 864
screen_height = 936

# Indirect path to images
# Get the directory of the script
script_dir = os.path.dirname(__file__)

# Construct the relative path to the image file
background_png = os.path.join(script_dir, "Images", "bg.png")
ground_png = os.path.join(script_dir, "Images", "ground.png")
bird1_png = os.path.join(script_dir, "Images", "bird1.png")
bird2_png = os.path.join(script_dir, "Images", "bird2.png")
bird3_png = os.path.join(script_dir, "Images", "bird3.png")
pipe_png = os.path.join(script_dir, "Images", "pipe.png")
button_png = os.path.join(script_dir, "Images", "restart.png")

# Load images
background = pygame.image.load(background_png)
ground_img = pygame.image.load(ground_png)
bird1_img = pygame.image.load(bird1_png)
bird2_img = pygame.image.load(bird2_png)
bird3_img = pygame.image.load(bird3_png)
pipe_img = pygame.image.load(pipe_png)
button_img = pygame.image.load(button_png)


# Screen size and display

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird Clone')

# Game clock and fps
clock = pygame.time.Clock()
fps = 60


class Bird (pygame.sprite.Sprite): #Sprite classses already have update written in them
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(bird1_png)
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1,4):
            img = pygame.image.load(eval(f'bird{num}_png'))
            self.images.append(img)
        self.image = self.images[self.index]
        self.vel = 0
        self.clicked = False


    def update(self):
        #Gravity
        if flying == True:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        #Jump
        if game_over == False:
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:   #Only clicking, no pressing down
                self.clicked = False

            # handle the animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            #rotate bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)

        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)



#PIPES
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(pipe_png)
        self.rect = self.image.get_rect()

        #position 1 is top, -1 is bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image,False,True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x,y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill() #destroy pipes out of screen


bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
flappy = Bird(100, int(screen_height / 2))
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)

    def draw(self):
        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()
        #check if mouse over button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
       #draw
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action
def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height/2)

# Define variables

bird_group.add(flappy)

pygame.init()


#Button
button = Button(screen_width // 2 - 50, screen_height // 2 -100, button_img)
# Game loop
run = True
while run:

    clock.tick(fps)
    # Draw background
    screen.blit(background,(0,0))
    # Generate bird
    bird_group.draw(screen)
    bird_group.update()
    # Generate pipe
    pipe_group.draw(screen)

    # Draw Ground
    screen.blit(ground_img,(0,768))

    if game_over == False and flying == True:

        #generate pipes
        time_now = pygame.time.get_ticks()
        pipe_height = random.randint(-150, 150)
        if time_now - last_pipe > pipe_frequency:
            btm_pipe = Pipe(screen_width, int(screen_height / 2)+ pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2)+ pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        # Draw and scroll ground
        screen.blit(ground_img,(ground_scroll,768))
        ground_scroll -= scroll_speed
        if abs(ground_scroll) >35:
            ground_scroll=0
        pipe_group.update()

        #Score
        if len(pipe_group) > 0:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                    and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                    and pass_pipe == False:
                pass_pipe = True
            if pass_pipe == True:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                    score += 1
                    pass_pipe = False

        draw_text(str(score), font, white, int(screen_width / 2), 20)

        #look for collision
        if pygame.sprite.groupcollide(bird_group, pipe_group, False,False) or flappy.rect.top < 0:
            game_over = True

        # Check ground collision
        if flappy.rect.bottom >= 768:
            game_over = True
            flying = False

    #check for game over and reset
    if game_over == True:
        if button.draw() == True:
            game_over = False
            reset_game()
            score = 0


    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  #Quit the game
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:  #Wait for user input and game is not over
            flying = True

    pygame.display.update()
pygame.quit()

