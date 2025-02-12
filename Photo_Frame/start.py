import os
import pygame
import subprocess
from PIL import Image, ExifTags

# Configuration
IMAGE_FOLDER = "images"
WIDTH, HEIGHT = 1200, 600  # Window size
FPS = 30  # Frames per second

def show_loading_screen():
    """Display a loading screen while images are downloading."""
    screen.fill((0, 0, 0))  # Black background
    font = pygame.font.SysFont(None, 40)
    loading_text = font.render("Downloading images...", True, (255, 255, 255))
    screen.blit(loading_text, ((WIDTH - loading_text.get_width()) // 2, HEIGHT // 2))
    pygame.display.update()
    
# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.mouse.set_visible(True)  # Show cursor for touchscreen use
clock = pygame.time.Clock()
show_loading_screen()

# Run downloader.py and wait for it to finish
subprocess.run(["python", "downloader.py"])

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

def show_loading_screen():
    """Display a loading screen while images are downloading."""
    screen.fill((0, 0, 0))  # Black background
    font = pygame.font.SysFont(None, 40)
    loading_text = font.render("Downloading images...", True, (255, 255, 255))
    screen.blit(loading_text, ((WIDTH - loading_text.get_width()) // 2, HEIGHT // 2))
    pygame.display.update()

# Pagination settings
padding = 20
thumbnails_per_row = (WIDTH - padding) // (THUMBNAIL_SIZE[0] + padding)
rows_per_page = (HEIGHT - 100) // (THUMBNAIL_SIZE[1] + padding)  # 100px reserved for Back button
thumbnails_per_page = thumbnails_per_row * rows_per_page

total_pages = (len(image_files) + thumbnails_per_page - 1) // thumbnails_per_page
current_page = 0

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
            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        pass  # No EXIF data or orientation tag found

    return image

def delete_images():
    for file in os.listdir(IMAGE_FOLDER):
        file_path = os.path.join(IMAGE_FOLDER, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    print("All images deleted.")

# Function to create a thumbnail for an image
def create_thumbnail(image_path, size=THUMBNAIL_SIZE):
    image = load_corrected_image(image_path)
    image.thumbnail(size)
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode)

# Function to show image grid with pagination
def show_image_grid():
    global current_page

    screen.fill((0, 0, 0))
    
    # Grid positions
    thumbnail_x = padding
    thumbnail_y = padding
    image_buttons = []
    
    # Get images for the current page
    start_index = current_page * thumbnails_per_page
    end_index = min(start_index + thumbnails_per_page, len(image_files))
    
    for i in range(start_index, end_index):
        image_path = image_files[i]
        thumbnail = create_thumbnail(image_path)
        image_rect = thumbnail.get_rect(topleft=(thumbnail_x, thumbnail_y))
        
        screen.blit(thumbnail, (thumbnail_x, thumbnail_y))
        image_buttons.append((image_rect, image_path))

        # Move to the next grid position
        thumbnail_x += THUMBNAIL_SIZE[0] + padding
        if (i - start_index + 1) % thumbnails_per_row == 0:
            thumbnail_x = padding
            thumbnail_y += THUMBNAIL_SIZE[1] + padding

    # Back Button (Positioned Near Bottom)
    back_button = pygame.Rect((WIDTH - 200) // 2, HEIGHT - 80, 200, 50)
    pygame.draw.rect(screen, (255, 0, 0), back_button)  # Red color
    font = pygame.font.SysFont(None, 30)
    back_text = font.render("Back", True, (255, 255, 255))
    screen.blit(back_text, (back_button.x + (back_button.width - back_text.get_width()) // 2,
                           back_button.y + (back_button.height - back_text.get_height()) // 2))

    # Draw Page Indicators (Circles)
    indicator_y = HEIGHT - 20
    indicator_x = WIDTH // 2 - (total_pages * 15) // 2  # Center indicators

    for page in range(total_pages):
        color = (255, 255, 255) if page == current_page else (100, 100, 100)
        pygame.draw.circle(screen, color, (indicator_x + page * 15, indicator_y), 5)

    pygame.display.update()
    return image_buttons, back_button

# Function to create the main menu
def show_menu():
    screen.fill((0, 0, 0))

    font = pygame.font.SysFont(None, 30)
    
    # Create "Slideshow" button
    slideshow_button = pygame.Rect((WIDTH - 300) // 2, HEIGHT // 3, 300, 50)
    pygame.draw.rect(screen, (255, 255, 255), slideshow_button)
    slideshow_text = font.render("Slideshow", True, (0, 0, 0))
    screen.blit(slideshow_text, (slideshow_button.x + 100, slideshow_button.y + 15))

    # Create "Images" button
    images_button = pygame.Rect((WIDTH - 300) // 2, HEIGHT // 2, 300, 50)
    pygame.draw.rect(screen, (255, 255, 255), images_button)
    images_text = font.render("Images", True, (0, 0, 0))
    screen.blit(images_text, (images_button.x + 120, images_button.y + 15))

    # Create "Quit" button
    quit_button = pygame.Rect((WIDTH - 300) // 2, HEIGHT * 2 // 3, 300, 50)
    pygame.draw.rect(screen, (255, 0, 0), quit_button)
    quit_text = font.render("Quit", True, (255, 255, 255))
    screen.blit(quit_text, (quit_button.x + 130, quit_button.y + 15))

    pygame.display.update()
    return slideshow_button, images_button, quit_button

# Run an image in main.py
def run_main(image_path):
    subprocess.Popen(["python", "main.py", image_path])

# Main program loop
running = True
in_grid = False
touch_start = None

while running:
    if in_grid:
        image_buttons, back_button = show_image_grid()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                touch_start = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                touch_end = event.pos
                
                if touch_start:  # Only proceed if touch_start is not None
                    if back_button.collidepoint(event.pos):
                        in_grid = False

                    else:
                        delta_x = touch_end[0] - touch_start[0]

                        if delta_x > 50 and current_page > 0:  # Swipe Right (Previous Page)
                            current_page -= 1
                        elif delta_x < -50 and current_page < total_pages - 1:  # Swipe Left (Next Page)
                            current_page += 1
                    
                    touch_start = None  # Reset touch

                    # Check if an image was clicked
                    for button_rect, image_path in image_buttons:
                        if button_rect.collidepoint(event.pos):
                            run_main(image_path)

    else:
        slideshow_button, images_button, quit_button = show_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if slideshow_button.collidepoint(event.pos):
                    subprocess.Popen(["python", "slideshow.py"])
                elif images_button.collidepoint(event.pos):
                    in_grid = True
                elif quit_button.collidepoint(event.pos):
                    delete_images()  # Delete images before quitting
                    running = False

pygame.quit()
