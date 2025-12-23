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
    def __init__(self, x, y, vy, vx=0, is_player_bullet=True, color=WHITE):
        super().__init__()
        size = 10 if is_player_bullet else 8
        self.image = pygame.Surface((size, size))
        
        if is_player_bullet:
            self.image.fill(color)
        else:
            pygame.draw.circle(self.image, RED, (size//2, size//2), size//2)
            self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vy = vy
        self.vx = vx

    def update(self):
        self.rect.y += self.vy
        self.rect.x += self.vx
        if self.rect.bottom < -50 or self.rect.top > SCREEN_HEIGHT + 50 or \
           self.rect.left < -50 or self.rect.right > SCREEN_WIDTH + 50:
            self.kill()

class Player(pygame.sprite.Sprite):
    """自機の親クラス（共通機能）"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30)) 
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed = 5
        self.last_shot_time = 0
        self.shoot_interval = 80
    
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

    def shoot(self):
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
        self.speed = 8
        self.shoot_interval = 80 

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_interval:
            bullet_centers = [0, -15, 15] 
            for angle in bullet_centers:
                rad = math.radians(angle)
                vx = math.sin(rad) * 10
                vy = -math.cos(rad) * 10
                bullet = Bullet(self.rect.centerx, self.rect.top, vy, vx, is_player_bullet=True, color=(255, 100, 100))
                all_sprites.add(bullet)
                player_bullets.add(bullet)
            self.last_shot_time = now

class PlayerShotgun(Player):
    """Type C: ショットガン型"""
    def __init__(self):
        super().__init__()
        self.image.fill(GREEN)
        self.speed = 4
        self.shoot_interval = 110

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_interval:
            bullet_angles = [-20, -10, 0, 10, 20]
            for angle in bullet_angles:
                rad = math.radians(angle)
                b_speed = 12
                vx = math.sin(rad) * b_speed
                vy = -math.cos(rad) * b_speed
                bullet = Bullet(self.rect.centerx, self.rect.top, vy, vx, is_player_bullet=True, color=YELLOW)
                all_sprites.add(bullet)
                player_bullets.add(bullet)
            self.last_shot_time = now

# ★★★ キャラクターリストの定義 ★★★
# ここに辞書を追加していくだけで、選択肢が増えます
CHAR_LIST = [
    {"name": "Type A: Balance", "desc": "バランス型", "color": BLUE,  "class": PlayerBalance},
    {"name": "Type B: Speed",   "desc": "高速移動型", "color": RED,   "class": PlayerSpeed},
    {"name": "Type C: Shotgun", "desc": "広範囲攻撃", "color": GREEN, "class": PlayerShotgun},
    # 例: {"name": "Type D: Power", "desc": "高火力", "color": PURPLE, "class": PlayerPower}, 
]


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
pygame.display.set_caption("シューティング")
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

player = None 

# ゲーム変数
score = 0
next_boss_score = BOSS_APPEAR_INTERVAL
boss_level = 1
is_boss_active = False

# ★インデックスで管理
selected_char_idx = 0 

GAME_STATE_TITLE = 0
GAME_STATE_SELECT = 1
GAME_STATE_PLAYING = 2
GAME_STATE_GAMEOVER = 3
current_state = GAME_STATE_TITLE

# --- 4. ゲームループ ---
running = True
while running:
    # --- イベント処理 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # ■ タイトル画面
        if current_state == GAME_STATE_TITLE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    current_state = GAME_STATE_SELECT
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # ■ キャラ選択画面 (ここを大きく変更)
        elif current_state == GAME_STATE_SELECT:
            if event.type == pygame.KEYDOWN:
                # ★ 左キー: インデックスを一つ戻す（余り計算でループ）
                if event.key == pygame.K_LEFT:
                    selected_char_idx = (selected_char_idx - 1) % len(CHAR_LIST)
                
                # ★ 右キー: インデックスを一つ進める（余り計算でループ）
                elif event.key == pygame.K_RIGHT:
                    selected_char_idx = (selected_char_idx + 1) % len(CHAR_LIST)
                
                # 決定
                elif event.key == pygame.K_SPACE or event.key == pygame.K_z:
                    all_sprites.empty()
                    enemies.empty()
                    boss_group.empty()
                    player_bullets.empty()
                    enemy_bullets.empty()
                    
                    # ★ リストからクラスを取り出してインスタンス化
                    # これにより if文の分岐が不要になります
                    PlayerClass = CHAR_LIST[selected_char_idx]["class"]
                    player = PlayerClass()
                    
                    all_sprites.add(player)
                    
                    score = 0
                    next_boss_score = BOSS_APPEAR_INTERVAL
                    boss_level = 1
                    is_boss_active = False
                    current_state = GAME_STATE_PLAYING
                if event.key == pygame.K_ESCAPE:
                    current_state = GAME_STATE_TITLE # 戻る

        # ■ ゲームオーバー画面
        elif current_state == GAME_STATE_GAMEOVER:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                current_state = GAME_STATE_TITLE

    # --- 更新処理 ---
    if current_state == GAME_STATE_PLAYING:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_z]:
            player.shoot()

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

        hits = pygame.sprite.groupcollide(enemies, player_bullets, True, True)
        for hit in hits:
            score += 10

        if is_boss_active:
            boss_hits = pygame.sprite.groupcollide(boss_group, player_bullets, False, True)
            for boss_sprite, bullets in boss_hits.items():
                for b in bullets:
                    boss_sprite.hp -= 1
                    score += 1
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
        
        # ★ リストから現在の選択中のデータを取得
        char_data = CHAR_LIST[selected_char_idx]

        # 中央にプレビュー表示
        preview_rect = pygame.Rect(0, 0, 100, 100)
        preview_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)
        pygame.draw.rect(screen, char_data["color"], preview_rect)
        pygame.draw.rect(screen, WHITE, preview_rect, 3) # 枠線

        # 名前と説明の表示
        name_text = font.render(char_data["name"], True, WHITE)
        desc_text = small_font.render(char_data["desc"], True, (200, 200, 200))
        
        screen.blit(name_text, (SCREEN_WIDTH//2 - name_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        screen.blit(desc_text, (SCREEN_WIDTH//2 - desc_text.get_width()//2, SCREEN_HEIGHT//2 + 100))

        # 左右の矢印ナビゲーション
        arrow_left = font.render("<", True, YELLOW)
        arrow_right = font.render(">", True, YELLOW)
        screen.blit(arrow_left, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 50))
        screen.blit(arrow_right, (SCREEN_WIDTH//2 + 120, SCREEN_HEIGHT//2 - 50))

        # ページ番号 (例: 1/3)
        page_text = small_font.render(f"{selected_char_idx + 1} / {len(CHAR_LIST)}", True, (100, 100, 100))
        screen.blit(page_text, (SCREEN_WIDTH//2 - page_text.get_width()//2, SCREEN_HEIGHT//2 + 150))

        guide_text = small_font.render("← → で変更 / Z or SPACE で決定", True, YELLOW)
        screen.blit(guide_text, (SCREEN_WIDTH//2 - guide_text.get_width()//2, SCREEN_HEIGHT - 80))

    elif current_state == GAME_STATE_PLAYING:
        all_sprites.draw(screen)
        score_text = small_font.render(f"スコア: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        if not is_boss_active:
            next_text = small_font.render(f"ボスまで: {next_boss_score - score}", True, YELLOW)
            screen.blit(next_text, (10, 40))
        if is_boss_active:
            for b in boss_group:
                pygame.draw.rect(screen, RED, (100, 20, 400, 20))
                hp_ratio = b.hp / b.max_hp
                pygame.draw.rect(screen, GREEN, (100, 20, 400 * hp_ratio, 20))
                pygame.draw.rect(screen, WHITE, (100, 20, 400, 20), 2)
                hp_text = small_font.render(f"Boss HP: {b.hp}", True, WHITE)
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