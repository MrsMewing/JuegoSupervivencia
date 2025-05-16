import pygame
import random
import sys

# Configuración
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 5
ENEMY_SPEED = 2
ENERGY_CAPSULES = 5
NIGHTS_TO_SURVIVE = 3
NIGHT_DURATION = 30  # segundos

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Explorador: Supervivencia Galáctica")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Clases
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.energy = 100

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.rect.y += PLAYER_SPEED
        self.rect.clamp_ip(screen.get_rect())

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        # Aparece en un borde aleatorio
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), 0))
        elif side == 'bottom':
            self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), HEIGHT))
        elif side == 'left':
            self.rect = self.image.get_rect(center=(0, random.randint(0, HEIGHT)))
        else:
            self.rect = self.image.get_rect(center=(WIDTH, random.randint(0, HEIGHT)))
        self.speed = ENEMY_SPEED

    def update(self, player_pos):
        dx, dy = player_pos[0] - self.rect.centerx, player_pos[1] - self.rect.centery
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        self.rect.x += int(self.speed * dx / dist)
        self.rect.y += int(self.speed * dy / dist)

class EnergyCapsule(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(random.randint(40, WIDTH-40), random.randint(40, HEIGHT-40)))

# Grupos de sprites
player = Player()
player_group = pygame.sprite.Group(player)
enemies = pygame.sprite.Group()
capsules = pygame.sprite.Group()

def spawn_capsules():
    capsules.empty()
    for _ in range(ENERGY_CAPSULES):
        capsules.add(EnergyCapsule())

def spawn_enemy():
    enemies.add(Enemy())

def draw_hud(night, time_left, energy):
    text = font.render(f"Noche: {night}/{NIGHTS_TO_SURVIVE}  Tiempo: {int(time_left)}s  Energía: {int(energy)}", True, WHITE)
    screen.blit(text, (10, 10))

def game_over_screen(win):
    screen.fill(BLACK)
    msg = "¡Rescate exitoso!" if win else "¡Has muerto!"
    text = font.render(msg, True, GREEN if win else RED)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 20))
    pygame.display.flip()
    pygame.time.wait(3000)

# Juego principal
def main():
    night = 1
    time_left = NIGHT_DURATION
    spawn_capsules()
    enemy_spawn_timer = 0
    running = True
    win = False

    while running:
        dt = clock.tick(FPS) / 1000
        time_left -= dt
        enemy_spawn_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        player.update(keys)

        # Energía baja con el tiempo
        player.energy -= 10 * dt
        if player.energy <= 0:
            running = False
            break

        # Colisiones con cápsulas
        hits = pygame.sprite.spritecollide(player, capsules, True)
        for _ in hits:
            player.energy = min(100, player.energy + 30)

        # Colisiones con enemigos
        if pygame.sprite.spritecollideany(player, enemies):
            running = False
            break

        # Enemigos persiguen al jugador
        for enemy in enemies:
            enemy.update(player.rect.center)

        # Spawnea enemigos cada 2 segundos
        if enemy_spawn_timer > 2:
            spawn_enemy()
            enemy_spawn_timer = 0

        # Si se acaban las cápsulas, respawnea
        if len(capsules) == 0:
            spawn_capsules()

        # Noche completada
        if time_left <= 0:
            night += 1
            time_left = NIGHT_DURATION
            enemies.empty()
            spawn_capsules()
            player.energy = min(100, player.energy + 50)
            if night > NIGHTS_TO_SURVIVE:
                win = True
                running = False

        # Dibujar
        screen.fill(BLACK)
        capsules.draw(screen)
        enemies.draw(screen)
        player_group.draw(screen)
        draw_hud(night, time_left, player.energy)
        pygame.display.flip()

    game_over_screen(win)

if __name__ == "__main__":
    main()