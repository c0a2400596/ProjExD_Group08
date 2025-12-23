import pygame
import sys
import os
import random
import math

# --- 1. 定数定義 ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60

# 色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# 敵の種類
ENEMY_TYPE_NORMAL = 0
ENEMY_TYPE_WAVY = 1
ENEMY_TYPE_SHOOTER = 2

# ボス出現スコア間隔
BOSS_APPEAR_INTERVAL = 150

# --- 2. 必須設定 ---
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- クラス定義 ---

class Bullet(pygame.sprite.Sprite):
    """弾クラス"""
    # is_melee フラグを追加：これがTrueなら敵弾を消せる
    def __init__(self, x, y, vy, vx=0, is_player_bullet=True, color=WHITE, size=None, life=None, is_melee=False):
        super().__init__()
        if size is None:
            base_size = 10 if is_player_bullet else 8
        else:
            base_size = size
            
        self.image = pygame.Surface((base_size, base_size))
        self.life = life
        self.is_melee = is_melee # 近接攻撃フラグ

        if is_player_bullet:
            self.image.fill(color)
        else:
            pygame.draw.circle(self.image, RED, (base_size//2, base_size//2), base_size//2)
            self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vy = vy
        self.vx = vx

    def update(self):
        self.rect.y += self.vy
        self.rect.x += self.vx
        
        if self.life is not None:
            self.life -= 1
            if self.life <= 0:
                self.kill()

        if self.rect.bottom < -50 or self.rect.top > SCREEN_HEIGHT + 50 or \
           self.rect.left < -50 or self.rect.right > SCREEN_WIDTH + 50:
            self.kill()

class SpecialBlast(pygame.sprite.Sprite):
    """必殺技：衝撃波クラス"""
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.radius = 10
        self.max_radius = 150 
        self.growth_speed = 10
        self.image = pygame.Surface((self.max_radius*2, self.max_radius*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = player.rect.center
        self.damage = 5

    def update(self):
        self.rect.center = self.player.rect.center
        if self.radius < self.max_radius:
            self.radius += self.growth_speed
        
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, (255, 200, 0, 150), (self.max_radius, self.max_radius), self.radius)
        pygame.draw.circle(self.image, (255, 255, 255, 200), (self.max_radius, self.max_radius), self.radius, 5)

        if self.radius >= self.max_radius:
            self.radius += 1
            if self.radius > self.max_radius + 20:
                self.kill()

class Player(pygame.sprite.Sprite):
    """自機の親クラス"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed = 5
        self.last_shot_time = 0
        self.shoot_interval = 80
        
        self.special_gauge = 0
        self.special_max = 100
        self.special_charge_rate = 0.2
    
    def update(self):
        keys = pygame.key.get_pressed()
        current_speed = self.speed
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            current_speed = self.speed / 2

        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= current_speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += current_speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= current_speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += current_speed

        if self.special_gauge < self.special_max:
            self.special_gauge += self.special_charge_rate
            if self.special_gauge > self.special_max:
                self.special_gauge = self.special_max

    def shoot(self):
        pass

    def trigger_special(self):
        pass

class PlayerBalance(Player):
    """Type A: バランス型"""
    def __init__(self):
        super().__init__()
        self.image.fill(BLUE)
        self.speed = 5
        self.shoot_interval = 80

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_interval:
            bullet_centers = [0, -15, 15]
            for angle in bullet_centers:
                rad = math.radians(angle)
                vx = math.sin(rad) * 10
                vy = -math.cos(rad) * 10
                bullet = Bullet(self.rect.centerx, self.rect.top, vy, vx, is_player_bullet=True, color=CYAN)
                all_sprites.add(bullet)
                player_bullets.add(bullet)
            self.last_shot_time = now

class PlayerSpeed(Player):
    """Type B: 高速移動型"""
    def __init__(self):
        super().__init__()
        self.image.fill(RED)
        self.speed = 9
        self.shoot_interval = 70

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_interval:
            bullet_centers = [0, -20, 20, -10, 10]
            for angle in bullet_centers:
                rad = math.radians(angle)
                vx = math.sin(rad) * 12
                vy = -math.cos(rad) * 12
                bullet = Bullet(self.rect.centerx, self.rect.top, vy, vx, is_player_bullet=True, color=(255, 100, 100))
                all_sprites.add(bullet)
                player_bullets.add(bullet)
            self.last_shot_time = now

class PlayerMelee(Player):
    """Type C: 近接型"""
    def __init__(self):
        super().__init__()
        
        try:
            image_path = "Gemini_Generated_Image_5a8oni5a8oni5a8o.png"
            original_image = pygame.image.load(image_path).convert_alpha()
            threshold = 200
            width, height = original_image.get_size()
            original_image.lock()
            for x in range(width):
                for y in range(height):
                    r, g, b, a = original_image.get_at((x, y))
                    if r > threshold and g > threshold and b > threshold:
                        original_image.set_at((x, y), (255, 255, 255, 0))
            original_image.unlock()
            
            rect = original_image.get_bounding_rect()
            if rect.width > 0 and rect.height > 0:
                cropped_image = original_image.subsurface(rect)
                self.image = pygame.transform.smoothscale(cropped_image, (50, 50))
            else:
                self.image = pygame.transform.smoothscale(original_image, (50, 50))
        except Exception as e:
            print(f"画像読み込み失敗: {e}")
            self.image.fill(GREEN)
            
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)

        self.speed = 6
        self.shoot_interval = 15
        
        self.special_gauge = 100
        self.special_max = 100
        self.special_charge_rate = 0.15

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_interval:
            # is_melee=True を指定して、敵弾を消せるようにする
            bullet = Bullet(self.rect.centerx, self.rect.top, -15, 0, 
                            is_player_bullet=True, color=YELLOW, size=20, life=15, is_melee=True)
            bullet_l = Bullet(self.rect.centerx - 15, self.rect.top + 10, -15, -2, 
                            is_player_bullet=True, color=YELLOW, size=15, life=10, is_melee=True)
            bullet_r = Bullet(self.rect.centerx + 15, self.rect.top + 10, -15, 2, 
                            is_player_bullet=True, color=YELLOW, size=15, life=10, is_melee=True)

            all_sprites.add(bullet, bullet_l, bullet_r)
            player_bullets.add(bullet, bullet_l, bullet_r)
            self.last_shot_time = now

    def trigger_special(self):
        if self.special_gauge >= self.special_max:
            self.special_gauge = 0
            blast = SpecialBlast(self)
            all_sprites.add(blast)
            special_group.add(blast)

class Enemy(pygame.sprite.Sprite):
    """ザコ敵クラス"""
    def __init__(self, enemy_type):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = pygame.Surface((30, 30))
        
        if self.enemy_type == ENEMY_TYPE_NORMAL:
            self.image.fill(RED)
            self.speed_y = 3
        elif self.enemy_type == ENEMY_TYPE_WAVY:
            self.image.fill(GREEN)
            self.speed_y = 2
            self.t = 0
        elif self.enemy_type == ENEMY_TYPE_SHOOTER:
            self.image.fill(YELLOW)
            self.speed_y = 1
            self.shoot_timer = 0

        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = -50

    def update(self):
        self.rect.y += self.speed_y

        if self.enemy_type == ENEMY_TYPE_WAVY:
            self.t += 0.1
            self.rect.x += math.sin(self.t) * 5
        elif self.enemy_type == ENEMY_TYPE_SHOOTER:
            self.shoot_timer += 1
            if self.shoot_timer > 120:
                self.shoot_at_player()
                self.shoot_timer = 0

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def shoot_at_player(self):
        if player: 
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            angle = math.atan2(dy, dx)
            speed = 5
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            bullet = Bullet(self.rect.centerx, self.rect.centery, vy, vx, is_player_bullet=False)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

class Boss(pygame.sprite.Sprite):
    """ボスクラス"""
    def __init__(self, level=1):
        super().__init__()
        self.image = pygame.Surface((60, 60))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, -100)
        
        self.max_hp = 100 * level
        self.hp = self.max_hp
        self.state = "entry"
        self.angle = 0
        self.timer = 0

    def update(self):
        if self.state == "entry":
            self.rect.y += 2
            if self.rect.y >= 100:
                self.state = "battle"
        
        elif self.state == "battle":
            self.timer += 1
            self.rect.x = (SCREEN_WIDTH // 2) + math.sin(self.timer * 0.05) * 150
            
            if self.timer % 5 == 0:
                self.shoot_danmaku()

    def shoot_danmaku(self):
        self.angle += 12
        bullet_speed = 4
        for i in range(0, 360, 90):
            theta = math.radians(self.angle + i)
            vx = math.cos(theta) * bullet_speed
            vy = math.sin(theta) * bullet_speed
            bullet = Bullet(self.rect.centerx, self.rect.centery, vy, vx, is_player_bullet=False)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

# --- 3. ゲーム初期化 ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("東方風シューティング")
clock = pygame.time.Clock()

try:
    font = pygame.font.SysFont("meiryo", 40)
    small_font = pygame.font.SysFont("meiryo", 24)
except:
    font = pygame.font.Font(None, 40)
    small_font = pygame.font.Font(None, 24)

all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
special_group = pygame.sprite.Group()

player = None 
score = 0
next_boss_score = BOSS_APPEAR_INTERVAL
boss_level = 1
is_boss_active = False
selected_char_idx = 0 

GAME_STATE_TITLE = 0
GAME_STATE_SELECT = 1
GAME_STATE_PLAYING = 2
GAME_STATE_GAMEOVER = 3
current_state = GAME_STATE_TITLE

# --- 4. ゲームループ ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if current_state == GAME_STATE_TITLE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    current_state = GAME_STATE_SELECT 
                elif event.key == pygame.K_ESCAPE:
                    running = False

        elif current_state == GAME_STATE_SELECT:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_char_idx = (selected_char_idx - 1) % 3
                if event.key == pygame.K_RIGHT:
                    selected_char_idx = (selected_char_idx + 1) % 3
                
                if event.key == pygame.K_SPACE or event.key == pygame.K_z:
                    all_sprites.empty()
                    enemies.empty()
                    boss_group.empty()
                    player_bullets.empty()
                    enemy_bullets.empty()
                    special_group.empty()
                    
                    if selected_char_idx == 0:
                        player = PlayerBalance()
                    elif selected_char_idx == 1:
                        player = PlayerSpeed()
                    else: 
                        player = PlayerMelee()
                        
                    all_sprites.add(player)
                    
                    score = 0
                    next_boss_score = BOSS_APPEAR_INTERVAL
                    boss_level = 1
                    is_boss_active = False
                    current_state = GAME_STATE_PLAYING
                if event.key == pygame.K_ESCAPE:
                    current_state = GAME_STATE_TITLE

        elif current_state == GAME_STATE_GAMEOVER:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                current_state = GAME_STATE_TITLE

    # --- 更新処理 ---
    if current_state == GAME_STATE_PLAYING:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_z]:
            player.shoot()
        
        if keys[pygame.K_x]:
            player.trigger_special()

        if not is_boss_active and score >= next_boss_score:
            is_boss_active = True
            boss = Boss(boss_level)
            all_sprites.add(boss)
            boss_group.add(boss)
            for e in enemies:
                score += 10
                e.kill()

        if not is_boss_active:
            if random.random() < 0.03: 
                t_type = random.choice([ENEMY_TYPE_NORMAL, ENEMY_TYPE_WAVY, ENEMY_TYPE_SHOOTER])
                enemy = Enemy(t_type)
                all_sprites.add(enemy)
                enemies.add(enemy)
        
        all_sprites.update()

        # 衝突判定：プレイヤー弾 vs 敵
        hits = pygame.sprite.groupcollide(enemies, player_bullets, True, True)
        for hit in hits:
            score += 10

        # ★★★ 追加機能：近接攻撃（斬撃）で敵の弾を消す ★★★
        # 全てのプレイヤー弾を確認
        for bullet in player_bullets:
            # もし「近接攻撃属性(is_melee)」を持っていたら
            if bullet.is_melee:
                # 敵弾との衝突判定（敵弾は消える=True, 自分の剣は消えない）
                hit_bullets = pygame.sprite.spritecollide(bullet, enemy_bullets, True)
                if hit_bullets:
                    score += 1 # 弾を切ったら少しスコアが入る

        # 衝突判定：必殺技 vs 敵弾/敵
        if len(special_group) > 0:
            pygame.sprite.groupcollide(special_group, enemy_bullets, False, True)
            hit_enemies = pygame.sprite.groupcollide(enemies, special_group, True, False)
            for e in hit_enemies:
                score += 20

        if is_boss_active:
            boss_hits = pygame.sprite.groupcollide(boss_group, player_bullets, False, True)
            for boss_sprite, bullets in boss_hits.items():
                for b in bullets:
                    boss_sprite.hp -= 1
                    score += 1
            
            if len(special_group) > 0:
                boss_blast_hits = pygame.sprite.groupcollide(boss_group, special_group, False, False)
                for boss_sprite, blasts in boss_blast_hits.items():
                    boss_sprite.hp -= 2
            
            for boss_sprite in boss_group:
                if boss_sprite.hp <= 0:
                    score += 1000
                    boss_sprite.kill()
                    is_boss_active = False
                    boss_level += 1
                    next_boss_score = score + BOSS_APPEAR_INTERVAL

        if pygame.sprite.spritecollide(player, enemies, False) or \
           pygame.sprite.spritecollide(player, enemy_bullets, False) or \
           pygame.sprite.spritecollide(player, boss_group, False):
            current_state = GAME_STATE_GAMEOVER

    # --- 描画処理 ---
    screen.fill(BLACK)

    if current_state == GAME_STATE_TITLE:
        title_text = font.render("東方風シューティング", True, WHITE)
        start_text = font.render("スペースキーで次へ", True, YELLOW)
        quit_text = small_font.render("ESCキーで終了", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, SCREEN_HEIGHT//2 + 100))

    elif current_state == GAME_STATE_SELECT:
        sel_title = font.render("キャラクター選択", True, WHITE)
        screen.blit(sel_title, (SCREEN_WIDTH//2 - sel_title.get_width()//2, 80))
        
        color_a = BLUE if selected_char_idx == 0 else (50, 50, 100)
        rect_a = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50, 80, 80)
        pygame.draw.rect(screen, color_a, rect_a)
        
        color_b = RED if selected_char_idx == 1 else (100, 50, 50)
        rect_b = pygame.Rect(SCREEN_WIDTH//2 - 40, SCREEN_HEIGHT//2 - 50, 80, 80)
        pygame.draw.rect(screen, color_b, rect_b)
        
        color_c = GREEN if selected_char_idx == 2 else (50, 100, 50)
        rect_c = pygame.Rect(SCREEN_WIDTH//2 + 120, SCREEN_HEIGHT//2 - 50, 80, 80)
        pygame.draw.rect(screen, color_c, rect_c)

        if selected_char_idx == 0:
            pygame.draw.rect(screen, YELLOW, rect_a, 5)
            desc_text = "Type A: バランス型"
            color_desc = BLUE
            skill_text = ""
        elif selected_char_idx == 1:
            pygame.draw.rect(screen, YELLOW, rect_b, 5)
            desc_text = "Type B: 高速移動型"
            color_desc = RED
            skill_text = ""
        else:
            pygame.draw.rect(screen, YELLOW, rect_c, 5)
            desc_text = "Type C: 近接型 (画像)"
            color_desc = GREEN
            skill_text = "必殺技(X): 衝撃波 / 通常攻撃で弾消し可能"

        info_text = font.render(desc_text, True, color_desc)
        screen.blit(info_text, (SCREEN_WIDTH//2 - info_text.get_width()//2, SCREEN_HEIGHT//2 + 60))
        
        if skill_text:
            s_text = small_font.render(skill_text, True, ORANGE)
            screen.blit(s_text, (SCREEN_WIDTH//2 - s_text.get_width()//2, SCREEN_HEIGHT//2 + 100))

        guide_text = small_font.render("← → で選択 / Z:決定 / X:必殺技(Cのみ)", True, YELLOW)
        screen.blit(guide_text, (SCREEN_WIDTH//2 - guide_text.get_width()//2, SCREEN_HEIGHT - 100))

    elif current_state == GAME_STATE_PLAYING:
        all_sprites.draw(screen)
        score_text = small_font.render(f"スコア: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        if isinstance(player, PlayerMelee):
            bar_width = 200
            bar_height = 20
            fill_width = int(bar_width * (player.special_gauge / player.special_max))
            bar_color = YELLOW if player.special_gauge < player.special_max else ORANGE
            pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH - bar_width - 20, SCREEN_HEIGHT - 40, bar_width, bar_height), 2)
            pygame.draw.rect(screen, bar_color, (SCREEN_WIDTH - bar_width - 20, SCREEN_HEIGHT - 40, fill_width, bar_height))
            skill_label = small_font.render("SPECIAL(X)", True, WHITE)
            screen.blit(skill_label, (SCREEN_WIDTH - bar_width - 20, SCREEN_HEIGHT - 70))

        if not is_boss_active:
            next_text = small_font.render(f"ボスまで: {next_boss_score - score}", True, YELLOW)
            screen.blit(next_text, (10, 40))
        if is_boss_active:
            for b in boss_group:
                pygame.draw.rect(screen, RED, (100, 20, 400, 20))
                hp_ratio = b.hp / b.max_hp
                if hp_ratio < 0: hp_ratio = 0
                pygame.draw.rect(screen, GREEN, (100, 20, 400 * hp_ratio, 20))
                pygame.draw.rect(screen, WHITE, (100, 20, 400, 20), 2)
                hp_text = small_font.render(f"Boss HP: {int(b.hp)}", True, WHITE)
                screen.blit(hp_text, (100, 45))

    elif current_state == GAME_STATE_GAMEOVER:
        over_text = font.render("ゲームオーバー", True, RED)
        score_res_text = font.render(f"最終スコア: {score}", True, WHITE)
        retry_text = small_font.render("Rキーでタイトルへ", True, WHITE)
        screen.blit(over_text, (SCREEN_WIDTH//2 - over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(score_res_text, (SCREEN_WIDTH//2 - score_res_text.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(retry_text, (SCREEN_WIDTH//2 - retry_text.get_width()//2, SCREEN_HEIGHT//2 + 50))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()