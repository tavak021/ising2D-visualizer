import numpy as np
import pygame
import math
import colorsys

class Lattice:
    def __init__(self, width, height, dtype=np.int8):
        self.width = width
        self.height = height

        self.points = np.zeros(shape=(self.width, self.height), dtype=dtype)

class IsingLattice(Lattice):
    def __init__(self, width, height):
        Lattice.__init__(self, width, height)

        self.rng = np.random.default_rng()

        self.initialize_lattice()
        self.create_masks()


    def initialize_lattice(self, same_spin=True):
        for i in range(self.width):
            for j in range(self.height):
                if same_spin or self.rng.random() > 0.5:
                    self.points[i][j] = -1
                else:
                    self.points[i][j] = 1

    def create_masks(self):
        mask = np.zeros(shape=(self.width, self.height), dtype=np.bool)
        for i in range(self.width):
            for j in range(self.height):
                if (i+j) % 2 == 0:
                    mask[i][j] = True

        self.masks = [mask, ~mask]

    def get_point(self, i, j):
        return self.points[i%self.width][j%self.height]

    def compute_correlation(self, max_distance, samples):
        correlations_squared = {} # {distance^2: [count, sum of sigma_s * sigma s_']}
        for _ in range(samples):
            sample_i = self.rng.integers(0, self.width)
            sample_j = self.rng.integers(0, self.height)

            i = self.rng.integers(-0.5*max_distance, 0.5*max_distance)
            j = self.rng.integers(-0.5*max_distance, 0.5*max_distance)

            distance_squared = i**2 + j**2

            if distance_squared not in correlations_squared:
                correlations_squared[distance_squared] = [0, 0]

            if distance_squared != 0:
                correlations_squared[distance_squared][0] += 1
                correlations_squared[distance_squared][1] += self.get_point(sample_i, sample_j) * self.get_point(sample_i + i, sample_j + j)

        keys = np.array(sorted(correlations_squared))
        count, total = np.array([correlations_squared[k] for k in keys]).T

        X = np.sqrt(keys)
        Y = np.divide(total, count)

        return (X, Y)
    
    def update(self, parameters):
        B = parameters[0].value
        J = parameters[1].value
        T = parameters[2].value

        for mask in self.masks:
            nn_sums = np.roll(self.points, 1, axis=0) + np.roll(self.points, -1, axis=0) + np.roll(self.points, 1, axis=1) + np.roll(self.points, -1, axis=1)
            delta_E = 2 * self.points * (J * nn_sums + B)

            flip = self.rng.random((self.width, self.height)) < np.exp(-np.maximum(delta_E, 0) / T)
            self.points[mask & flip] *= -1

    def draw(self, screen):
        window_size = screen.get_size()

        cell_x = window_size[0]/self.width
        cell_y = window_size[1]/self.height

        for i in range(self.width):
            for j in range(self.height):
                if self.points[i][j] == 1:
                    pygame.draw.rect(screen, (90, 0, 255), (cell_x*i, cell_y*j, cell_x, cell_y))

class XYLattice(Lattice):
    def __init__(self, width, height):
        Lattice.__init__(self, width, height, dtype=np.float32)

        self.rng = np.random.default_rng()

        self.initialize_lattice()
        self.create_masks()


    def initialize_lattice(self):
        for i in range(self.width):
            for j in range(self.height):
                self.points[i][j] = 0

    def create_masks(self):
            mask = np.zeros(shape=(self.width, self.height), dtype=np.bool)
            for i in range(self.width):
                for j in range(self.height):
                    if (i+j) % 2 == 0:
                        mask[i][j] = True

            self.masks = [mask, ~mask]
    
    def get_point(self, i, j):
        return self.points[i%self.width][j%self.height]
    
    def update(self, parameters):
        T = parameters[0].value
        delta = parameters[1].value

        for mask in self.masks:
            proposed_spins = self.rng.random((self.width, self.height), dtype=np.float32)*2*np.pi
            
            roll_left = np.roll(self.points, -1, axis=0)
            roll_right = np.roll(self.points, 1, axis=0)
            roll_down = np.roll(self.points, -1, axis=1)
            roll_up = np.roll(self.points, 1, axis=1)

            E_old = -(np.cos(self.points - roll_left) + np.cos(self.points - roll_right) + np.cos(self.points - roll_down) + np.cos(self.points - roll_up))-delta*np.cos(self.points)**6
            E_new = -(np.cos(proposed_spins - roll_left) + np.cos(proposed_spins - roll_right) + np.cos(proposed_spins - roll_down) + np.cos(proposed_spins - roll_up))-delta*np.cos(proposed_spins)**6

            delta_E = E_new-E_old

            random_array = self.rng.random((self.width, self.height), np.float32)

            flip = delta_E < 0 if T == 0 else random_array < np.exp(-np.maximum(delta_E, 0) / T)
            self.points[mask & flip] = proposed_spins[mask & flip]

    def draw(self, screen):
        window_size = screen.get_size()

        cell_x = window_size[0]/self.width
        cell_y = window_size[1]/self.height

        for i in range(self.width):
            for j in range(self.height):
                #pygame.draw.rect(screen, get_rgb(self.points[i][j]), (cell_x*i, cell_y*j, cell_x, cell_y))
                pygame.draw.line(screen, get_rgb(self.points[i][j]), (cell_x*i, cell_y*j), (cell_x*i + 10*np.cos(self.points[i][j]), cell_y*j + 10*np.sin(self.points[i][j])), width=2)

def get_rgb(theta):
    h = ((theta+3.9) % (2*np.pi)) / (2*np.pi)
    r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
    return (round(r * 255), round(g * 255), round(b * 255))