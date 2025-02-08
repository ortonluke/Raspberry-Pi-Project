import os
import pygame
import subprocess
from PIL import Image, ExifTags

# Configuration
IMAGE_FOLDER = "images"
WIDTH, HEIGHT = 1200, 600  # Window size
FPS = 30  # Frames per second

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.mouse.set_visible(True)  # Hide cursor for a clean display
clock = pygame.time.Clock()

# Thumbnail size
THUMBNAIL_SIZE = (150, 150)

# Load all image paths from the folder
image_files = [
    os.path.join(IMAGE_FOLDER, f) for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('png', 'jpg', 'jpeg'))
]

if not image_files:
    print("No images found in the folder.")
    pygame.quit()
    exit()

# Function to load and correct image orientation using PIL
def load_corrected_image(image_path):
    image = Image.open(image_path)

    try:
        # Get EXIF data to correct the orientation
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

# Function to load and create a thumbnail for an image
def create_thumbnail(image_path, size=THUMBNAIL_SIZE):
    image = load_corrected_image(image_path)  # Correct orientation first
    image.thumbnail(size)  # Resize the image to the thumbnail size
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode)

# Function to create a grid of image previews
def show_image_grid():
    screen.fill((0, 0, 0))  # Fill the screen with black
    
    # Grid configuration
    padding = 20
    thumbnails_per_row = (WIDTH - padding) // (THUMBNAIL_SIZE[0] + padding)
    thumbnail_x = padding
    thumbnail_y = padding
    image_buttons = []

    # Create thumbnails and place them in a grid
    for i, image_path in enumerate(image_files):
        thumbnail = create_thumbnail(image_path)
        image_rect = thumbnail.get_rect(topleft=(thumbnail_x, thumbnail_y))
        
        screen.blit(thumbnail, (thumbnail_x, thumbnail_y))
        image_buttons.append((image_rect, image_path))

        # Move to the next position in the grid
        thumbnail_x += THUMBNAIL_SIZE[0] + padding
        if (i + 1) % thumbnails_per_row == 0:
            thumbnail_x = padding
            thumbnail_y += THUMBNAIL_SIZE[1] + padding

    # Create "Back" button near the bottom
    back_button = pygame.Rect((WIDTH - 250) // 2, HEIGHT - 80, 250, 60)
    pygame.draw.rect(screen, (255, 0, 0), back_button)  # Red color
    font = pygame.font.SysFont(None, 35)
    back_text = font.render("Back", True, (255, 255, 255))
    screen.blit(back_text, (back_button.x + (back_button.width - back_text.get_width()) // 2,
                            back_button.y + (back_button.height - back_text.get_height()) // 2))


    pygame.display.update()
    return image_buttons, back_button

# Function to create the main menu
def show_menu():
    screen.fill((0, 0, 0))  # Fill the screen with black
    
    # Create "Slideshow" button
    slideshow_button = pygame.Rect((WIDTH - 300) // 2, HEIGHT // 3, 300, 50)
    pygame.draw.rect(screen, (255, 255, 255), slideshow_button)  # White color
    font = pygame.font.SysFont(None, 30)
    slideshow_text = font.render("Slideshow", True, (0, 0, 0))  # Black text
    screen.blit(slideshow_text, (slideshow_button.x + (slideshow_button.width - slideshow_text.get_width()) // 2,
                                 slideshow_button.y + (slideshow_button.height - slideshow_text.get_height()) // 2))

    # Create "Images" button
    images_button = pygame.Rect((WIDTH - 300) // 2, HEIGHT // 2, 300, 50)
    pygame.draw.rect(screen, (255, 255, 255), images_button)  # White color
    images_text = font.render("Images", True, (0, 0, 0))  # Black text
    screen.blit(images_text, (images_button.x + (images_button.width - images_text.get_width()) // 2,
                              images_button.y + (images_button.height - images_text.get_height()) // 2))

    # Create "Quit" button
    quit_button = pygame.Rect((WIDTH - 300) // 2, HEIGHT * 2 // 3, 300, 50)
    pygame.draw.rect(screen, (255, 0, 0), quit_button)  # Red color
    quit_text = font.render("Quit", True, (255, 255, 255))  # White text
    screen.blit(quit_text, (quit_button.x + (quit_button.width - quit_text.get_width()) // 2,
                            quit_button.y + (quit_button.height - quit_text.get_height()) // 2))

    pygame.display.update()
    return slideshow_button, images_button, quit_button

# Function to run the main script with the selected image
def run_main(image_path):
    subprocess.Popen(["python", "main.py", image_path])  # Start main.py in the background

# Main program loop
running = True
in_grid = False  # Track whether we're in the image grid

while running:
    if in_grid:
        image_buttons, back_button = show_image_grid()  # Show image grid
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):  # Back button clicked
                    in_grid = False  # Exit the image grid view
                else:
                    # Check if any thumbnail was clicked
                    for button_rect, image_path in image_buttons:
                        if button_rect.collidepoint(event.pos):  # Thumbnail clicked
                            run_main(image_path)  # Run the main script with the selected image
                            # Do not stop the loop to keep start.py running
    else:
        slideshow_button, images_button, quit_button = show_menu()  # Show main menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if slideshow_button.collidepoint(event.pos):  # Slideshow clicked
                    subprocess.Popen(["python", "slideshow.py"])  # Run slideshow script asynchronously
                    # Do not stop the loop to keep start.py running
                elif images_button.collidepoint(event.pos):  # Images clicked
                    in_grid = True  # Go to image grid
                elif quit_button.collidepoint(event.pos):  # Quit clicked
                    running = False

pygame.quit()
