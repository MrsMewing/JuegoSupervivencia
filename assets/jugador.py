import pygame

class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y, ancho=50, alto=50, color=(0, 128, 255)):
        super().__init__()
        self.image = pygame.Surface((ancho, alto))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.velocidad = 5

    def update(self, teclas):
        if teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidad
        if teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidad
        if teclas[pygame.K_UP]:
            self.rect.y -= self.velocidad
        if teclas[pygame.K_DOWN]:
            self.rect.y += self.velocidad