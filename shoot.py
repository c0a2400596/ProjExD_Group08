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

    """
    弾クラス（修正版）
    寿命(life)と近接属性(is_melee)を追加
    """
    def __init__(self, x:float, y:float, vy:float, vx:float=0, is_player_bullet:bool=True, color:tuple=WHITE, pierce:bool=False, damage:int=1, is_melee:bool=False, life:int=0, size:int=0) -> None:
        """
        弾の設定
        引数 x,y: 弾の座標
        引数 vx,vy: 弾の速度
        引数 is_player_bullet: プレイヤーの弾かどうか
        引数 color: 弾の色
        引数 pierce: 貫通判定の有無
        引数 damge: ボスに与えるダメージ量
        引数 is_melee: 近接キャラかどうか
        引数 size: 弾のサイズ
        引数 life: 弾の寿命
        """
        super().__init__()

        # sizeが指定されていなければデフォルト値を使う
        if size == 0:
            size = 10 if is_player_bullet else 8
            
        self.image = pygame.Surface((size, size))
        self.damage = damage
        self.pierce = pierce
        self.is_melee = is_melee # 近接攻撃かどうか
        self.life = life         # 寿命（フレーム数）。0なら無限（画面外まで）
        
        if is_player_bullet:
            # プレイヤー弾は引数で色を指定可能にする
            self.image.fill(color)
        else:
            # 敵弾は赤玉
            pygame.draw.circle(self.image, RED, (size//2, size//2), size//2)
            self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vy = vy
        self.vx = vx

    def update(self) -> None:
        """
        弾の移動処理と画面外削除、寿命管理
        """
        self.rect.y += self.vy
        self.rect.x += self.vx
        
        # 寿命がある弾（近接攻撃など）の処理
        if self.life > 0:
            self.life -= 1
            if self.life <= 0:
                self.kill() # 寿命が尽きたら消える

        # 画面外に出たら削除
        if self.rect.bottom < -50 or self.rect.top > SCREEN_HEIGHT + 50 or \
           self.rect.left < -50 or self.rect.right > SCREEN_WIDTH + 50:
            self.kill()

class Player(pygame.sprite.Sprite):
    """
    自機の親クラス（共通機能）
    """
    def __init__(self) -> None:
        """
        自機の共通機能の設定
        """
        super().__init__()
        self.image = pygame.Surface((30, 30)) 
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed = 5
        self.last_shot_time = 0
        self.shoot_interval = 80
    
    def update(self) -> None:
        """
        自機の移動処理の設定
        """
        keys = pygame.key.get_pressed()
        current_speed = self.speed
        # Shiftキーで低速移動
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


    def shoot(self) -> None:
        """
        子クラスでオーバーライド（上書き）するためのメソッド
        """

        pass

class PlayerBalance(Player):
    """
    Type A: バランス型(青)
    """
    def __init__(self) -> None:
        """
        バランス型の各種設定
        """
        super().__init__()
        self.image.fill(BLUE)
        self.speed = 5
        self.shoot_interval = 80

    def shoot(self) -> None:
        """
        バランス型の射撃機構
        """
        if not keys[pygame.K_z]:
            return
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_interval:
            # 3WAY弾 (シアン)
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
    """
    Type B: 高速移動型（赤）
    """
    def __init__(self) -> None:
        """
        高速移動型の各種設定
        """
        super().__init__()
        self.image.fill(RED)
        self.speed = 8
        self.shoot_interval = 80 

    def shoot(self) -> None:
        """
        高速移動型の射撃機構
        """
        if not keys[pygame.K_z]:
            return
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_interval:
            # 3WAY弾 (少し赤い白)
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
    """
    Type C: ショットガン型
    """
    def __init__(self) -> None:
        """
        ショットガン型の各種設定
        """
        super().__init__()
        self.image.fill(GREEN)
        self.speed = 4
        self.shoot_interval = 200
        image_path = "./fig/shot.png"
        
        try:
            raw_image = pygame.image.load(image_path).convert()
            
            # リサイズする
            target_size = (50, 50)
            scaled_image = pygame.transform.scale(raw_image, target_size)
            
            # 3. アルファ付きに変換
            self.image = scaled_image.convert_alpha()
            bg_color = self.image.get_at((0, 0))
            
            # 色の許容範囲 (Threshold)
            # この数値を大きくすると、より広い範囲の色が消えます。
            threshold = 60 
            
            width, height = self.image.get_size()
            for x in range(width):
                for y in range(height):
                    # 現在のピクセルの色を取得
                    c = self.image.get_at((x, y))
                    diff = abs(c.r - bg_color.r) + abs(c.g - bg_color.g) + abs(c.b - bg_color.b)
                    
                    if diff < threshold:
                        # 差が許容範囲内なら、完全に透明にする (R,G,B,Alpha)
                        self.image.set_at((x, y), (0, 0, 0, 0))
            
        except FileNotFoundError:
            print(f"画像ファイル {image_path} が見つかりません。緑色の矩形を使用します。")
            self.image = pygame.Surface((30, 30))
            self.image.fill(GREEN)
        
        # --- マスクの作成 ---
        # 透明部分を無視した正確な衝突判定用マスクを作成
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        super().__init__()
        self.image.fill(GREEN)
        
        self.speed = 4
        self.shoot_interval = 200

    def shoot(self) -> None:
        """
        ショットガン型の射撃機構
        """
        if not keys[pygame.K_z]:
            return
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_interval:
            bullet_angles = [-20, -15, -10, -5, 0, 5, 10, 15, 20]
            for angle in bullet_angles:
                rad = math.radians(angle)
                b_speed = 12
                vx = math.sin(rad) * b_speed
                vy = -math.cos(rad) * b_speed
                bullet = Bullet(self.rect.centerx, self.rect.top, vy, vx, is_player_bullet=True, color=GREEN)
                all_sprites.add(bullet)
                player_bullets.add(bullet)
            self.last_shot_time = now


class PlayerReimu(Player):
    """
    Type D: 博麗霊夢風のホーミング（誘導）機体
    最も近い敵を自動で索敵し、追尾する弾を発射する。
    """
    def __init__(self) -> None:
        """
        コンストラクタ
        機体の色や速度、弾の連射速度を初期化する。
        """
        super().__init__()
        self.image.fill(WHITE)
        self.speed: int = 5            # 標準速度
        self.shoot_interval: int = 120 # 誘導弾は強力なので連射は遅めに設定

    def shoot(self) -> None:
        """
        最も近い敵に向かって誘導弾を発射する。
        敵がいない場合は真上に発射する。
        """
        if not keys[pygame.K_z]:
            return
        now = pygame.time.get_ticks()
        # 前回の発射から一定時間経過しているか確認
        if now - self.last_shot_time > self.shoot_interval:
            # 左右の少しズレた位置から2発発射するためのオフセット
            offsets = [-15, 15]
            for offset_x in offsets:
                # 画面内で最も近い敵を取得するメソッドを呼ぶ
                target: Enemy | None = self.get_nearest_enemy()
                
                angle: float = 0.0
                if target:
                    # 敵がいる場合：敵の方向への角度(ラジアン)を計算
                    # atan2(yの差分, xの差分) で角度が求まる
                    dx = target.rect.centerx - (self.rect.centerx + offset_x)
                    dy = target.rect.centery - self.rect.top
                    angle = math.atan2(dy, dx)
                else:
                    # 敵がいない場合：真上 (-90度 = -pi/2 ラジアン)
                    angle = -math.pi / 2

                # 弾速の設定 (ホーミング弾は挙動が見えやすいよう少し遅め)
                speed: float = 8.0
                vx: float = math.cos(angle) * speed # 横方向の速度成分
                vy: float = math.sin(angle) * speed # 縦方向の速度成分
                
                # 弾の生成 (お札風の長方形)
                bullet = Bullet(self.rect.centerx + offset_x, self.rect.top, vy, vx, is_player_bullet=True, color=(255, 50, 50))
                # 弾の見た目を長方形（お札）に変更
                bullet.image = pygame.Surface((10, 14))
                bullet.image.fill(WHITE)           # 背景白
                pygame.draw.rect(bullet.image, RED, (2, 2, 6, 10)) # 赤い枠線を描く
                bullet.rect = bullet.image.get_rect(center=(self.rect.centerx + offset_x, self.rect.top))
                
                # スプライトグループに追加
                all_sprites.add(bullet)
                player_bullets.add(bullet)
            
            # 最終発射時間を更新
            self.last_shot_time = now

    def get_nearest_enemy(self) -> any:
        """
        現在画面内にいる敵の中から、自機に最も近い敵を探索して返す。
        Returns:
            Enemy | None: 最も近い敵インスタンス。敵がいない場合はNone。
        """
        nearest_enemy = None
        min_dist_sq = float('inf') # 最短距離の記録用（初期値は無限大）
        
        # global変数のenemiesグループから探索
        for enemy in enemies:
            # まだ画面に出てきていない(y < 0)敵は対象外にする
            if enemy.rect.top < 0:
                continue

            # 距離の二乗を計算 (ルート計算を避けて処理を高速化)
            # 距離^2 = (x1-x2)^2 + (y1-y2)^2
            dx = enemy.rect.centerx - self.rect.centerx
            dy = enemy.rect.centery - self.rect.centery
            dist_sq = dx*dx + dy*dy
            
            # これまでの最短距離より近ければ更新
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest_enemy = enemy
                
        # ボス戦中はボスもターゲット候補にする
        if is_boss_active:
            for boss in boss_group:
                 dx = boss.rect.centerx - self.rect.centerx
                 dy = boss.rect.centery - self.rect.centery
                 dist_sq = dx*dx + dy*dy
                 if dist_sq < min_dist_sq:
                     nearest_enemy = boss

        return nearest_enemy
    

class PlayerMelee(Player):
    """
    Type G: 近接型
    """
    def __init__(self) -> None:
        """
        近接型の各種設定
        """
        super().__init__()
        # 画像読み込み（なければ四角形で代用）
        try:
            image_path = "./fig/Gemini_Generated_Image_5a8oni5a8oni5a8o.png"
            if os.path.exists(image_path):
                original_image = pygame.image.load(image_path).convert_alpha()
                # 簡易的な背景透過処理（白っぽい部分を透過）
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
            else:
                raise FileNotFoundError
        except Exception as e:
            # 画像がない場合は黄色い四角
            self.image = pygame.Surface((40, 40))
            self.image.fill(YELLOW)
            
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)

        self.speed = 6
        self.shoot_interval = 15 # 連射速度速い（近接攻撃）
        
    def shoot(self) -> None:
        """
        近接型の射撃機構
        """
        
        if not keys[pygame.K_z]:
            return
        
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_interval:
            # 近接攻撃（剣を振るイメージの短射程・高威力弾）
            # is_melee=True を指定して、敵弾を消せるようにする
            
            # 中央
            bullet = Bullet(self.rect.centerx, self.rect.top, -15, 0, 
                            is_player_bullet=True, color=YELLOW, size=20, life=15, is_melee=True)
            # 左
            bullet_l = Bullet(self.rect.centerx - 15, self.rect.top + 10, -15, -2, 
                            is_player_bullet=True, color=YELLOW, size=15, life=10, is_melee=True)
            # 右
            bullet_r = Bullet(self.rect.centerx + 15, self.rect.top + 10, -15, 2, 
                            is_player_bullet=True, color=YELLOW, size=15, life=10, is_melee=True)

            all_sprites.add(bullet, bullet_l, bullet_r)
            player_bullets.add(bullet, bullet_l, bullet_r)
            self.last_shot_time = now


class PlayerSwitch(Player):
    """
    Type E: 射撃モード切替型
    """
    def __init__(self) -> None:
        """
        射撃モード切替型の各種設定
        """
        super().__init__()
        self.image.fill(YELLOW)
        self.speed = 5
        self.shoot_mode = 2 # 2wayスタート
        self.last_toggle_time = 0 # 連打防止

    def shoot(self) -> None:
        """
        射撃モード切替型の射撃機構
        """
        if not keys[pygame.K_z]:
            return
        now = pygame.time.get_ticks()
        self.shoot_interval = 80 if self.shoot_mode == 2 else 20
        if now - self.last_shot_time > self.shoot_interval:
            bullet_centers = [-10, 10] if self.shoot_mode == 2 else [0]
            for angle in bullet_centers:
                rad = math.radians(angle)
                vx = math.sin(rad) * 10
                vy = -math.cos(rad) * 10
                bullet = Bullet(self.rect.centerx, self.rect.top, vy, vx, is_player_bullet=True, color=YELLOW)
                all_sprites.add(bullet)
                player_bullets.add(bullet)
            self.last_shot_time = now
        
    def toggle_mode(self) -> None:
        """
        射撃モード切替型専用
        Xキーで射撃モード切替
        """
        now = pygame.time.get_ticks()
        if now -self.last_toggle_time > 300: # 0.3秒クールタイム
            self.shoot_mode = 1 if self.shoot_mode == 2 else 2
            self.last_toggle_time = now

class PlayerCharge(Player):
    """
    Type F: チャージショット型（水色）
    """
    def __init__(self) -> None:
        """
        チャージショット型の各種設定
        """
        super().__init__()
        self.image.fill(CYAN)
        self.speed = 5

        # チャージ関連
        self.is_charging = False
        self.charge_time = 0
        self.max_charge = 120  # フレーム上限

    def shoot(self) -> None:
        """
        チャージショット型の射撃機構
        """
        keys = pygame.key.get_pressed()

        # Zキーが押されている間：チャージ
        if keys[pygame.K_z]:
            self.is_charging = True
            self.charge_time = min(self.charge_time + 1, self.max_charge)

        # Zキーを離した瞬間：発射
        elif self.is_charging:
            # 発射処理
            power = self.charge_time
            self.is_charging = False
            self.charge_time = 0

            #チャージ時間に応じて弾の性能を変える
            damage = 1 + power // 5
            size = 10 + power // 4
            speed = 8 + power // 5

            bullet_centers = [0, -15, 15]
            for angle in bullet_centers:
                rad = math.radians(angle)
                vx = math.sin(rad) * speed
                vy = -math.cos(rad) * speed
                
                bullet = Bullet(
                    self.rect.centerx,
                    self.rect.top,
                    vy=vy,
                    vx=vx,
                    is_player_bullet=True,
                    color=CYAN,
                    pierce=True,
                    damage=damage
                )

            # 見た目強化（サイズ変更）
                bullet.image = pygame.Surface((size, size))
                bullet.image.fill(YELLOW)
                bullet.rect = bullet.image.get_rect(center=bullet.rect.center)

                all_sprites.add(bullet)
                player_bullets.add(bullet)

            # リセット
            self.is_charging = False
            self.charge_time = 0

# ★★★ キャラクターリストの定義 ★★★
# ここに辞書を追加していくだけで、選択肢が増えます
CHAR_LIST = [
    {"name": "Type A: Balance", "desc": "バランス型", "color": BLUE,  "class": PlayerBalance},
    {"name": "Type B: Speed",   "desc": "高速移動型", "color": RED,   "class": PlayerSpeed},
    {"name": "Type C: Shotgun", "desc": "広範囲攻撃", "color": GREEN, "class": PlayerShotgun},
    {"name": "Type D: Reimu", "desc": "誘導弾幕", "color": WHITE, "class": PlayerReimu},
    {"name": "Type E: Switch", "desc": "射撃切替", "color": YELLOW, "class": PlayerSwitch},
    {"name": "Type F: Charge", "desc": "チャージ攻撃", "color": CYAN, "class" :PlayerCharge},
    {"name": "Type G: Melee",   "desc": "近接斬撃(弾消し)", "color": YELLOW, "class": PlayerMelee},
    # 例: {"name": "Type D: Power", "desc": "高火力", "color": PURPLE, "class": PlayerPower}, 
]

class Enemy(pygame.sprite.Sprite):
    """
    ザコ敵クラス
    タイプに応じて動作を変更
    """
    def __init__(self, enemy_type:int) -> None:
        """
        敵の設定
        引数 enemy_type: 敵のタイプの種類
        """
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

    def update(self) -> None:
        """
        敵の挙動処理
        """
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

    def shoot_at_player(self) -> None:
        """
        プレイヤーに狙い撃ちする弾を発射
        """
        if player: # プレイヤーが存在する場合のみ
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
    """
    ボスクラス
    """
    def __init__(self, level:int=1) -> None:
        """
        ボスの設定
        引数 level: ボスのレベル(HPや弾幕の強度に影響)
        """
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

    def update(self) -> None:
        """
        ボスの行動更新
        """
        if self.state == "entry":
            self.rect.y += 2
            if self.rect.y >= 100:
                self.state = "battle"
        
        elif self.state == "battle":
            self.timer += 1
            self.rect.x = (SCREEN_WIDTH // 2) + math.sin(self.timer * 0.05) * 150
            
            if self.timer % 5 == 0:
                self.shoot_danmaku()

    def shoot_danmaku(self) -> None:
        """
        回転弾幕を発射
        """
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

# フォント設定
try:
    font = pygame.font.SysFont("meiryo", 40)
    small_font = pygame.font.SysFont("meiryo", 24)
except:
    font = pygame.font.Font(None, 40)
    small_font = pygame.font.Font(None, 24)

# グループ作成
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

player = None # プレイヤーインスタンス用

# ゲーム変数
score = 0
next_boss_score = BOSS_APPEAR_INTERVAL
boss_level = 1
is_boss_active = False

# ★インデックスで管理
selected_char_idx = 0 

# ゲーム状態定義
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

        # ■ キャラ選択画面
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
                    

                    # リストからクラスを取り出してインスタンス化
                    PlayerClass = CHAR_LIST[selected_char_idx]["class"]
                    player = PlayerClass()
                    

                    all_sprites.add(player)
                    
                    score = 0
                    next_boss_score = BOSS_APPEAR_INTERVAL
                    boss_level = 1
                    is_boss_active = False
                    current_state = GAME_STATE_PLAYING
                elif event.key == pygame.K_ESCAPE:
                    current_state = GAME_STATE_TITLE # 戻る

        # ■ ゲームオーバー画面
        elif current_state == GAME_STATE_GAMEOVER:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                current_state = GAME_STATE_TITLE

    # --- 更新処理 ---
    if current_state == GAME_STATE_PLAYING:
        keys = pygame.key.get_pressed()
        player.shoot()
        if isinstance(player, PlayerSwitch) and keys[pygame.K_x]:
            player.toggle_mode()




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

        hits = pygame.sprite.groupcollide(enemies, player_bullets, True, False) #弾はいったん消さない
        for enemy, bullets in hits.items():
            score += 10
            for bullet in bullets:
                if not getattr(bullet, "pierce", False):
                    bullet.kill()
        # ★追加: 近接攻撃(is_melee=True) vs 敵弾 の相殺処理
        # 1. まずプレイヤー弾の中から is_melee が True のものだけを抽出
        melee_bullets = [b for b in player_bullets if hasattr(b, 'is_melee') and b.is_melee]
        
        # 2. 抽出した近接弾と、敵弾グループの衝突判定
        #    False, True なので、近接弾は消えず(貫通)、敵弾だけ消える設定です
        if melee_bullets:
            # groupcollideはGroup同士である必要があるため、一時的なGroupを作るか、
            # あるいは spritecollide でループ回すのが簡単です
            for melee in melee_bullets:
                # 敵弾と接触したら、敵弾(True)を消す
                pygame.sprite.spritecollide(melee, enemy_bullets, True)
                
                # ボス弾幕も消したい場合はここに追加
                # pygame.sprite.spritecollide(melee, boss_bullets, True) # boss_bulletsグループがあれば    

        if is_boss_active:
            boss_hits = pygame.sprite.groupcollide(boss_group, player_bullets, False, True)
            for boss_sprite, bullets in boss_hits.items():
                for b in bullets:
                    boss_sprite.hp -= b.damage
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