import os
import pygame
import time
import random
from PIL import Image, ExifTags

# Configuration
IMAGE_FOLDER = "images"
DISPLAY_TIME = 5  # Time each image is fully shown (in seconds)
FADE_TIME = 3  # Time for the fade transition (in seconds)
FPS = 30  # Frames per second for smooth fade
WIDTH, HEIGHT = 1536, 864

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.mouse.set_visible(True)  # Show cursor
clock = pygame.time.Clock()

# Function to load and correct image orientation using PIL
def load_corrected_image(image_path):
    image = Image.open(image_path)

    try:
        for tag in ExifTags.TAGS:
            if ExifTags.TAGS[tag] == "Orientation":
                orientation_tag = tag
                break
        exif = image._getexif()
        if exif and orientation_tag in exif:
            orientation = exif[orientation_tag]

            # Rotate based on EXIF orientation
            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)

    except (AttributeError, KeyError, IndexError):
        pass  # No EXIF data or orientation tag found

    return image

# Load all image paths from the folder and shuffle them
image_files = [
    os.path.join(IMAGE_FOLDER, f) for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('png', 'jpg', 'jpeg'))
]

if not image_files:
    print("No images found in the folder.")
    pygame.quit()
    exit()

random.shuffle(image_files)  # Randomize order at the start

# Function to scale and center an image
def prepare_image(image):
    image = image.convert("RGB")  # Ensure compatibility
    image_surface = pygame.image.fromstring(image.tobytes(), image.size, image.mode)

    # Calculate scaling factor
    scale_factor = min(WIDTH / image_surface.get_width(), HEIGHT / image_surface.get_height())

    # Scale image
    scaled_width = int(image_surface.get_width() * scale_factor)
    scaled_height = int(image_surface.get_height() * scale_factor)
    scaled_image = pygame.transform.scale(image_surface, (scaled_width, scaled_height))

    # Centering
    x = (WIDTH - scaled_width) // 2
    y = (HEIGHT - scaled_height) // 2

    return scaled_image, (x, y)

# Function to fade between images, now supporting immediate quit
def fade_transition(old_image, old_pos, new_image, new_pos):
    for alpha in range(0, 256, int(255 / (FADE_TIME * FPS))):  # Fade step based on FPS
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return False  # Exit fade transition immediately

        screen.fill((0, 0, 0))  # Clear screen
        old_image.set_alpha(255 - alpha)  # Reduce opacity of old image
        new_image.set_alpha(alpha)  # Increase opacity of new image
        screen.blit(old_image, old_pos)
        screen.blit(new_image, new_pos)
        pygame.display.update()
        clock.tick(FPS)  # Control frame rate
    return True  # Completed fade transition successfully

# Main loop
running = True
index = 0

# Load first image
current_image = load_corrected_image(image_files[index])
current_scaled_image, current_position = prepare_image(current_image)

while running:
    # Display the current image
    screen.fill((0, 0, 0))
    screen.blit(current_scaled_image, current_position)
    pygame.display.update()

    # Timer logic for image display
    start_time = time.time()
    while time.time() - start_time < DISPLAY_TIME:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                running = False
                break
        if not running:
            break

    if not running:
        break  # Ensure immediate exit

    # Load next image
    index += 1
    if index >= len(image_files):  
        random.shuffle(image_files)  # Shuffle again before restarting
        index = 0

    next_image = load_corrected_image(image_files[index])
    next_scaled_image, next_position = prepare_image(next_image)

    # Apply fade transition; exit if quit event occurs
    if not fade_transition(current_scaled_image, current_position, next_scaled_image, next_position):
        break  

    # Set next image as current
    current_scaled_image, current_position = next_scaled_image, next_position

pygame.quit()
