import pygame

# Initialize Pygame
pygame.init()

# Set the screen dimensions
WIDTH, HEIGHT = 1536, 864
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Load the image
image_path = 'images/test.jpg'
image_surface = pygame.image.load(image_path)

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

# Print out image and screen details for debugging
#print("Height: ", HEIGHT)
#print("Scaled_Height: ", scaled_height)
#print("Width: ", WIDTH)
#print("Scaled_Width: ", scaled_width)

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

print("WASSUP")
# Quit Pygame
pygame.quit()
