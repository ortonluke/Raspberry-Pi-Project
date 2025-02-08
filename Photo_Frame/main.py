import pygame
from PIL import Image, ExifTags

# Initialize Pygame
pygame.init()

# Set the screen dimensions
WIDTH, HEIGHT = 1536, 864
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
image_path = 'images/IMG_0580.JPG'
image = load_corrected_image(image_path)

# Convert PIL image to Pygame surface
image = image.convert("RGB")  # Ensure compatibility
image_surface = pygame.image.fromstring(image.tobytes(), image.size, image.mode)

# Calculate scale factors for both width and height
scale_factor_width = WIDTH / image_surface.get_width()
scale_factor_height = HEIGHT / image_surface.get_height()

# Use the smallest scale factor to ensure the image fits
scale_factor = min(scale_factor_width, scale_factor_height)

# Scale the image using the selected scale factor
scaled_width = int(image_surface.get_width() * scale_factor)
scaled_height = int(image_surface.get_height() * scale_factor)
scaled_image = pygame.transform.scale(image_surface, (scaled_width, scaled_height))

# Calculate the margin for centering the image horizontally and vertically
margin_top = (HEIGHT - scaled_height) // 2
margin_left = (WIDTH - scaled_width) // 2

# Adjust the x and y positions to center the image
x = margin_left
y = margin_top

# Run the main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw the scaled image
    screen.blit(scaled_image, (x, y))

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()