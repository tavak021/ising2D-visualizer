import pygame
import matplotlib.pyplot as plt
import numpy as np
import time

AXIS_COLOR = (100, 100, 100)
SLIDER_LENGTH = 400
TICK_SPACING = 100

TAIL_LENGTH = 50
FANCY_COLORS = True

TIME_STEP = 0.05

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

class Plot:
    def __init__(self, window_size, lattice):

        # Pygame Config
        pygame.init()
        self.screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        pygame.display.set_caption("Ising Model")

        self.lattice = lattice

        self.parameters = []

        self.running = True

    # add tunable parameters
    def add_parameter(self, parameter):
        self.parameters.append(parameter)

    
    # get the position on the screen from cartesian coordinates on the plot
    def get_display_position(self, coords):
        s_size = self.screen.get_size()

        x_center = round(s_size[0] / 2)
        y_center = round(s_size[1] / 2)

        return (coords[0] * TICK_SPACING + x_center, -coords[1] * TICK_SPACING + y_center)
    
    # get the cartesian coords from a screen position
    def get_cartesian_coords(self, coords):
        s_size = self.screen.get_size()

        x_center = round(s_size[0] / 2)
        y_center = round(s_size[1] / 2)

        return ((coords[0] - x_center) / TICK_SPACING, -(coords[1] - y_center) / TICK_SPACING)

    # draw the axis and tick marks. TODO: use get_display_position for tick marks
    def draw_axis(self):
        s_size = self.screen.get_size()

        x_center = round(s_size[0] / 2)
        y_center = round(s_size[1] / 2)

        pygame.draw.line(self.screen, AXIS_COLOR, [x_center, 0], [x_center, s_size[1]], 2)
        pygame.draw.line(self.screen, AXIS_COLOR, [0, y_center], [s_size[0], y_center], 2)

        for x in range(0, x_center + 1, TICK_SPACING):
            pygame.draw.line(self.screen, AXIS_COLOR, [x_center + x, y_center - 5], [x_center + x, y_center + 5], 1)
            pygame.draw.line(self.screen, AXIS_COLOR, [x_center - x, y_center - 5], [x_center - x, y_center + 5], 1)

        for y in range(0, y_center + 1, TICK_SPACING):
            pygame.draw.line(self.screen, AXIS_COLOR, [x_center - 5, y_center + y], [x_center + 5, y_center + y], 1)
            pygame.draw.line(self.screen, AXIS_COLOR, [x_center - 5, y_center - y], [x_center + 5, y_center - y], 1)


    # draw sliders for the parameters
    def draw_sliders(self):
        i = 0
        for param in self.parameters:
            pygame.draw.line(self.screen, AXIS_COLOR, (25, 25+50*i), (25+SLIDER_LENGTH, 25+50*i), width=4)
            pygame.draw.circle(self.screen, WHITE, (param.get_slider_position(), 25+50*i), 6)
            i += 1

    # main loop
    def run(self):
        mouse_pressed = False
        while self.running:
            # Event Handler
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pressed = True

                        i = 0
                        for param in self.parameters:
                            slider_x = param.get_slider_position()
                            slider_y = 25 + 50*i

                            if (pygame.mouse.get_pos()[0]-slider_x)**2 + (pygame.mouse.get_pos()[1]-slider_y)**2 <= 36:
                                param.slider_dragging = True

                            i += 1

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        mouse_pressed = False

                        for param in self.parameters:
                            param.slider_dragging = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        X, Y = self.lattice.compute_correlation(10, 1000000)
                        plt.plot(X, Y)
                        plt.show()

            if mouse_pressed:
                for param in self.parameters:
                    if param.slider_dragging:
                        param.set_slider_value(pygame.mouse.get_pos()[0])

                        # print({param.name: param.value for param in self.parameters})


            self.screen.fill(BLACK)

            # Do drawing for frame here
            self.lattice.draw(self.screen)

            self.draw_sliders()

            pygame.display.flip()
            self.clock.tick(60)

            #print(f"fps: {self.clock.get_fps()}")
            print("Temperature: ", self.parameters[0].value)

            self.lattice.update(self.parameters)

class Parameter:
    def __init__(self, param_name: str, low: float, high: float, initial: float):
        self.name = param_name
        self.low = low
        self.high = high
        self.value = initial

        self.slider_dragging = False
    
    def get_slider_position(self):
        return 25 + (self.value - self.low) * SLIDER_LENGTH/(self.high-self.low)
    
    def set_slider_value(self, mouse_x):
        self.value = max(self.low, min(self.high, self.low + (mouse_x - 25) * (self.high-self.low)/SLIDER_LENGTH))