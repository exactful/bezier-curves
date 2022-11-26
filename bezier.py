import pygame
import math

class Line():

    def __init__(self, point_a, point_b):

        opp = point_b[1] - point_a[1]
        adj = point_b[0] - point_a[0]
        angle = math.atan2(opp, adj)
        hyp = math.hypot(opp, adj)

        self.start = point_a
        self.angle = angle # In radians
        self.length = hyp
        self.end = point_b

    def draw(self, screen, colour):
        pygame.draw.line(screen, colour, self.start, self.end, 2)
        pygame.draw.circle(screen, colour, (self.start), 3)
        pygame.draw.circle(screen, colour, (self.end), 3)

    def part_way_point(self, factor):
        return (self.start[0] + math.cos(self.angle) * self.length * factor, self.start[1] + math.sin(self.angle) * self.length * factor)

    def draw_part_way_point(self, screen, factor, colour):
        pygame.draw.circle(screen, colour, (self.part_way_point(factor)), 5)

# Define constants
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 900
TITLE = "Bezier curve generator"

# Variables to control travel along the lines
grow = True                     # Determines whether to increase / decrease the factor
factor = 0.5                    # Current factor
factor_delta_default = 0.0005   # Default value to increase / decrease factor by
factor_delta = 0                # Value to increase / decrease factor by; starts as zero, then gets set to default factor delta

# Define points in the four corners of the screen
point_margin = 50
points = []
points.append((point_margin, SCREEN_HEIGHT-point_margin))
points.append((point_margin, point_margin))
points.append((SCREEN_WIDTH-point_margin, point_margin))
points.append((SCREEN_WIDTH-point_margin, SCREEN_HEIGHT-point_margin))

# Define pygame.Rect for each point in a list
rect_size = 10
rects = []
for point in points:
    rects.append(pygame.Rect(point[0]-rect_size/2, point[1]-rect_size/2, rect_size, rect_size))

# Control drag and drop
can_drag = False    # Mouse button is pressed down
is_dragging = -1    # The index of the point being dragged

# Record steps along the path when space bar is pressed
steps = []

# Current wizard helper step
wizard_step = 1

# Pygame stuff
pygame.init()
font = pygame.font.SysFont('calibri', 20)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)

done = False

while not done:
    
    # Check events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            can_drag = True
        elif event.type == pygame.MOUSEBUTTONUP:
            can_drag = False
            is_dragging = -1

    # If mouse button is pressed down
    if can_drag:
        if wizard_step == 3:
            wizard_step = 4
        # Get mouse pointer position
        mouse_pos = pygame.mouse.get_pos()
        # Iterate through each rect
        for i in range(len(rects)):
            # If no rect is currently being dragged, check if mouse pointer is over a rect
            if is_dragging == -1:
                if rects[i].collidepoint(mouse_pos):
                    is_dragging = i
            # If the current rect is being dragged
            if is_dragging == i:
                # Overwrite current rect with one in the new position
                rects[i] = pygame.Rect(mouse_pos[0]-rect_size/2, mouse_pos[1]-rect_size/2, rect_size, rect_size)
                points[i] = mouse_pos

    # Check key events
    keys = pygame.key.get_pressed()

    if keys[pygame.K_RETURN]:
        # If return key is pressed, set the amount by which the factor (the % along each line) should change
        factor_delta = factor_delta_default
        if wizard_step == 1:
            wizard_step = 2
    elif keys[pygame.K_SPACE]:
        # If space bar is pressed, trace the path
        steps.append(line_f.part_way_point(factor))
        if wizard_step == 2:
            wizard_step = 3
        elif wizard_step == 4:
            wizard_step = -1
    else:
        # Reset the path trace
        steps = []

    # Increase and decrease the factor (the % along each line), maintaining it between 0 and 1
    if factor > 1:
        grow = False
        steps = []
    elif factor < 0:
        grow = True
        steps = []

    if grow:
        factor += factor_delta
    else:
        factor -= factor_delta

    # Create three line objects between the four points
    line_a = Line(points[0], points[1])
    line_b = Line(points[2], points[3])
    line_c = Line(line_a.end, line_b.start)

    # Create two line objects between the three line objects above
    line_d = Line(line_a.part_way_point(factor), line_c.part_way_point(factor))
    line_e = Line(line_c.part_way_point(factor), line_b.part_way_point(factor))

    # Create the final line object between the two line objects above
    line_f = Line(line_d.part_way_point(factor), line_e.part_way_point(factor))

    # Draw the display
    screen.fill((0, 0, 0))

    # Draw each rect
    for rect in rects:
        pygame.draw.rect(screen, RED, rect)

    # Draw the lines
    line_a.draw(screen, RED)
    line_b.draw(screen, RED)
    line_c.draw(screen, RED)
    line_d.draw(screen, GREEN)
    line_e.draw(screen, GREEN)
    line_f.draw(screen, BLUE)

    # Draw the main point
    line_f.draw_part_way_point(screen, factor, WHITE)

    # Draw the path
    for step in steps:
        pygame.draw.circle(screen, WHITE, (step), 3)

    # Display messages
    if wizard_step == 1:
        msg = "Press return to start"
    elif wizard_step == 2 or wizard_step == 4:
        msg = "Hold the space bar to trace the path"
    elif wizard_step == 3:
        msg = "Drag and drop the rectangles to create new curves"

    if wizard_step in (1,2,3, 4):
        screen_msg = font.render(msg, True, WHITE)
        screen.blit(screen_msg, (point_margin, 20))
    
    screen_factor = font.render(f"Factor: {round(factor, 2)}", True, WHITE)
    screen.blit(screen_factor, (SCREEN_WIDTH-140, 20))

    pygame.display.flip()