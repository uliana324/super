import time
import pygame
import random

import game_sprite
import player
import enemy
import music


WIN_WIDTH = 700
WIN_HEIGHT = 500

window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Shooter")

pygame.font.init()
font = pygame.font.Font(None, 36)

background = pygame.transform.scale(pygame.image.load("img/galaxy.jpg"), (WIN_WIDTH, WIN_HEIGHT))
ship = player.Player("img/rocket.png", 5, WIN_HEIGHT-100, 80, 100, 10, (WIN_WIDTH, WIN_HEIGHT))

enemys = []
for _ in range(3):
    enemys.append(
        enemy.Enemy(
            "img/ufo.png", 
            random.randint(80, WIN_WIDTH-80), 
            -50, 
            80, 
            50, 
            random.randint(1, 5), 
            (WIN_WIDTH, WIN_HEIGHT)
            ))
    
boss = enemy.Boss(
    "img/ufo_boss.png",
    50,
    0,
    120,
    120,
    5,
    (WIN_WIDTH, WIN_HEIGHT)
)
    
bullets = pygame.sprite.Group()
ult = None
finish = False
game = True
lost = 0
score = 0
boss_fight = 10
timer = time.time()
gun_time = time.time()
gun_bullet = 0
reload_flag = False
boss_timer = time.time()
boss_rocket = []
asteroids = []

while game:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if reload_flag:
                    if time.time() - gun_time >= 3:
                        reload_flag = False
                else:
                    gun_bullet += 1
                    bullets.add(ship.fire())
                    music.fire_sound.play()
                    if gun_bullet >= 5:
                        gun_bullet = 0
                        reload_flag = True
                        gun_time = time.time()

            elif event.key == pygame.K_e:
                if time.time() - timer > 5:
                    ult = ship.ult()
                    music.fire_sound.play()
                    timer = time.time()
    
    if not finish:
        window.blit(background, (0, 0))
        pygame.draw.line(window, (130, 130, 130), (10, 10), (110, 10), 20)
        pygame.draw.line(window, (255, 0, 0), (10, 10), (ship.hp + 10, 10), 20)

        if reload_flag:
            window.blit(
                    font.render(f"Reload: {int(time.time()- gun_time)}/3", 1, (255, 255, 255)), 
                    (10, 80))

        ship.update()
        bullets.update()

        window.blit(*ship.draw())

        if not asteroids:
            for _ in range(3):
                asteroids.append(enemy.Enemy("img/asteroid.png", 
                                 random.randint(80, WIN_WIDTH-80), 
                                 -50, 
                                 80, 
                                 50, 
                                 random.randint(1, 5), 
                                 (WIN_WIDTH, WIN_HEIGHT)
                                ))
        
        for asteroid in asteroids[:]:
            if asteroid.rect.colliderect(ship.rect):
                ship.hp -= 15
            if asteroid.update():
                asteroids.remove(asteroid)
            window.blit(*asteroid.draw())

        ### Boss fight
        if score >= 10:
            pygame.draw.line(window, (130, 130, 130), (200, 10), (500+100, 10), 20)
            pygame.draw.line(window, (255, 0, 0), (200, 10), (boss.hp+100, 10), 20)
            boss.update()
            window.blit(*boss.draw())

            if time.time() - boss_timer >= 5:
                boss_rocket = boss.fire_rockets(ship.rect)
                boss_timer = time.time()

            for rocket in boss_rocket[:]:
                rocket.update()
                window.blit(*rocket.draw())
                if rocket.rect.colliderect(ship.rect):
                    ship.hp -= 25
                if rocket.rect.top > WIN_HEIGHT:
                    boss_rocket.clear()
             

            for bullet in bullets:
                window.blit(*bullet.draw())
                if bullet.rect.colliderect(boss.rect):
                    boss.hp -= 10
                    bullet.kill()
            if ult:
                window.blit(*ult.draw())
                flag = ult.update(boss.rect)
                if flag == "dist":
                    boss.hp -= 100
                    ult = None
                
            if boss.hp <= 0:
                window.blit(
                font.render(f"WIN!!!", 1, (255, 255, 255)), 
                (WIN_WIDTH // 2 - 40, WIN_HEIGHT // 2))
                window.blit(
                font.render(f"Ты пропустил {lost} зефирок на землю", 1, (255, 255, 255)), 
                (WIN_WIDTH // 2 - 140, WIN_HEIGHT // 2 + 30))
                finish = True
            
            if ship.hp <= 0:
                window.blit(
                font.render(f"Проиграл!!!", 1, (255, 255, 255)), 
                (WIN_WIDTH // 2 - 40, WIN_HEIGHT // 2))
                window.blit(
                font.render(f"Ты пропустил {lost} зефирок на землю", 1, (255, 255, 255)), 
                (WIN_WIDTH // 2 - 140, WIN_HEIGHT // 2 + 30))
                finish = True

        ### Main fight
        else:
            for monster in enemys:
                window.blit(*monster.draw())
                if monster.update():
                    lost += 1
                    ship.hp -= 10

            for bullet in bullets:
                window.blit(*bullet.draw())
                for monster in enemys[:]:
                    if bullet.rect.colliderect(monster.rect):
                        enemys.remove(monster)
                        score += 1
                        bullet.kill()

            window.blit(
                font.render(f"Пропущенно: {lost}", 1, (255, 255, 255)), 
                (10, 20))
            window.blit(
                font.render(f"Счёт: {score}", 1, (255, 255, 255)), 
                (10, 50))

            if ship.hp <= 0:
                window.blit(
                font.render(f"Проиграл!!!", 1, (255, 255, 255)), 
                (WIN_WIDTH // 2 - 40, WIN_HEIGHT // 2))
                window.blit(
                font.render(f"Ты пропустил {lost} зефирок на землю", 1, (255, 255, 255)), 
                (WIN_WIDTH // 2 - 140, WIN_HEIGHT // 2 + 30))
                finish = True

            if len(enemys) < 6:
                enemys.append(
                    enemy.Enemy(
                        "img/ufo.png", 
                        random.randint(80, WIN_WIDTH-80), 
                        -50, 
                        80, 
                        50, 
                        random.randint(1, 5), 
                        (WIN_WIDTH, WIN_HEIGHT)
                        ))

        pygame.display.update()
    pygame.time.delay(50)
