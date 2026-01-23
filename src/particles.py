import pygame
import random

class Particle:
    def __init__(self, x, y, color, size, life):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        # Random velocity
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, -1.5) # Tend upwards

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.05) # Shrink over time

    def draw(self, screen, camera):
        if self.life > 0:
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)
            # Fade out alpha
            alpha = int((self.life / self.max_life) * 255)
            s = pygame.Surface((int(self.size * camera.zoom_level), int(self.size * camera.zoom_level)), pygame.SRCALPHA)
            s.fill((*self.color, alpha))
            screen.blit(s, (screen_x, screen_y))

class ParticleManager:
    def __init__(self):
        self.particles = []

    def spawn_particle(self, x, y, color, size=0.5, life=60):
        p = Particle(x, y, color, size, life)
        self.particles.append(p)

    def update(self):
        # Update and keep alive particles
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, screen, camera):
        for p in self.particles:
            p.draw(screen, camera)
