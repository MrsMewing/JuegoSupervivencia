import pygame
import random
import sys
import math

# Configuración
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 5
ENEMY_SPEED = 2
ENERGY_CAPSULES = 5
NIGHTS_TO_SURVIVE = 5
NIGHT_DURATION = 30  # segundos

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Explorador: Supervivencia Galáctica")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)


fuente = pygame.font.Font(None, 35)

# Clases
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.energy = 100

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
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

class Bullet(pygame.sprite.Sprite):
    def __init__(self, position_player, position_mouse):
        super().__init__()
        self.image = pygame.Surface((7, 7))
        self.image.fill(WHITE)

        #posicion inicial del la bala
        self.rect = self.image.get_rect(center = (position_player[0] + 20, position_player[1] + 20)) #posiciona la bala justo en medio del personaje, que es de ahi de donde saldra

        #configuracion de bala
        self.speed = 5

        #calcula la direccion de hacia donde se va a mover la bala
        self.direction_x = position_mouse[0] - position_player[0]
        self.direction_y = position_mouse[1] - position_player[1]

        self.magnitud = math.sqrt(self.direction_x**2 + self.direction_y**2)

        self.dx = self.direction_x / self.magnitud
        self.dy = self.direction_y / self.magnitud

    def update(self):
        #verifica que la bala este dentro de la pantalla y no se haya salido
        if (self.rect.x >= 0 and self.rect.x <= WIDTH) and (self.rect.y >= 0 and self.rect.y <= HEIGHT):

            self.rect.x += self.dx * self.speed
            self.rect.y += self.dy * self.speed
        
        #si se salio de la pantalla eliminalo del grupo
        else: self.kill()

class Ammunition(pygame.sprite.Sprite):
    def __init__(self, ):
        super().__init__()
        self.image = pygame.surface.Surface((20, 20))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect(center=(random.randint(40, WIDTH-40), random.randint(40, HEIGHT-40)))
        self.creation_time = pygame.time.get_ticks() #obtiene el tiempo en el que creo la municion
        self.lifetime = 2000 #2 segundos sera el tiempo en que estara vivo la municion

    def update(self):
        current_weather = pygame.time.get_ticks()
        if current_weather - self.creation_time  >= self.lifetime:
            self.kill()

# Grupos de sprites
player = Player()
player_group = pygame.sprite.Group(player)
enemies = pygame.sprite.Group()
capsules = pygame.sprite.Group()
balas = pygame.sprite.Group()
ammunitions = pygame.sprite.Group()

def spawn_capsules():
    capsules.empty()
    for _ in range(ENERGY_CAPSULES):
        capsules.add(EnergyCapsule())

def spawn_ammunition():
    ammunitions.add(Ammunition())

def spawn_enemy():
    enemies.add(Enemy())

def draw_hud(night, time_left, energy):
    text = font.render(f"Noche: {night}/{NIGHTS_TO_SURVIVE}  Tiempo: {int(time_left)}s  Energía: {int(energy)}", True, WHITE)
    screen.blit(text, (10, 10))

def draw_available_bullets(texto):    
    texto_renderizado = fuente.render(texto, True, WHITE)
    screen.blit(texto_renderizado, (10, 550))

def game_over_screen(win):
    screen.fill(BLACK)
    msg = "¡Rescate exitoso!" if win else "¡Has muerto!"
    text = font.render(msg, True, GREEN if win else RED)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 20))
    pygame.display.flip()
    pygame.time.wait(3000)

# Juego principal
def main():
    balas_disponibles = 5
    night = 1
    time_left = NIGHT_DURATION
    spawn_capsules()
    enemy_spawn_timer = 0
    ammunition_spawn_timer = 0
    running = True
    win = False

    while running:
        dt = clock.tick(FPS) / 1000
        time_left -= dt
        enemy_spawn_timer += dt
        ammunition_spawn_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                #verifica si se presiono el espacio o el boton derecho del mouse
                if event.key == pygame.K_SPACE and balas_disponibles > 0: 
                    pos_mouse = pygame.mouse.get_pos()
                    
                    nueva_bala = Bullet(player.rect, pos_mouse)
                    balas.add(nueva_bala)
                    balas_disponibles -= 1
            
            if event.type == pygame.MOUSEBUTTONDOWN and balas_disponibles > 0:
                if event.button == 1:
                    pos_mouse = pygame.mouse.get_pos()

                    nueva_bala = Bullet(player.rect, pos_mouse)
                    balas.add(nueva_bala)
                    balas_disponibles -= 1

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

        # Colision de balas con enemigos
        pygame.sprite.groupcollide(balas, enemies, True, True)

        colision_entre_jugador_y_enemigo = pygame.sprite.spritecollide(player, ammunitions, True)
        if colision_entre_jugador_y_enemigo:
            if balas_disponibles < 5:
                balas_disponibles = 5
        
        #balas se mueven hacia la direccion del cursor
        for bullet in balas:
            bullet.update()

        # Enemigos persiguen al jugador
        for enemy in enemies:
            enemy.update(player.rect.center)

        for ammunition in ammunitions:
            ammunition.update()

        # Spawnea enemigos cada 2 segundos
        if enemy_spawn_timer > 2:
            spawn_enemy()
            enemy_spawn_timer = 0

        #Spawnea municiones cada 3 segundos
        if ammunition_spawn_timer > 3:
            spawn_ammunition()
            ammunition_spawn_timer = 0

        # Si se acaban las cápsulas, respawnea
        if len(capsules) == 0:
            spawn_capsules()

        # Noche completada
        if time_left <= 0:
            night += 1
            time_left = NIGHT_DURATION
            enemies.empty()
            spawn_capsules()
            balas_disponibles = 5
            player.energy = min(100, player.energy + 50)
            if night > NIGHTS_TO_SURVIVE:
                win = True
                running = False

        # Dibujar
        screen.fill(BLACK)
        capsules.draw(screen)
        enemies.draw(screen)
        player_group.draw(screen)
        balas.draw(screen)
        ammunitions.draw(screen)
        draw_hud(night, time_left, player.energy)

        if balas_disponibles == 0: 
            draw_available_bullets(f"Recargando balas...")
        else: draw_available_bullets(f"Balas disponibles {balas_disponibles}")

        pygame.display.flip()

    game_over_screen(win)

if __name__ == "__main__":
    main()