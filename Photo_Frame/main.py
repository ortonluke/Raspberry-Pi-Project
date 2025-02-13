import pygame
import sys
from PIL import Image, ExifTags

# Ensure an image path is provided
if len(sys.argv) < 2:
    print("Error: No image path provided.")
    pygame.quit()
    exit()

# Get image path from command-line arguments
image_path = sys.argv[1]

# Initialize Pygame
pygame.init()
pygame.mouse.set_visible(False)  # Show cursor

# Set the screen dimensions
WIDTH, HEIGHT = 1024, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Load and correct image orientation using Pillow (PIL)
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

# Load image with rotation correction
image = load_corrected_image(image_path)

# Convert PIL image to Pygame surface
image = image.convert("RGB")  # Ensure compatibility
image_surface = pygame.image.fromstring(image.tobytes(), image.size, image.mode)

# Calculate scale factors for both width and height
scale_factor = min(WIDTH / image_surface.get_width(), HEIGHT / image_surface.get_height())

# Scale the image
scaled_width = int(image_surface.get_width() * scale_factor)
scaled_height = int(image_surface.get_height() * scale_factor)
scaled_image = pygame.transform.scale(image_surface, (scaled_width, scaled_height))

# Center the image
x = (WIDTH - scaled_width) // 2
y = (HEIGHT - scaled_height) // 2

# Run the main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            running = False  # Quit on any key press or mouse click

    # Draw the image
    screen.fill((0, 0, 0))
    screen.blit(scaled_image, (x, y))
    pygame.display.update()

# Quit Pygame
pygame.quit()
