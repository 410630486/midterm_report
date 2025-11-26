import pygame
import pygame.gfxdraw
import sys
import math
import os
import random

# ==========================================
# 1. 參數與配色
# ==========================================
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# --- 環境色 ---
COLOR_BG_DARK = (15, 20, 25)        
COLOR_GRASS_BASE = (34, 139, 34)     
COLOR_GRASS_DARK = (20, 100, 20)    
COLOR_GRASS_NOISE = (40, 75, 50)  
COLOR_PATH_DIRT = (101, 67, 33)      
COLOR_PATH_SAND = (210, 180, 140)   

# --- UI 色 ---
COLOR_UI_PANEL = (10, 15, 25, 200)  
COLOR_UI_BORDER = (200, 170, 80)
COLOR_UI_HIGHLIGHT = (255, 215, 0) 
COLOR_BTN_XP = (20, 80, 180)        
COLOR_BTN_REFRESH = (180, 60, 60)   
COLOR_BTN_START = (40, 180, 40)     
COLOR_BTN_START_DIS = (60, 80, 60)
COLOR_BTN_MENU = (60, 60, 80) 
COLOR_BTN_MENU_HOVER = (80, 80, 120)
COLOR_BTN_GENERIC = (60, 60, 80)
COLOR_BTN_HOVER = (80, 80, 100)
COLOR_XP_BAR = (100, 200, 255)      
COLOR_BENCH_SLOT = (0, 0, 0, 100)
COLOR_RANGE_VALID = (100, 255, 100, 80) 
COLOR_RANGE_INVALID = (255, 50, 50, 80) 
COLOR_PLACEMENT_HIGHLIGHT = (255, 255, 255, 50)
COLOR_SELL_ZONE = (150, 20, 20, 180)
COLOR_STAR = (255, 215, 0)
COLOR_TOOLTIP_BG = (15, 20, 35, 240)
COLOR_CRIT = (255, 50, 50)
COLOR_PAUSE_OVERLAY = (0, 0, 0, 180)
COLOR_GAMEOVER_OVERLAY = (50, 0, 0, 200)
# --- 設定選單顏色 ---
COLOR_SLIDER_BG = (50, 50, 50)
COLOR_SLIDER_FILL = (255, 215, 0)
COLOR_SLIDER_KNOB = (200, 200, 200)

# --- 羈絆代表色 ---
TRAIT_COLORS = {
    "魔神族": (200, 50, 50), "女神族": (255, 215, 0), "人類": (100, 150, 255), 
    "巨人族": (139, 69, 19), "妖精族": (255, 105, 180), "七大罪": (148, 0, 211),
    "十戒": (50, 50, 50), "聖騎士": (192, 192, 192), "德魯伊": (34, 139, 34),  
    "低級魔族": (100, 60, 60), "豬": (255, 192, 203)
}

COLOR_RARITY = {
    1: (140, 140, 140), 2: (20, 160, 60), 3: (40, 120, 220),
    4: (180, 40, 200), 5: (240, 180, 40)
}

pygame.font.init()
pygame.mixer.init()

def get_font(size, bold=False):
    fonts = ["Microsoft JhengHei", "SimHei", "PingFang TC", "Arial"]
    for f in fonts:
        try: return pygame.font.SysFont(f, size, bold=bold)
        except: continue
    return pygame.font.SysFont("Arial", size, bold=bold)

FONT_TITLE = get_font(100, bold=True)
FONT_XL = get_font(32, bold=True)
FONT_L = get_font(24, bold=True)
FONT_M = get_font(18, bold=True)
FONT_S = get_font(14)
FONT_XS = get_font(12)

UI_SPLIT_Y = 740 
MAP_WIDTH = SCREEN_WIDTH 
MAP_HEIGHT = SCREEN_HEIGHT 
MAP_OFFSET_X = 0 
MAP_OFFSET_Y = 0 

# ==========================================
# 2. 資料庫
# ==========================================
TRAIT_DATA = {
    "魔神族": {"breakpoints": [2, 4, 6], "desc": "攻擊力 +20% / 50% / 100%", "type": "race"},
    "女神族": {"breakpoints": [2, 4], "desc": "每秒回復 2% / 5% 最大生命", "type": "race"},
    "巨人族": {"breakpoints": [2, 3], "desc": "生命值 +30% / 80%", "type": "race"},
    "妖精族": {"breakpoints": [2], "desc": "攻擊範圍 +60", "type": "race"},
    "人類":   {"breakpoints": [2, 4, 6], "desc": "暴擊率 +20% / 40% / 60%", "type": "race"},
    "豬":     {"breakpoints": [1], "desc": "這是一隻豬，沒有任何戰鬥效果。", "type": "race"},
    "七大罪": {"breakpoints": [3, 5, 7], "desc": "全屬性 +15% / 30% / 60%", "type": "faction"},
    "十戒":   {"breakpoints": [2, 4], "desc": "攻速 +20% / 50%", "type": "faction"},
    "聖騎士": {"breakpoints": [2, 3], "desc": "受到傷害 -15% / -30%", "type": "faction"},
    "德魯伊": {"breakpoints": [2], "desc": "技能冷卻 -30%", "type": "faction"},
    "低級魔族": {"breakpoints": [2], "desc": "部署時返還 1 金幣", "type": "faction"}
}

UNIT_CONFIG = {
    "霍克": {'traits': ["豬"], 'role': 'RANGED', 'hp': 300, 'colors': ((255, 180, 200), (240, 150, 170), (50, 50, 50)), 'stats': (140, 0.8, 30), 'visual': (0.8, 0.7, False)},
    "紅魔族": {'traits': ["魔神族", "低級魔族"], 'role': 'MELEE', 'hp': 1200, 'colors': ((180, 50, 50), (120, 30, 30), (255, 255, 0)), 'stats': (180, 1.0, 50), 'visual': (1.2, 1.2, False)},
    "古利亞莫爾": {'traits': ["人類", "聖騎士"], 'role': 'MELEE', 'hp': 1500, 'colors': ((50, 50, 50), (150, 150, 160), (255, 255, 200)), 'stats': (150, 0.6, 60), 'visual': (1.3, 1.2, False)},
    "伊蓮恩": {'traits': ["妖精族", "德魯伊"], 'role': 'RANGED', 'hp': 200, 'colors': ((240, 230, 180), (200, 255, 220), (50, 50, 100)), 'stats': (180, 1.0, 45), 'visual': (0.9, 1.0, True)},
    "伊莉莎白": {'traits': ["女神族", "德魯伊"], 'role': 'RANGED', 'hp': 350, 'colors': ((220, 220, 240), (100, 180, 255), (50, 50, 100)), 'stats': (170, 1.2, 55), 'visual': (0.9, 1.1, False)},
    "黛安娜": {'traits': ["巨人族", "七大罪"], 'role': 'MELEE', 'hp': 2200, 'colors': ((100, 70, 30), (200, 140, 50), (50, 50, 50)), 'stats': (200, 1.5, 70), 'visual': (1.4, 1.4, False)},
    "灰瑟": {'traits': ["魔神族", "低級魔族"], 'role': 'RANGED', 'hp': 400, 'colors': ((80, 80, 80), (40, 30, 50), (150, 100, 200)), 'stats': (150, 1.3, 60), 'visual': (1.0, 1.2, True)},
    "吉爾桑德": {'traits': ["人類", "聖騎士"], 'role': 'MELEE', 'hp': 1400, 'colors': ((255, 150, 180), (150, 150, 255), (100, 200, 255)), 'stats': (160, 1.2, 50), 'visual': (1.0, 1.1, False)},
    "豪澤爾": {'traits': ["人類", "聖騎士"], 'role': 'MELEE', 'hp': 1300, 'colors': ((200, 200, 100), (100, 200, 100), (50, 50, 50)), 'stats': (150, 1.1, 45), 'visual': (1.0, 1.1, False)},
    "瑪梅利斯": {'traits': ["魔神族", "十戒"], 'role': 'RANGED', 'hp': 400, 'colors': ((255, 200, 220), (255, 255, 255), (100, 0, 0)), 'stats': (160, 1.2, 50), 'visual': (0.9, 1.1, True)},
    "金": {'traits': ["妖精族", "七大罪"], 'role': 'RANGED', 'hp': 300, 'colors': ((255, 160, 50), (50, 150, 150), (50, 50, 50)), 'stats': (220, 1.4, 40), 'visual': (0.9, 1.1, True)},
    "高瑟": {'traits': ["人類", "七大罪"], 'role': 'RANGED', 'hp': 450, 'colors': ((255, 100, 150), (240, 240, 250), (200, 50, 150)), 'stats': (160, 1.3, 50), 'visual': (1.0, 1.1, False)},
    "伽藍": {'traits': ["魔神族", "十戒"], 'role': 'MELEE', 'hp': 1800, 'colors': ((100, 20, 20), (40, 100, 40), (200, 200, 200)), 'stats': (180, 1.5, 45), 'visual': (1.2, 1.5, False)},
    "詹娜": {'traits': ["人類", "德魯伊"], 'role': 'RANGED', 'hp': 350, 'colors': ((240, 240, 200), (50, 120, 50), (255, 255, 255)), 'stats': (160, 1.0, 40), 'visual': (0.9, 1.0, False)},
    "薩瑞爾": {'traits': ["女神族", "聖騎士"], 'role': 'RANGED', 'hp': 500, 'colors': ((240, 240, 240), (50, 150, 255), (255, 215, 0)), 'stats': (170, 1.4, 40), 'visual': (0.8, 0.8, True)},
    "塔米葉": {'traits': ["女神族", "聖騎士"], 'role': 'MELEE', 'hp': 2000, 'colors': ((240, 240, 240), (100, 200, 100), (255, 215, 0)), 'stats': (140, 1.0, 60), 'visual': (1.4, 1.4, True)},
    "德里艾利": {'traits': ["魔神族", "十戒"], 'role': 'MELEE', 'hp': 1700, 'colors': ((255, 100, 0), (50, 0, 0), (0, 0, 0)), 'stats': (140, 1.6, 30), 'visual': (1.0, 1.1, False)},
    "門斯皮特": {'traits': ["魔神族", "十戒"], 'role': 'RANGED', 'hp': 500, 'colors': ((100, 50, 0), (255, 255, 255), (50, 0, 0)), 'stats': (180, 1.5, 55), 'visual': (1.0, 1.2, False)},
    "瑪琳": {'traits': ["人類", "七大罪"], 'role': 'RANGED', 'hp': 500, 'colors': ((30, 30, 40), (80, 40, 120), (100, 200, 255)), 'stats': (180, 1.6, 35), 'visual': (1.0, 1.2, True)},
    "多洛爾": {'traits': ["巨人族", "十戒"], 'role': 'MELEE', 'hp': 2800, 'colors': ((120, 100, 80), (80, 70, 60), (255, 100, 50)), 'stats': (200, 1.8, 80), 'visual': (1.5, 1.5, False)},
    "艾斯塔羅薩": {'traits': ["魔神族", "十戒"], 'role': 'MELEE', 'hp': 3000, 'colors': ((200, 200, 200), (80, 50, 30), (100, 0, 0)), 'stats': (150, 1.5, 60), 'visual': (1.2, 1.2, False)},
    "班": {'traits': ["人類", "七大罪"], 'role': 'MELEE', 'hp': 2600, 'colors': ((200, 200, 220), (180, 30, 30), (200, 0, 0)), 'stats': (160, 1.4, 40), 'visual': (1.0, 1.2, False)},
    "流德雪爾": {'traits': ["女神族", "聖騎士"], 'role': 'RANGED', 'hp': 600, 'colors': ((255, 255, 255), (220, 220, 255), (255, 215, 0)), 'stats': (190, 1.8, 30), 'visual': (1.0, 1.3, True)},
    "梅利奧達斯": {'traits': ["魔神族", "七大罪"], 'role': 'MELEE', 'hp': 2400, 'colors': ((240, 220, 50), (50, 50, 60), (50, 150, 50)), 'stats': (180, 2.0, 25), 'visual': (1.0, 1.1, False)},
    "艾斯卡諾": {'traits': ["人類", "七大罪"], 'role': 'MELEE', 'hp': 3500, 'colors': ((255, 200, 50), (200, 180, 50), (255, 255, 200)), 'stats': (220, 2.8, 100), 'visual': (1.4, 1.6, False)},
    "馬埃爾": {'traits': ["女神族", "聖騎士"], 'role': 'MELEE', 'hp': 3200, 'colors': ((255, 255, 255), (255, 215, 0), (255, 100, 0)), 'stats': (200, 2.5, 40), 'visual': (1.2, 1.4, True)},
    "賽多里斯": {'traits': ["魔神族", "十戒"], 'role': 'MELEE', 'hp': 2500, 'colors': ((30, 30, 30), (150, 20, 20), (100, 0, 100)), 'stats': (160, 2.2, 30), 'visual': (1.0, 1.1, False)}
}
DEFAULT_CONFIG = {'role': 'RANGED', 'hp': 100, 'colors': ((100,100,100), (150,150,150), (200,200,200)), 'stats': (150, 1.0, 60), 'visual': (1.0, 1.0, False)}

# --- 敵人資料庫 (含扣血量) ---
ENEMY_CONFIG = {
    "小惡魔": {
        'colors': ((150, 150, 150), (100, 80, 120), (255, 50, 255)), 
        'hp_base': 30, 'damage': 5, 'player_damage': 2, 
        'radius': 10, 'height': 12
    },
    "紅魔族": {
        'colors': ((180, 50, 50), (120, 30, 30), (255, 255, 0)), 
        'hp_base': 80, 'damage': 15, 'player_damage': 5, 
        'radius': 14, 'height': 18
    },
    "灰魔族": {
        'colors': ((100, 100, 100), (60, 60, 60), (200, 0, 200)), 
        'hp_base': 200, 'damage': 20, 'player_damage': 8, 
        'radius': 18, 'height': 22
    },
    "聖騎士": {
        'colors': ((200, 200, 220), (150, 150, 180), (50, 200, 255)), 
        'hp_base': 120, 'damage': 25, 'player_damage': 10, 
        'radius': 15, 'height': 20
    }
}

CARD_POOL = {
    1: [("紅魔族", UNIT_CONFIG["紅魔族"]['traits']), ("霍克", UNIT_CONFIG["霍克"]['traits']), ("古利亞莫爾", UNIT_CONFIG["古利亞莫爾"]['traits']), ("伊蓮恩", UNIT_CONFIG["伊蓮恩"]['traits'])],
    2: [("伊莉莎白", UNIT_CONFIG["伊莉莎白"]['traits']), ("黛安娜", UNIT_CONFIG["黛安娜"]['traits']), ("灰瑟", UNIT_CONFIG["灰瑟"]['traits']), ("吉爾桑德", UNIT_CONFIG["吉爾桑德"]['traits']), ("豪澤爾", UNIT_CONFIG["豪澤爾"]['traits']), ("瑪梅利斯", UNIT_CONFIG["瑪梅利斯"]['traits'])],
    3: [("金", UNIT_CONFIG["金"]['traits']), ("高瑟", UNIT_CONFIG["高瑟"]['traits']), ("伽藍", UNIT_CONFIG["伽藍"]['traits']), ("詹娜", UNIT_CONFIG["詹娜"]['traits']), ("薩瑞爾", UNIT_CONFIG["薩瑞爾"]['traits']), ("塔米葉", UNIT_CONFIG["塔米葉"]['traits']), ("德里艾利", UNIT_CONFIG["德里艾利"]['traits']), ("門斯皮特", UNIT_CONFIG["門斯皮特"]['traits'])],
    4: [("瑪琳", UNIT_CONFIG["瑪琳"]['traits']), ("多洛爾", UNIT_CONFIG["多洛爾"]['traits']), ("艾斯塔羅薩", UNIT_CONFIG["艾斯塔羅薩"]['traits']), ("班", UNIT_CONFIG["班"]['traits']), ("流德雪爾", UNIT_CONFIG["流德雪爾"]['traits'])],
    5: [("梅利奧達斯", UNIT_CONFIG["梅利奧達斯"]['traits']), ("艾斯卡諾", UNIT_CONFIG["艾斯卡諾"]['traits']), ("馬埃爾", UNIT_CONFIG["馬埃爾"]['traits']), ("賽多里斯", UNIT_CONFIG["賽多里斯"]['traits'])]
}

SHOP_ODDS = {
    3: [75, 25, 0, 0, 0], 4: [55, 30, 15, 0, 0], 5: [45, 33, 20, 2, 0],
    6: [25, 40, 30, 5, 0], 7: [19, 30, 35, 15, 1], 8: [16, 20, 35, 25, 4]
}

# ==========================================
# 3. 音效管理器
# ==========================================
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_playing = None
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        audio_dir = os.path.join(base_path, "audio")
        print(f"SoundManager: Looking for audio files in: {audio_dir}")

        self.load_sound("click", os.path.join(audio_dir, "click.wav"))
        self.load_sound("buy", os.path.join(audio_dir, "buy.wav"))
        self.load_sound("sell", os.path.join(audio_dir, "sell.wav"))
        self.load_sound("refresh", os.path.join(audio_dir, "refresh.wav"))
        self.load_sound("attack_melee", os.path.join(audio_dir, "attack_melee.wav"))
        self.load_sound("attack_range", os.path.join(audio_dir, "attack_range.wav"))
        self.load_sound("game_over", os.path.join(audio_dir, "game_over.wav"))
        self.load_sound("dead", os.path.join(audio_dir, "dead.wav"))
        
        self.bgm_path = os.path.join(audio_dir, "bgm.mp3")
        self.play_music(self.bgm_path)
        
        self.volume_master = 0.5
        self.set_volume(0.5)

    def load_sound(self, name, path):
        if os.path.exists(path):
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"Warning: Failed to load sound {path} ({e})")
        else:
            print(f"Warning: File not found: {path}")

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def play_music(self, path):
        if os.path.exists(path) and self.music_playing != path:
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1) 
                self.music_playing = path
            except Exception as e:
                print(f"Warning: Failed to load music {path} ({e})")
    
    def set_volume(self, volume):
        self.volume_master = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume_master)
        for s in self.sounds.values():
            s.set_volume(self.volume_master)

# ==========================================
# 4. 基礎物件與繪圖
# ==========================================
MERGE_POINT = (SCREEN_WIDTH // 2, 350 + MAP_OFFSET_Y)
END_POINT = (SCREEN_WIDTH // 2, SCREEN_HEIGHT + 50) 

LEFT_KEY_POINTS = [(-100, 200), (300, 200), (600, 350), MERGE_POINT]
RIGHT_KEY_POINTS = [(SCREEN_WIDTH + 100, 200), (SCREEN_WIDTH - 300, 200), (SCREEN_WIDTH - 600, 350), MERGE_POINT]
TAIL_KEY_POINTS = [MERGE_POINT, (SCREEN_WIDTH // 2, 550 + MAP_OFFSET_Y), END_POINT]

def generate_smooth_path(key_points, density=4):
    smooth_path = []
    for i in range(len(key_points) - 1):
        p1 = key_points[i]
        p2 = key_points[i+1]
        dist = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
        steps = int(dist / density)
        if steps == 0: steps = 1
        for j in range(steps):
            t = j / steps
            x = p1[0] * (1-t) + p2[0] * t
            y = p1[1] * (1-t) + p2[1] * t
            smooth_path.append((x, y))
    smooth_path.append(key_points[-1])
    return smooth_path

PATH_LEFT = generate_smooth_path(LEFT_KEY_POINTS + TAIL_KEY_POINTS[1:])
PATH_RIGHT = generate_smooth_path(RIGHT_KEY_POINTS + TAIL_KEY_POINTS[1:])
ALL_PATH_POINTS = PATH_LEFT + PATH_RIGHT
PATH_WIDTH = 70 

def draw_smooth_circle(surface, color, center, radius):
    x, y = int(center[0]), int(center[1])
    pygame.gfxdraw.filled_circle(surface, x, y, int(radius), color)
    pygame.gfxdraw.aacircle(surface, x, y, int(radius), color)

def draw_smooth_ellipse(surface, color, rect):
    x, y, w, h = rect
    cx, cy = x + w//2, y + h//2
    rx, ry = w//2, h//2
    pygame.gfxdraw.filled_ellipse(surface, int(cx), int(cy), int(rx), int(ry), color)
    pygame.gfxdraw.aaellipse(surface, int(cx), int(cy), int(rx), int(ry), color)

def draw_star_shape(surface, color, x, y, size):
    points = []
    for i in range(10):
        angle = i * 36 + 18
        r = size if i % 2 == 0 else size * 0.4
        px = x + r * math.cos(math.radians(angle - 90))
        py = y + r * math.sin(math.radians(angle - 90))
        points.append((px, py))
    pygame.gfxdraw.filled_polygon(surface, points, color)
    pygame.gfxdraw.aapolygon(surface, points, color)

def draw_gear_icon(surface, color, center, radius):
    cx, cy = center
    pygame.draw.circle(surface, color, center, radius, 3) 
    for i in range(8):
        angle = math.radians(i * 45)
        sx = cx + math.cos(angle) * (radius - 4)
        sy = cy + math.sin(angle) * (radius - 4)
        ex = cx + math.cos(angle) * (radius + 4)
        ey = cy + math.sin(angle) * (radius + 4)
        pygame.draw.line(surface, color, (sx, sy), (ex, ey), 5)
    pygame.draw.circle(surface, color, center, 4)

def draw_iso_cylinder(surface, color_side, color_top, x, y, r, h, outline=None):
    rect = pygame.Rect(x - r, y - h, r * 2, h)
    pygame.draw.rect(surface, color_side, rect)
    draw_smooth_circle(surface, color_side, (x, y), r)
    draw_smooth_circle(surface, color_top, (x, y - h), r)
    pygame.draw.arc(surface, (255, 255, 255), (x-r+2, y-h-r+2, r*2-4, r*2-4), math.pi/2, math.pi, 2)
    if outline: pygame.gfxdraw.aacircle(surface, int(x), int(y-h), int(r), outline)

def draw_shadow(surface, x, y, r):
    s = pygame.Surface((r*2, r), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 80), (0, 0, r*2, r))
    surface.blit(s, (x-r, y-r//2))

def draw_chamfered_rect(surface, color, rect, border=None, border_width=2):
    x, y, w, h = rect
    c = 10
    pts = [(x+c,y), (x+w-c,y), (x+w,y+c), (x+w,y+h-c), (x+w-c,y+h), (x+c,y+h), (x,y+h-c), (x,y+c)]
    pygame.draw.polygon(surface, color, pts)
    if border: pygame.draw.polygon(surface, border, pts, border_width)

def draw_iso_humanoid(surface, colors, x, y, r, h, floating_offset=0, is_dead=False):
    draw_y = y - floating_offset
    if is_dead: colors = ((100,100,100), (80,80,80), (50,50,50))
    body_h = h * 0.4; body_r = r * 0.7; body_y = draw_y
    head_r = r * 0.9; head_y = draw_y - body_h - head_r * 0.3 
    body_color_top = tuple(min(255, c + 20) for c in colors[1])
    draw_iso_cylinder(surface, colors[1], body_color_top, x, body_y, body_r, body_h)
    arm_r = body_r * 0.4
    draw_smooth_ellipse(surface, colors[1], (x - body_r - arm_r, body_y - body_h, arm_r*2, arm_r*3))
    draw_smooth_ellipse(surface, colors[1], (x + body_r - arm_r, body_y - body_h, arm_r*2, arm_r*3))
    draw_smooth_circle(surface, colors[0], (x, head_y), head_r)
    highlight_color = tuple(min(255, c + 40) for c in colors[0])
    draw_smooth_circle(surface, highlight_color, (x-head_r*0.2, head_y-head_r*0.2), head_r*0.8)
    if not is_dead:
        eye_r = head_r * 0.15; eye_y = head_y + head_r * 0.1
        draw_smooth_ellipse(surface, colors[2], (x - head_r*0.3 - eye_r, eye_y - eye_r, eye_r*2, eye_r*1.5))
        draw_smooth_ellipse(surface, colors[2], (x + head_r*0.3 - eye_r, eye_y - eye_r, eye_r*2, eye_r*1.5))
    else:
        def draw_x(sx, sy, size):
            pygame.draw.aaline(surface, (0,0,0), (sx-size, sy-size), (sx+size, sy+size))
            pygame.draw.aaline(surface, (0,0,0), (sx-size, sy+size), (sx+size, sy-size))
        draw_x(center_x - head_r*0.3, eye_y, 3)
        draw_x(center_x + head_r*0.3, eye_y, 3)

def draw_animated_humanoid(surface, colors, x, y, r, h, timer=0, action='IDLE', is_dead=False, is_floating=False):
    draw_y = y
    if is_dead: colors = ((100,100,100), (80,80,80), (50,50,50))
    bob_y = 0; leg_offset = 0; attack_x = 0
    if not is_dead:
        if action == 'IDLE':
            bob_y = math.sin(timer * 0.05) * 2
            if is_floating: bob_y = math.sin(timer * 0.05) * 5 - 15
        elif action == 'WALK':
            bob_y = abs(math.sin(timer * 0.2)) * 3
            leg_offset = math.sin(timer * 0.2) * (r * 0.4)
        elif action == 'ATTACK':
            attack_x = 5 
    center_x = x + attack_x; center_y = draw_y - bob_y
    body_h = h * 0.4; body_r = r * 0.7; body_y = center_y
    head_r = r * 0.9; head_y = center_y - body_h - head_r * 0.3 
    if action == 'WALK' and not is_floating:
        foot_r = body_r * 0.5
        draw_smooth_ellipse(surface, colors[1], (center_x - body_r + leg_offset, y - foot_r, foot_r*2, foot_r*1.5))
        draw_smooth_ellipse(surface, colors[1], (center_x + body_r*0.2 - leg_offset, y - foot_r, foot_r*2, foot_r*1.5))
    elif not is_floating and not is_dead:
        draw_smooth_ellipse(surface, colors[1], (center_x - body_r, y - body_r*0.5, body_r*2, body_r))
    body_top_col = tuple(min(255, c + 20) for c in colors[1])
    draw_iso_cylinder(surface, colors[1], body_top_col, center_x, body_y, body_r, body_h)
    arm_r = body_r * 0.4
    arm_swing = leg_offset if action == 'WALK' else 0
    draw_smooth_ellipse(surface, colors[1], (center_x - body_r - arm_r - arm_swing, body_y - body_h, arm_r*2, arm_r*3))
    draw_smooth_ellipse(surface, colors[1], (center_x + body_r - arm_r + arm_swing, body_y - body_h, arm_r*2, arm_r*3))
    draw_smooth_circle(surface, colors[0], (center_x, head_y), head_r)
    highlight_col = tuple(min(255, c + 40) for c in colors[0])
    draw_smooth_circle(surface, highlight_col, (center_x-head_r*0.2, head_y-head_r*0.2), head_r*0.8)
    eye_r = head_r * 0.15; eye_y = head_y + head_r * 0.1
    if not is_dead:
        draw_smooth_ellipse(surface, colors[2], (center_x - head_r*0.3 - eye_r, eye_y - eye_r, eye_r*2, eye_r*1.5))
        draw_smooth_ellipse(surface, colors[2], (x + head_r*0.3 - eye_r, eye_y - eye_r, eye_r*2, eye_r*1.5))
    else:
        def draw_x(sx, sy, size):
            pygame.draw.aaline(surface, (0,0,0), (sx-size, sy-size), (sx+size, sy+size))
            pygame.draw.aaline(surface, (0,0,0), (sx-size, sy+size), (sx+size, sy-size))
        draw_x(center_x - head_r*0.3, eye_y, 3)
        draw_x(center_x + head_r*0.3, eye_y, 3)

def draw_card_portrait(surface, x, y, w, h, name):
    config = UNIT_CONFIG.get(name, DEFAULT_CONFIG)
    colors = config['colors']
    bg_rect = pygame.Rect(x, y, w, h)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, (30, 30, 45, 180), (0,0,w,h))
    surface.blit(s, (x, y))
    pygame.draw.rect(surface, (60, 60, 80), bg_rect, 1)
    cx, cy = x + w // 2, y + h // 2 + 15
    scale = 1.2 
    draw_smooth_ellipse(surface, colors[1], (cx - 20*scale, cy, 40*scale, 30*scale))
    draw_smooth_circle(surface, colors[0], (cx, cy - 15*scale), 18*scale)
    eye_c = colors[2]
    draw_smooth_circle(surface, eye_c, (cx - 6*scale, cy - 15*scale), 3*scale)
    draw_smooth_circle(surface, eye_c, (cx + 6*scale, cy - 15*scale), 3*scale)

def draw_hexagon(surface, color, center, size):
    cx, cy = center
    points = []
    for i in range(6):
        angle_deg = 60 * i - 30
        angle_rad = math.radians(angle_deg)
        points.append((cx + size * math.cos(angle_rad), cy + size * math.sin(angle_rad)))
    pygame.gfxdraw.filled_polygon(surface, points, color)
    pygame.gfxdraw.aapolygon(surface, points, color)

def draw_tooltip(screen, x, y, trait_name, count, data):
    unit_list = []
    for cost, units in CARD_POOL.items():
        for u_name, u_traits in units:
            if trait_name in u_traits:
                unit_list.append((cost, u_name))
    unit_list.sort(key=lambda x: x[0])
    lines = []
    lines.append(FONT_M.render(f"{trait_name} ({count})", True, (255, 215, 0)))
    
    bp_text = "啟動需求: " + " / ".join(map(str, data['breakpoints']))
    lines.append(FONT_S.render(bp_text, True, (100, 255, 100)))
    
    lines.append(FONT_S.render(data['desc'], True, (200, 200, 200)))
    lines.append(FONT_S.render("--- 角色列表 ---", True, (150, 150, 150)))
    for idx, (cost, name) in enumerate(unit_list):
        color = COLOR_RARITY.get(cost, (255, 255, 255))
        lines.append((FONT_S.render(f"${cost} {name}", True, color)))
    max_w = 220
    total_h = 20 + len(lines) * 25
    bg_rect = pygame.Rect(x + 25, y - 10, max_w, total_h)
    draw_chamfered_rect(screen, COLOR_TOOLTIP_BG, bg_rect, COLOR_UI_BORDER)
    curr_y = y 
    for line in lines:
        if isinstance(line, pygame.Surface):
            screen.blit(line, (x + 35, curr_y))
        curr_y += 22

def draw_unit_tooltip(screen, unit, mx, my):
    w, h = 220, 180
    x = mx + 20; y = my - 20
    if x + w > SCREEN_WIDTH: x = mx - w - 20
    if y + h > SCREEN_HEIGHT: y = my - h - 20
    draw_chamfered_rect(screen, COLOR_TOOLTIP_BG, (x, y, w, h), COLOR_UI_BORDER)
    stars = "★" * unit.star
    title_color = COLOR_STAR if unit.star >= 3 else (255,255,255)
    title_surf = FONT_M.render(f"{unit.data.name} {stars}", True, title_color)
    screen.blit(title_surf, (x + 15, y + 10))
    trait_str = " / ".join(unit.data.traits)
    trait_surf = FONT_S.render(trait_str, True, (180,180,180))
    screen.blit(trait_surf, (x + 15, y + 35))
    y_off = 60
    hp_txt = f"HP: {int(unit.current_hp)} / {int(unit.max_hp)}"
    screen.blit(FONT_S.render(hp_txt, True, (100, 255, 100)), (x + 15, y + y_off))
    y_off += 20
    dmg_txt = f"攻擊: {int(unit.damage)}"
    screen.blit(FONT_S.render(dmg_txt, True, (255, 100, 100)), (x + 15, y + y_off))
    y_off += 20
    range_txt = f"範圍: {int(unit.aggro_range)}" 
    screen.blit(FONT_S.render(range_txt, True, (100, 200, 255)), (x + 15, y + y_off))
    y_off += 20
    cd_txt = f"攻速: {round(60/unit.cooldown_max, 1)}/秒"
    screen.blit(FONT_S.render(cd_txt, True, (255, 255, 100)), (x + 15, y + y_off))
    y_off += 25
    skill_name = "技能: 扇形斬擊 (AOE)" if unit.role == 'MELEE' else "技能: 魔法彈 (單體)"
    screen.blit(FONT_S.render(skill_name, True, (200, 200, 255)), (x + 15, y + y_off))

# ==========================================
# 5. 遊戲物件 (Entities)
# ==========================================
class Decoration:
    def __init__(self, x, y, type):
        self.x, self.y = x, y; self.type = type; self.scale = random.uniform(0.8, 1.2)
        self.wind_phase = random.uniform(0, 100) 

    def draw(self, screen, timer=0):
        if self.type == 'tree':
            sway = math.sin(timer * 0.03 + self.wind_phase) * 3 
            draw_iso_cylinder(screen, (60, 40, 20), (80, 60, 30), self.x, self.y, 6*self.scale, 15*self.scale)
            for i in range(3):
                h_off = 15*self.scale + i * 12 * self.scale
                r = (18-i*4)*self.scale
                c1 = (20, 80+i*20, 30); c2 = (40, 120+i*20, 50)
                sway_offset = sway * (i + 1) * 0.5
                draw_iso_cylinder(screen, c1, c2, self.x + sway_offset, self.y - h_off, r, 10*self.scale)
        elif self.type == 'rock':
            draw_iso_cylinder(screen, (80, 80, 85), (120, 120, 125), self.x, self.y, 10*self.scale, 8*self.scale)

class Projectile:
    def __init__(self, x, y, target, damage, color, is_crit=False):
        self.x, self.y = x, y; self.target = target; self.damage = damage; self.color = color
        self.is_crit = is_crit
        self.speed = 12; self.active = True; self.z = 30
    def update(self):
        if not self.target or self.target.current_hp <= 0: self.active = False; return
        tx, ty = self.target.x, self.target.y - self.target.height/2
        dx, dy = tx - self.x, ty - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist < self.speed: self.target.take_damage(self.damage); self.active = False
        else: self.x += (dx/dist)*self.speed; self.y += (dy/dist)*self.speed
    def draw(self, screen):
        r = 8 if self.is_crit else 5
        c = COLOR_CRIT if self.is_crit else self.color
        draw_smooth_circle(screen, c, (self.x, self.y - self.z), r)

class Enemy:
    def __init__(self, path, speed, wave_hp_bonus=0, type_name="紅魔族"):
        self.path = path; self.speed = speed; self.x, self.y = path[0]
        self.idx = 0; self.finished = False
        
        if type_name == "小惡魔":
            config = {'colors': ((150, 150, 150), (100, 80, 120), (255, 50, 255)), 'hp_base': 30, 'damage': 5, 'player_damage': 2, 'radius': 10, 'height': 12}
            self.speed = speed * 1.5
        elif type_name == "灰魔族":
            config = {'colors': ((100, 100, 100), (60, 60, 60), (200, 0, 200)), 'hp_base': 200, 'damage': 20, 'player_damage': 8, 'radius': 18, 'height': 22}
            self.speed = speed * 0.7
        elif type_name == "聖騎士":
            config = {'colors': ((200, 200, 220), (150, 150, 180), (50, 200, 255)), 'hp_base': 120, 'damage': 25, 'player_damage': 10, 'radius': 15, 'height': 20}
            self.speed = speed
        else: 
            config = {'colors': ((180, 50, 50), (120, 30, 30), (255, 255, 0)), 'hp_base': 80, 'damage': 15, 'player_damage': 5, 'radius': 14, 'height': 18}
            self.speed = speed
            
        self.colors = config['colors']
        self.radius = config['radius']
        self.height = config['height']
        self.damage = config['damage']
        self.player_damage = config.get('player_damage', 5)
        
        self.max_hp = config['hp_base'] + wave_hp_bonus
        self.current_hp = self.max_hp
        self.attack_cd = 0; self.blocked_by = None
        self.anim_timer = random.randint(0, 100) 

    def take_damage(self, dmg): self.current_hp -= dmg
    
    def move(self, units):
        if self.current_hp <= 0: return
        self.anim_timer += 1 
        
        if self.blocked_by:
            if self.blocked_by.current_hp <= 0 or self.blocked_by not in units:
                self.blocked_by = None
            else:
                if self.attack_cd > 0: self.attack_cd -= 1
                else:
                    self.blocked_by.take_damage(self.damage)
                    self.attack_cd = 60
                return 

        for u in units:
            if u.role == 'MELEE' and u.current_hp > 0:
                dist = math.sqrt((self.x - u.x)**2 + (self.y - u.y)**2)
                if dist < 20:
                    self.blocked_by = u
                    return

        if self.idx >= len(self.path): self.finished = True; return
        tx, ty = self.path[self.idx]
        dist = math.sqrt((tx-self.x)**2 + (ty-self.y)**2)
        if dist < self.speed: self.x, self.y = tx, ty; self.idx += 1
        else: self.x += ((tx-self.x)/dist)*self.speed; self.y += ((ty-self.y)/dist)*self.speed

    def draw(self, screen):
        draw_shadow(screen, self.x, self.y, self.radius)
        action = 'WALK'
        if self.blocked_by: action = 'ATTACK' 
        draw_animated_humanoid(screen, self.colors, self.x, self.y, self.radius, self.height, self.anim_timer, action)
        if self.current_hp < self.max_hp:
            bar_w = 24; pct = self.current_hp / self.max_hp
            bx, by = self.x - bar_w/2, self.y - self.height - 15
            pygame.draw.rect(screen, (50, 0, 0), (bx, by, bar_w, 4))
            pygame.draw.rect(screen, (0, 255, 0), (bx, by, bar_w * pct, 4))

class Unit:
    def __init__(self, x, y, card_data, star_level=1):
        self.anchor_x, self.anchor_y = x, y
        self.x, self.y = x, y
        self.data = card_data
        self.star = star_level
        config = UNIT_CONFIG.get(card_data.name, DEFAULT_CONFIG)
        self.role = config['role']
        self.colors = config['colors']
        stats = config['stats']
        visual = config['visual']
        
        self.base_mult_hp = 1.8 ** (self.star - 1)
        self.base_mult_dmg = 1.5 ** (self.star - 1)
        
        self.aggro_range = stats[0] 
        self.range = self.aggro_range 
        
        self.attack_range = 50 
        self.damage = 10 * card_data.cost * stats[1] * self.base_mult_dmg
        self.cooldown_max = stats[2]; self.cooldown = 0
        
        self.base_max_hp = config.get('hp', 200) * (1 + card_data.cost * 0.2) * self.base_mult_hp
        self.max_hp = self.base_max_hp
        self.current_hp = self.max_hp
        
        scale_star = 1 + (self.star - 1) * 0.2
        base_radius = 20 * scale_star; base_height = 35 * scale_star
        self.radius = base_radius * visual[0]; self.height = base_height * visual[1]
        self.floating = visual[2]
        self.float_offset = 15 if self.floating else 0
        self.anim_timer = random.randint(0, 100); self.is_attacking = False
        self.slash_timer = 0; self.slash_angle = 0
        self.state = 'IDLE'; self.target = None; self.move_speed = 2.0
        self.dmg_red = 0 
        
        self.rect = pygame.Rect(0, 0, 0, 0)

    def take_damage(self, dmg, reduction=0):
        actual_dmg = dmg * (1 - self.dmg_red) 
        self.current_hp -= actual_dmg
        if self.current_hp < 0: self.current_hp = 0

    def revive(self): 
        self.current_hp = self.max_hp
        self.x, self.y = self.anchor_x, self.anchor_y
        self.state = 'IDLE'; self.target = None

    def get_buff_multipliers(self, active_traits):
        dmg_mul = 1.0; hp_mul = 1.0; cd_mul = 1.0; range_add = 0; regen_rate = 0; crit_rate = 0; dmg_red = 0
        
        demon_count = active_traits.get("魔神族", 0)
        if demon_count >= 6: dmg_mul += 1.0
        elif demon_count >= 4: dmg_mul += 0.5
        elif demon_count >= 2: dmg_mul += 0.2
        
        human_count = active_traits.get("人類", 0)
        if human_count >= 6: crit_rate = 0.6
        elif human_count >= 4: crit_rate = 0.35
        elif human_count >= 2: crit_rate = 0.15
        
        giant_count = active_traits.get("巨人族", 0)
        if giant_count >= 3: hp_mul += 0.8
        elif giant_count >= 2: hp_mul += 0.3
        
        fairy_count = active_traits.get("妖精族", 0)
        if fairy_count >= 2: range_add += 60
        
        goddess_count = active_traits.get("女神族", 0)
        if goddess_count >= 4: regen_rate = 0.05
        elif goddess_count >= 2: regen_rate = 0.02
        
        sin_count = active_traits.get("七大罪", 0)
        if sin_count >= 7: dmg_mul += 0.6; hp_mul += 0.6; cd_mul -= 0.6 
        elif sin_count >= 5: dmg_mul += 0.3; hp_mul += 0.3; cd_mul -= 0.3
        elif sin_count >= 3: dmg_mul += 0.15; hp_mul += 0.15; cd_mul -= 0.15
        
        cmd_count = active_traits.get("十戒", 0)
        if cmd_count >= 4: cd_mul -= 0.5
        elif cmd_count >= 2: cd_mul -= 0.2
        
        paladin_count = active_traits.get("聖騎士", 0)
        if paladin_count >= 3: dmg_red = 0.3 
        elif paladin_count >= 2: dmg_red = 0.15
        
        druid_count = active_traits.get("德魯伊", 0)
        if druid_count >= 2: cd_mul -= 0.3

        return dmg_mul, hp_mul, cd_mul, range_add, regen_rate, crit_rate, dmg_red

    def update(self, enemies, projectiles, active_traits, sound_manager):
        self.anim_timer += 1; self.is_attacking = False 
        if self.slash_timer > 0: self.slash_timer -= 1
        if self.current_hp <= 0: return 
        
        dmg_mul, hp_mul, cd_mul, range_add, regen_rate, crit_rate, self.dmg_red = self.get_buff_multipliers(active_traits)
        
        expected_max_hp = self.base_max_hp * hp_mul
        if abs(self.max_hp - expected_max_hp) > 1:
             ratio = self.current_hp / self.max_hp
             self.max_hp = expected_max_hp
             self.current_hp = self.max_hp * ratio
        
        current_damage = self.damage * dmg_mul
        current_cooldown_max = self.cooldown_max * cd_mul
        current_range = self.aggro_range + range_add if self.role == 'RANGED' else self.aggro_range
        
        if regen_rate > 0 and self.current_hp < self.max_hp:
            self.current_hp += self.max_hp * regen_rate / 60
            if self.current_hp > self.max_hp: self.current_hp = self.max_hp

        if self.cooldown > 0: self.cooldown -= 1
        else:
            target = None
            if self.role == 'MELEE':
                if self.state == 'IDLE':
                    closest = None; min_dist = current_range
                    for e in enemies:
                        dist = math.sqrt((e.x - self.anchor_x)**2 + (e.y - self.anchor_y)**2)
                        if dist < min_dist: closest = e; min_dist = dist
                    if closest: self.target = closest; self.state = 'CHASE'
                elif self.state == 'CHASE':
                    if not self.target or self.target.current_hp <= 0: self.target = None; self.state = 'RETURN'
                    else:
                        dist_to_target = math.sqrt((self.target.x - self.x)**2 + (self.target.y - self.y)**2)
                        if dist_to_target <= self.attack_range:
                            if self.cooldown > 0: self.cooldown -= 1
                            else:
                                self.cooldown = current_cooldown_max; self.is_attacking = True; self.slash_timer = 15
                                self.slash_angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
                                
                                # Play Sound
                                sound_manager.play("attack_melee")

                                is_crit = False
                                dmg = current_damage
                                if random.random() < crit_rate:
                                    is_crit = True; dmg *= 1.5
                                for e in enemies:
                                    d = math.sqrt((e.x - self.x)**2 + (e.y - self.y)**2)
                                    if d <= self.attack_range + 30: e.take_damage(dmg)
                        else:
                            dx = self.target.x - self.x; dy = self.target.y - self.y
                            dist = math.sqrt(dx**2 + dy**2)
                            self.x += (dx/dist) * self.move_speed; self.y += (dy/dist) * self.move_speed
                            dist_home = math.sqrt((self.x - self.anchor_x)**2 + (self.y - self.anchor_y)**2)
                            if dist_home > current_range * 1.5: self.target = None; self.state = 'RETURN'
                elif self.state == 'RETURN':
                    dx = self.anchor_x - self.x; dy = self.anchor_y - self.y
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist < self.move_speed:
                        self.x, self.y = self.anchor_x, self.anchor_y; self.state = 'IDLE'
                        if self.current_hp < self.max_hp: self.current_hp += 1
                    else:
                        self.x += (dx/dist) * self.move_speed; self.y += (dy/dist) * self.move_speed
            else: 
                for e in enemies:
                    if math.sqrt((e.x - self.x)**2 + (e.y - self.y)**2) <= current_range:
                        self.cooldown = current_cooldown_max
                        # Play Sound
                        sound_manager.play("attack_range")
                        
                        is_crit = False
                        dmg = current_damage
                        if random.random() < crit_rate:
                             is_crit = True; dmg *= 1.5
                        projectiles.append(Projectile(self.x, self.y - self.height*0.5 - self.float_offset, e, dmg, self.colors[2], is_crit))
                        self.is_attacking = True; break

    def draw_slash(self, screen):
        if self.slash_timer > 0:
            progress = 1 - (self.slash_timer / 15)
            start_angle = self.slash_angle + 0.8; end_angle = self.slash_angle - 0.8
            current_angle = start_angle + (end_angle - start_angle) * progress
            tip_x = self.x + math.cos(current_angle) * 60
            tip_y = (self.y - self.height//2) + math.sin(current_angle) * 60
            points = [(self.x, self.y - self.height//2)]
            steps = 5
            for i in range(steps + 1):
                t = i / steps
                a = start_angle + (current_angle - start_angle) * t
                px = self.x + math.cos(a) * 60; py = (self.y - self.height//2) + math.sin(a) * 60
                points.append((px, py))
            if len(points) > 2:
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.polygon(s, (255, 255, 200, 150 - int(progress*150)), points)
                screen.blit(s, (0,0))
            pygame.draw.line(screen, (255, 255, 255), (self.x, self.y - self.height//2), (tip_x, tip_y), 3)

    def draw(self, screen):
        is_dead = self.current_hp <= 0
        shadow_r = self.radius * (0.8 if self.floating else 1.0)
        if not is_dead: draw_shadow(screen, self.x, self.y, shadow_r)
        action = 'IDLE'
        if self.state == 'CHASE' or self.state == 'RETURN': action = 'WALK'
        if self.is_attacking: action = 'ATTACK'
        if is_dead: action = 'IDLE'
        draw_animated_humanoid(screen, self.colors, self.x, self.y, self.radius, self.height, 
                               self.anim_timer, action, is_dead, self.floating)
        if not is_dead and self.role == 'MELEE': self.draw_slash(screen)
        if not is_dead:
            if self.current_hp < self.max_hp:
                bar_w = 30; pct = self.current_hp / self.max_hp
                bx, by = self.x - bar_w/2, self.y - self.height - self.float_offset - 10
                pygame.draw.rect(screen, (50,0,0), (bx, by, bar_w, 5))
                pygame.draw.rect(screen, (50,255,50), (bx, by, bar_w * pct, 5))
            if self.star > 1:
                for i in range(self.star):
                    sx = self.x - ((self.star-1)*8) + i*16
                    sy = self.y - self.height - self.float_offset - 25
                    draw_star_shape(screen, COLOR_STAR, sx, sy, 8)
        if is_dead:
            txt = FONT_S.render("復活中...", True, (200,200,200))
            screen.blit(txt, (self.x - txt.get_width()//2, self.y - 40))

# ==========================================
# 6. 商店、卡牌與備戰區
# ==========================================
class Card:
    def __init__(self, name, cost, traits, star_level=1):
        self.name = name; self.cost = cost; self.traits = traits; self.star = star_level
        self.color = COLOR_RARITY.get(cost, (255,255,255))
        config = UNIT_CONFIG.get(name, DEFAULT_CONFIG)
        self.role = config.get('role', 'RANGED')
        self.rect = pygame.Rect(0, 0, 0, 0)

class Shop:
    def __init__(self):
        self.w, self.h = 1100, 220
        # 預先設定位置，防止初始 rect 為空
        self.x = (SCREEN_WIDTH - self.w)//2
        self.y = SCREEN_HEIGHT - self.h - 10
        
        self.cards = []
        self.rect_bg = pygame.Rect(self.x, self.y, self.w, self.h)
        self.rect_xp = pygame.Rect(self.x + 40, self.y + 60, 160, 50)
        self.rect_refresh = pygame.Rect(self.x + 40, self.y + 130, 160, 50)
        self.refresh(3)

    def refresh(self, player_level):
        odds = SHOP_ODDS.get(player_level, SHOP_ODDS[8])
        self.cards = []
        for i in range(5):
            roll = random.randint(1, 100)
            chosen_cost = 1
            cumulative = 0
            for cost_idx, prob in enumerate(odds):
                cumulative += prob
                if roll <= cumulative: chosen_cost = cost_idx + 1; break
            pool = CARD_POOL.get(chosen_cost, CARD_POOL[1])
            card_data = random.choice(pool)
            new_card = Card(card_data[0], chosen_cost, card_data[1])
            
            card_w, card_h = 150, 150
            start_x = self.x + 250
            cx = start_x + i * (card_w + 20)
            cy = self.y + 40
            new_card.rect = pygame.Rect(cx, cy, card_w, card_h)
            
            self.cards.append(new_card)

    def draw(self, screen, gold, level, xp, next_xp):
        draw_chamfered_rect(screen, COLOR_UI_PANEL, self.rect_bg, COLOR_UI_BORDER)
        # XP
        draw_chamfered_rect(screen, COLOR_BTN_XP, self.rect_xp, (100, 150, 255))
        screen.blit(FONT_M.render("購買經驗 (4金)", True, (255,255,255)), (self.rect_xp.x+15, self.rect_xp.y+10))
        screen.blit(FONT_S.render(f"Lv.{level}  {xp}/{next_xp}", True, (200,200,200)), (self.rect_xp.x, self.rect_xp.y-20))
        bw, bh = 160, 4
        pygame.draw.rect(screen, (50,50,50), (self.rect_xp.x, self.rect_xp.y-5, bw, bh))
        if next_xp > 0:
            fill = min(1.0, xp/next_xp) * bw
            pygame.draw.rect(screen, COLOR_XP_BAR, (self.rect_xp.x, self.rect_xp.y-5, fill, bh))
        # Refresh
        draw_chamfered_rect(screen, COLOR_BTN_REFRESH, self.rect_refresh, (255, 100, 100))
        screen.blit(FONT_M.render("刷新商店 (2金)", True, (255,255,255)), (self.rect_refresh.x+15, self.rect_refresh.y+10))
        # Odds
        odds = SHOP_ODDS.get(level, SHOP_ODDS[8])
        odds_text = f"機率: {odds[0]}% / {odds[1]}% / {odds[2]}% / {odds[3]}% / {odds[4]}%"
        screen.blit(FONT_S.render(odds_text, True, (180, 180, 180)), (self.x + 250, self.y + 15))
        # Cards
        mx, my = pygame.mouse.get_pos()
        card_w, card_h = 150, 150; start_x = self.x + 250 
        for i, card in enumerate(self.cards):
            if not card: continue
            cx, cy = start_x + i * (card_w + 20), self.y + 40
            card.rect = pygame.Rect(cx, cy, card_w, card_h) # Update rect
            is_hover = card.rect.collidepoint((mx, my))
            draw_y = cy - 5 if is_hover else cy
            border_c = (255, 255, 255) if is_hover else card.color
            draw_chamfered_rect(screen, (40,40,60), (cx, draw_y, card_w, card_h), border_c)
            draw_card_portrait(screen, cx + 10, draw_y + 40, card_w - 20, card_h - 75, card.name)
            screen.blit(FONT_M.render(card.name, True, (255,255,255)), (cx+10, draw_y+10))
            
            trait_text = f"{card.traits[0]}"
            if len(card.traits) > 1: trait_text += f" / {card.traits[1]}"
            
            role_txt = "近戰" if card.role == 'MELEE' else "遠程"
            screen.blit(FONT_S.render(trait_text, True, (180,180,180)), (cx+10, draw_y+card_h-40))
            screen.blit(FONT_S.render(role_txt, True, (200,200,200)), (cx+10, draw_y+card_h-20))
            screen.blit(FONT_L.render(f"${card.cost}", True, (255,215,0)), (cx+card_w-30, draw_y+card_h-30))

class Bench:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.slots = [None] * 9
        self.slot_size = 90
        self.padding = 15
        self.width = 9 * (self.slot_size + self.padding) + self.padding
        self.rect = pygame.Rect(x, y, self.width, self.slot_size + 2*self.padding)

    def add_card(self, card):
        for i in range(9):
            if self.slots[i] is None:
                self.slots[i] = card
                return True
        return False

    def draw(self, screen):
        draw_chamfered_rect(screen, COLOR_UI_PANEL, self.rect, COLOR_UI_BORDER)
        for i in range(9):
            sx = self.x + self.padding + i * (self.slot_size + self.padding)
            sy = self.y + self.padding
            slot_rect = pygame.Rect(sx, sy, self.slot_size, self.slot_size)
            pygame.draw.rect(screen, COLOR_BENCH_SLOT, slot_rect)
            pygame.draw.rect(screen, (50, 60, 70), slot_rect, 1)
            card = self.slots[i]
            if card:
                draw_card_portrait(screen, sx+5, sy+5, self.slot_size-10, self.slot_size-10, card.name)
                if card.star > 1:
                    star_x = sx + self.slot_size // 2
                    star_y = sy + 15
                    draw_star_shape(screen, COLOR_STAR, star_x, star_y, 8)
                    if card.star == 3:
                         draw_star_shape(screen, COLOR_STAR, star_x-10, star_y+5, 6)
                         draw_star_shape(screen, COLOR_STAR, star_x+10, star_y+5, 6)

    def get_clicked_slot(self, pos):
        for i in range(9):
            sx = self.x + self.padding + i * (self.slot_size + self.padding)
            sy = self.y + self.padding
            if pygame.Rect(sx, sy, self.slot_size, self.slot_size).collidepoint(pos): return i
        return None

# ==========================================
# 7. 遊戲主程式
# ==========================================
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("七大罪：魔神防線 (Step 69: ESC Key Implemented)")
        self.clock = pygame.time.Clock()
        self.sm = SoundManager()
        
        self.enemies = []; self.units = []; self.projectiles = []
        self.decorations = self.generate_decorations()
        
        self.gold = 5; 
        self.hp = 100; self.level = 3; self.xp = 0
        self.xp_table = {3: 6, 4: 10, 5: 20, 6: 36, 7: 56, 8: 999}
        
        self.shop = Shop()
        
        # --- 修正備戰區位置：緊貼 UI 頂部 ---
        self.bench = Bench((SCREEN_WIDTH - 1000)//2, UI_SPLIT_Y + 10) 
        
        # --- 修正商店位置：緊貼底部 ---
        self.shop.y = SCREEN_HEIGHT - self.shop.h - 10
        self.shop.rect_bg = pygame.Rect(self.shop.x, self.shop.y, self.shop.w, self.shop.h)
        self.shop.rect_xp.y = self.shop.y + 60
        self.shop.rect_refresh.y = self.shop.y + 130
        
        self.bg_surface = self.create_background()
        
        self.state = "MENU" 
        self.previous_state = "PLANNING"
        self.last_game_state = "PLANNING" # 新增：記錄暫停前的遊戲狀態
        self.wave = 1
        self.enemies_to_spawn = []; self.spawn_timer = 0
        self.message = ""; self.message_timer = 0; self.frame_count = 0
        
        self.dragging_obj = None; self.drag_source = None; self.drag_index = -1
        self.rect_start = pygame.Rect(SCREEN_WIDTH//2 - 100, 20, 200, 60)
        # 出售區移到右下角
        self.rect_sell = pygame.Rect(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 150, 200, 120)
        self.rect_gear = pygame.Rect(SCREEN_WIDTH - 60, 20, 40, 40)
        
        self.active_traits = {}
        
        self.rect_settings_panel = pygame.Rect((SCREEN_WIDTH-500)//2, (SCREEN_HEIGHT-400)//2, 500, 400)
        self.rect_settings_back = pygame.Rect((SCREEN_WIDTH-200)//2, (SCREEN_HEIGHT-400)//2 + 320, 200, 50)
        self.rect_slider_vol = pygame.Rect((SCREEN_WIDTH-300)//2, (SCREEN_HEIGHT-400)//2 + 100, 300, 10)
        self.rect_slider_bright = pygame.Rect((SCREEN_WIDTH-300)//2, (SCREEN_HEIGHT-400)//2 + 200, 300, 10)
        self.volume = 0.5; self.brightness = 1.0; self.dragging_slider = None
        self.brightness_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.brightness_surface.fill((0,0,0))

        self.menu_bg_surface = self.create_menu_background()
        self.menu_hero = Unit(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 + 100, Card("梅利奧達斯", 5, ["魔神族", "七大罪"]), star_level=3)
        self.menu_villain = Unit(SCREEN_WIDTH * 2 // 3, SCREEN_HEIGHT // 2 + 100, Card("紅魔族", 1, ["魔神族", "低級魔族"]), star_level=3)
        self.menu_villain.slash_angle = math.pi
        
        btn_w, btn_h = 240, 70
        btn_x = SCREEN_WIDTH // 2 - btn_w // 2
        start_y = SCREEN_HEIGHT // 2 + 180
        self.rect_menu_start = pygame.Rect(btn_x, start_y, btn_w, btn_h)
        self.rect_menu_settings = pygame.Rect(btn_x, start_y + btn_h + 20, btn_w, btn_h)
        self.rect_menu_exit = pygame.Rect(btn_x, start_y + 2 * (btn_h + 20), btn_w, btn_h)

        p_w, p_h = 400, 300
        p_x, p_y = (SCREEN_WIDTH - p_w)//2, (SCREEN_HEIGHT - p_h)//2
        self.rect_pause_panel = pygame.Rect(p_x, p_y, p_w, p_h)
        self.rect_pause_resume = pygame.Rect(p_x + 50, p_y + 50, 300, 50)
        self.rect_pause_settings = pygame.Rect(p_x + 50, p_y + 120, 300, 50)
        self.rect_pause_title = pygame.Rect(p_x + 50, p_y + 190, 300, 50)

        self.rect_gameover_title = pygame.Rect(p_x + 50, p_y + 120, 300, 50)

    def generate_decorations(self):
        decs = []
        for _ in range(300):
            rx = random.randint(0, SCREEN_WIDTH)
            ry = random.randint(0, SCREEN_HEIGHT)
            safe = True
            for p in ALL_PATH_POINTS:
                if math.sqrt((rx-p[0])**2 + (ry-p[1])**2) < PATH_WIDTH + 30: safe = False; break
            if safe: decs.append(Decoration(rx, ry, random.choice(['tree', 'tree', 'rock'])))
        decs.sort(key=lambda d: d.y)
        return decs

    def create_background(self):
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        bg.fill(COLOR_BG_DARK)
        play_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT) 
        pygame.draw.rect(bg, COLOR_GRASS_BASE, play_rect)
        for _ in range(15000):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(bg, COLOR_GRASS_NOISE, (x, y), 2)
        for path in [PATH_LEFT, PATH_RIGHT]:
            if len(path) > 1:
                p_base = [(p[0], p[1]+6) for p in path]
                pygame.draw.lines(bg, COLOR_PATH_DIRT, False, p_base, PATH_WIDTH+8)
                for p in p_base: draw_smooth_circle(bg, COLOR_PATH_DIRT, (p[0], p[1]), (PATH_WIDTH+8)/2)
                pygame.draw.lines(bg, COLOR_PATH_SAND, False, path, PATH_WIDTH)
                for p in path: draw_smooth_circle(bg, COLOR_PATH_SAND, (p[0], p[1]), PATH_WIDTH/2)
        return bg

    def create_menu_background(self):
        bg = self.create_background()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        bg.blit(overlay, (0, 0))
        return bg

    def show_message(self, text): self.message = text; self.message_timer = 60

    def calculate_synergies(self):
        counts = {}
        unique_units = set()
        for u in self.units:
            if u.data.name not in unique_units:
                unique_units.add(u.data.name)
                for trait in u.data.traits:
                    counts[trait] = counts.get(trait, 0) + 1
        low_demon_count = 0
        for u in self.units:
            if "低級魔族" in u.data.traits: low_demon_count += 1
        if low_demon_count > 0: counts["低級魔族"] = low_demon_count
        self.active_traits = counts

    def draw_synergy_panel(self, screen):
        panel_x = 30; panel_y = 100
        mouse_pos = pygame.mouse.get_pos()
        sorted_traits = sorted(TRAIT_DATA.items(), key=lambda x: (x[1]['type'] != 'race', self.active_traits.get(x[0], 0)), reverse=False)
        sorted_traits.sort(key=lambda x: self.active_traits.get(x[0], 0) == 0)
        active_list = [t for t in sorted_traits if self.active_traits.get(t[0], 0) > 0]
        
        for i, (trait_name, data) in enumerate(active_list):
            py = panel_y + i * 60
            count = self.active_traits.get(trait_name, 0)
            is_active = count >= data['breakpoints'][0]
            color = TRAIT_COLORS.get(trait_name, (100, 100, 100))
            if not is_active: color = tuple(c//2 for c in color)
            bg_rect = pygame.Rect(panel_x, py, 50, 50)
            if bg_rect.collidepoint(mouse_pos): draw_tooltip(screen, panel_x + 60, py, trait_name, count, data)
            draw_hexagon(screen, color, (panel_x + 25, py + 25), 25)
            initial = trait_name[0]
            txt_init = FONT_M.render(initial, True, (255,255,255))
            screen.blit(txt_init, (panel_x + 16, py + 15))
            txt_count = FONT_S.render(f"{count}", True, (255, 255, 255))
            screen.blit(txt_count, (panel_x + 18, py + 55))

    def start_round(self):
        if self.state == "PLANNING":
            self.state = "COMBAT"
            self.enemies_to_spawn = []
            count = 2 + self.wave
            for u in self.units: u.revive()
            
            enemy_type = "紅魔族"
            if self.wave <= 2: enemy_type = "小惡魔"
            elif self.wave >= 5: enemy_type = random.choice(["紅魔族", "灰魔族", "聖騎士"])
            
            wave_hp = (self.wave - 1) * 20
            for _ in range(count):
                path = random.choice([PATH_LEFT, PATH_RIGHT])
                self.enemies_to_spawn.append(Enemy(path, 1.2, wave_hp, enemy_type))
            self.show_message(f"第 {self.wave} 波 開始!")

    def end_round(self):
        self.state = "PLANNING"; self.wave += 1
        interest = min(self.gold // 10, 5); income = 5 + interest; self.gold += income
        low_demon_bonus = 0
        if self.active_traits.get("低級魔族", 0) >= 2:
            low_demon_bonus = self.active_traits.get("低級魔族", 0)
            self.gold += low_demon_bonus
        if self.level < 8:
            self.xp += 2; 
            if self.xp >= self.xp_table[self.level]: self.xp -= self.xp_table[self.level]; self.level += 1
        msg = f"回合結束! 收入: +{income}"
        if low_demon_bonus > 0: msg += f" (魔族+{low_demon_bonus})"
        self.show_message(msg); self.shop.refresh(self.level)

    def check_upgrades(self, name):
        for star in [1, 2]:
            candidates = []
            for u in self.units:
                if u.data.name == name and u.star == star: candidates.append(u)
            for i, card in enumerate(self.bench.slots):
                if card and card.name == name and card.star == star: candidates.append((i, card))
            if len(candidates) >= 3:
                target = None
                map_candidates = [c for c in candidates if isinstance(c, Unit)]
                if map_candidates:
                    target = map_candidates[0]
                    to_process = candidates[:3]
                    target.star += 1
                    target.__init__(target.x, target.y, target.data, target.star) 
                    for obj in to_process:
                        if obj == target: continue
                        if isinstance(obj, Unit): self.units.remove(obj)
                        else: self.bench.slots[obj[0]] = None
                else:
                    bench_candidates = [c for c in candidates if isinstance(c, tuple)]
                    target_idx, target_card = bench_candidates[0]
                    target_card.star += 1
                    to_remove = bench_candidates[1:3]
                    for idx, c in to_remove: self.bench.slots[idx] = None
                self.show_message(f"{name} 升級為 {star+1} 星!")
                self.sm.play("buy")
                self.check_upgrades(name); break

    def check_can_deploy(self, x, y, role):
        if y > UI_SPLIT_Y: return False
        closest_dist = min([math.hypot(x-p[0], y-p[1]) for p in ALL_PATH_POINTS])
        if role == 'MELEE':
            if closest_dist > PATH_WIDTH // 2 + 5: return False 
        else: 
            if closest_dist < PATH_WIDTH // 2 + 5: return False
        for u in self.units:
            if self.drag_source == 'map' and self.units.index(u) == self.drag_index: continue
            if math.hypot(x-u.x, y-u.y) < 30: return False
        return True

    def handle_input(self):
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            
            # --- Insert this block ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state in ["PLANNING", "COMBAT"]:
                        self.sm.play("click")
                        self.last_game_state = self.state
                        self.previous_state = self.state
                        self.state = "PAUSED"
                    elif self.state == "PAUSED":
                        self.sm.play("click")
                        self.state = self.last_game_state
                    elif self.state == "SETTINGS":
                        self.sm.play("click")
                        self.state = self.previous_state
            # -------------------------
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # SETTINGS
                    if self.state == "SETTINGS":
                        knob_r = 10
                        if self.rect_slider_vol.collidepoint((mx, my)): self.dragging_slider = 'vol'
                        elif self.rect_slider_bright.collidepoint((mx, my)): self.dragging_slider = 'bright'
                        if self.rect_settings_back.collidepoint((mx, my)):
                            self.state = self.previous_state 
                            self.sm.play("click")
                        continue
                    # MENU
                    if self.state == "MENU":
                        if self.rect_menu_start.collidepoint((mx, my)): 
                            self.state = "PLANNING"
                            self.sm.play("click")
                        elif self.rect_menu_settings.collidepoint((mx, my)): 
                            self.previous_state = "MENU"
                            self.state = "SETTINGS"
                            self.sm.play("click")
                        elif self.rect_menu_exit.collidepoint((mx, my)): 
                            pygame.quit(); sys.exit()
                        continue
                    # PAUSED
                    if self.state == "PAUSED":
                        if self.rect_pause_resume.collidepoint((mx, my)):
                            self.state = self.last_game_state # 回到暫停前的狀態
                            self.sm.play("click")
                        elif self.rect_pause_settings.collidepoint((mx, my)):
                             self.previous_state = "PAUSED"
                             self.state = "SETTINGS"
                             self.sm.play("click")
                        elif self.rect_pause_title.collidepoint((mx, my)):
                            self.sm.play("click")
                            self.__init__(); self.state = "MENU"
                        continue
                    # GAME OVER
                    if self.state == "GAME_OVER":
                        if self.rect_pause_title.collidepoint((mx, my)):
                             self.sm.play("click")
                             self.__init__(); self.state = "MENU"
                        continue

                    # GAME
                    if self.rect_gear.collidepoint((mx, my)):
                        self.sm.play("click")
                        self.last_game_state = self.state 
                        self.previous_state = self.state
                        self.state = "PAUSED"; continue

                    if self.rect_start.collidepoint((mx, my)): 
                        self.sm.play("click")
                        self.start_round(); continue
                    if self.shop.rect_xp.collidepoint((mx, my)):
                        if self.level < 8 and self.gold >= 4:
                            self.gold -= 4; self.xp += 4
                            self.sm.play("buy")
                            if self.xp >= self.xp_table[self.level]: self.xp -= self.xp_table[self.level]; self.level += 1
                        else: self.show_message("無法購買經驗"); continue
                    if self.shop.rect_refresh.collidepoint((mx, my)):
                        if self.gold >= 2: 
                            self.gold -= 2; self.shop.refresh(self.level)
                            self.sm.play("refresh")
                        else: self.show_message("金幣不足"); continue
                    
                    if self.state == "PLANNING":
                        for i, card in enumerate(self.shop.cards):
                            if card and card.rect and card.rect.collidepoint((mx, my)):
                                if self.gold >= card.cost:
                                    self.dragging_obj = card; self.drag_source = 'shop'; self.drag_index = i
                                    self.sm.play("click")
                                else: self.show_message("金幣不足")
                                break
                    
                    if not self.dragging_obj:
                        idx = self.bench.get_clicked_slot((mx, my))
                        if idx is not None and self.bench.slots[idx]:
                            self.dragging_obj = self.bench.slots[idx]
                            self.drag_source = 'bench'; self.drag_index = idx; self.bench.slots[idx] = None
                            self.sm.play("click")

                    if not self.dragging_obj and self.state == "PLANNING":
                        if my < UI_SPLIT_Y:
                            for i, u in enumerate(self.units):
                                if math.sqrt((mx-u.x)**2 + (my-u.y)**2) < u.radius + 5:
                                    self.dragging_obj = u.data
                                    self.dragging_obj.star = u.star 
                                    self.drag_source = 'map'; self.drag_index = i; self.units.pop(i); 
                                    self.sm.play("click")
                                    break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.state == "SETTINGS":
                        self.dragging_slider = None
                        continue

                    if self.dragging_obj:
                        placed = False
                        
                        if self.rect_sell.collidepoint((mx, my)):
                            self.gold += self.dragging_obj.cost; self.show_message("已出售"); placed = True 
                            self.sm.play("sell")
                        elif my < UI_SPLIT_Y:
                            if len(self.units) < self.level:
                                role = self.dragging_obj.role
                                if self.check_can_deploy(mx, my, role):
                                    new_unit = Unit(mx, my, self.dragging_obj, self.dragging_obj.star)
                                    self.units.append(new_unit)
                                    if self.drag_source == 'shop': 
                                        self.gold -= self.dragging_obj.cost; self.shop.cards[self.drag_index] = None
                                        self.sm.play("buy")
                                        if self.active_traits.get("低級魔族", 0) >= 2 and "低級魔族" in self.dragging_obj.traits:
                                            self.gold += 1; self.show_message("+1金幣 (魔族)")
                                    placed = True
                                    self.check_upgrades(new_unit.data.name)
                                else: 
                                    if role == 'MELEE': self.show_message("近戰必須放路上!")
                                    else: self.show_message("遠程必須放路邊!")
                            else: self.show_message("人口已滿!")
                        
                        if not placed:
                            if self.drag_source == 'shop':
                                if self.bench.add_card(self.dragging_obj):
                                    self.gold -= self.dragging_obj.cost; self.shop.cards[self.drag_index] = None; placed = True
                                    self.sm.play("buy")
                                    self.check_upgrades(self.dragging_obj.name)
                            elif self.drag_source == 'bench':
                                target_slot = self.bench.get_clicked_slot((mx, my))
                                if target_slot is not None and self.bench.slots[target_slot] is None:
                                    self.bench.slots[target_slot] = self.dragging_obj
                                else: self.bench.slots[self.drag_index] = self.dragging_obj
                                placed = True
                            elif self.drag_source == 'map':
                                if self.bench.add_card(self.dragging_obj): 
                                    placed = True; self.check_upgrades(self.dragging_obj.name)
                                else: self.gold += self.dragging_obj.cost; self.show_message("已出售"); placed = True; self.sm.play("sell")
                        
                        self.calculate_synergies()
                        self.dragging_obj = None; self.drag_source = None; self.drag_index = -1

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if self.dragging_obj:
                    if self.drag_source != 'shop': self.gold += self.dragging_obj.cost; self.show_message("已出售"); self.sm.play("sell")
                    if self.drag_source == 'bench': self.bench.slots[self.drag_index] = self.dragging_obj
                    self.dragging_obj = None

    def update(self):
        self.frame_count += 1
        
        if self.state == "SETTINGS" and self.dragging_slider:
            mx, my = pygame.mouse.get_pos()
            if self.dragging_slider == 'vol':
                val = (mx - self.rect_slider_vol.x) / self.rect_slider_vol.width
                self.volume = max(0.0, min(1.0, val))
                self.sm.set_volume(self.volume)
            elif self.dragging_slider == 'bright':
                val = (mx - self.rect_slider_bright.x) / self.rect_slider_bright.width
                self.brightness = max(0.0, min(1.0, val))
            return

        if self.state == "MENU":
            self.menu_hero.anim_timer += 1; self.menu_villain.anim_timer += 1
            if self.frame_count % 40 == 0:
                self.menu_hero.is_attacking = True; self.menu_hero.slash_timer = 15
                self.menu_villain.is_attacking = True; self.menu_villain.slash_timer = 15
            else:
                self.menu_hero.is_attacking = False; self.menu_villain.is_attacking = False
            if self.menu_hero.slash_timer > 0: self.menu_hero.slash_timer -= 1
            if self.menu_villain.slash_timer > 0: self.menu_villain.slash_timer -= 1
            return

        if self.state == "PAUSED" or self.state == "GAME_OVER" or self.state == "SETTINGS": return

        self.calculate_synergies()
        if self.state == "COMBAT":
            self.spawn_timer += 1
            if self.spawn_timer >= 120 and self.enemies_to_spawn:
                self.spawn_timer = 0; self.enemies.append(self.enemies_to_spawn.pop(0))
            if not self.enemies_to_spawn and not self.enemies: self.end_round()

        for u in self.units: 
            u.update(self.enemies, self.projectiles, self.active_traits, self.sm)
            
        for p in self.projectiles: p.update()
        self.projectiles = [p for p in self.projectiles if p.active]
        for e in self.enemies: e.move(self.units)
        alive_e = []
        for e in self.enemies:
            if e.current_hp <= 0: 
                self.gold += 1; self.sm.play("dead")
            elif e.finished:
                self.hp -= e.damage
                if self.hp <= 0:
                    self.hp = 0
                    self.state = "GAME_OVER"
                    self.sm.play("game_over")
            
            if e.current_hp > 0 and not e.finished: 
                alive_e.append(e)
                
        self.enemies = alive_e
        if self.message_timer > 0: self.message_timer -= 1

    def draw_menu(self):
        self.screen.blit(self.menu_bg_surface, (0, 0))
        for dec in self.decorations: dec.draw(self.screen, self.frame_count)
        self.menu_hero.draw(self.screen); self.menu_villain.draw(self.screen)
        
        title_text = "七大罪：魔神防線"
        title_surf = FONT_TITLE.render(title_text, True, COLOR_STAR)
        title_shadow = FONT_TITLE.render(title_text, True, (0, 0, 0))
        cx = SCREEN_WIDTH // 2 - title_surf.get_width() // 2
        cy = SCREEN_HEIGHT // 4
        self.screen.blit(title_shadow, (cx + 4, cy + 4))
        self.screen.blit(title_surf, (cx, cy))
        
        mx, my = pygame.mouse.get_pos()
        buttons = [(self.rect_menu_start, "開始遊戲"), (self.rect_menu_settings, "設定"), (self.rect_menu_exit, "離開遊戲")]
        for rect, text in buttons:
            is_hover = rect.collidepoint((mx, my))
            bg_color = COLOR_BTN_MENU_HOVER if is_hover else COLOR_BTN_MENU
            border_color = COLOR_UI_HIGHLIGHT if is_hover else COLOR_UI_BORDER
            draw_chamfered_rect(self.screen, bg_color, rect, border_color, border_width=3)
            txt_surf = FONT_L.render(text, True, (255, 255, 255))
            self.screen.blit(txt_surf, (rect.centerx - txt_surf.get_width() // 2, rect.centery - txt_surf.get_height() // 2))

    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_PAUSE_OVERLAY)
        self.screen.blit(overlay, (0,0))
        
        draw_chamfered_rect(self.screen, COLOR_UI_PANEL, self.rect_pause_panel, COLOR_UI_BORDER, border_width=3)
        title = FONT_L.render("暫停", True, (255, 255, 255))
        self.screen.blit(title, (self.rect_pause_panel.centerx - title.get_width()//2, self.rect_pause_panel.y + 15))
        
        mx, my = pygame.mouse.get_pos()
        buttons = [(self.rect_pause_resume, "繼續遊戲"), (self.rect_pause_settings, "設定"), (self.rect_pause_title, "返回標題")]
        for rect, text in buttons:
            is_hover = rect.collidepoint((mx, my))
            bg = COLOR_BTN_HOVER if is_hover else COLOR_BTN_GENERIC
            draw_chamfered_rect(self.screen, bg, rect)
            txt_s = FONT_M.render(text, True, (255,255,255))
            self.screen.blit(txt_s, (rect.centerx - txt_s.get_width()//2, rect.centery - txt_s.get_height()//2))

    def draw_settings(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_PAUSE_OVERLAY)
        self.screen.blit(overlay, (0,0))
        
        draw_chamfered_rect(self.screen, COLOR_UI_PANEL, self.rect_settings_panel, COLOR_UI_BORDER, border_width=3)
        title = FONT_L.render("設定", True, (255, 255, 255))
        self.screen.blit(title, (self.rect_settings_panel.centerx - title.get_width()//2, self.rect_settings_panel.y + 15))

        # Volume
        vol_label = FONT_M.render(f"音量: {int(self.volume*100)}%", True, (200,200,200))
        self.screen.blit(vol_label, (self.rect_slider_vol.x, self.rect_slider_vol.y - 30))
        pygame.draw.rect(self.screen, COLOR_SLIDER_BG, self.rect_slider_vol, border_radius=5)
        fill_w = int(self.rect_slider_vol.width * self.volume)
        pygame.draw.rect(self.screen, COLOR_SLIDER_FILL, (self.rect_slider_vol.x, self.rect_slider_vol.y, fill_w, self.rect_slider_vol.height), border_radius=5)
        knob_x = self.rect_slider_vol.x + fill_w
        pygame.draw.circle(self.screen, COLOR_SLIDER_KNOB, (knob_x, self.rect_slider_vol.centery), 10)

        # Brightness
        bri_label = FONT_M.render(f"亮度: {int(self.brightness*100)}%", True, (200,200,200))
        self.screen.blit(bri_label, (self.rect_slider_bright.x, self.rect_slider_bright.y - 30))
        pygame.draw.rect(self.screen, COLOR_SLIDER_BG, self.rect_slider_bright, border_radius=5)
        fill_w = int(self.rect_slider_bright.width * self.brightness)
        pygame.draw.rect(self.screen, COLOR_SLIDER_FILL, (self.rect_slider_bright.x, self.rect_slider_bright.y, fill_w, self.rect_slider_bright.height), border_radius=5)
        knob_x = self.rect_slider_bright.x + fill_w
        pygame.draw.circle(self.screen, COLOR_SLIDER_KNOB, (knob_x, self.rect_slider_bright.centery), 10)

        # Back
        mx, my = pygame.mouse.get_pos()
        is_hover = self.rect_settings_back.collidepoint((mx, my))
        bg = COLOR_BTN_HOVER if is_hover else COLOR_BTN_GENERIC
        draw_chamfered_rect(self.screen, bg, self.rect_settings_back)
        txt_s = FONT_M.render("返回", True, (255,255,255))
        self.screen.blit(txt_s, (self.rect_settings_back.centerx - txt_s.get_width()//2, self.rect_settings_back.centery - txt_s.get_height()//2))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_GAMEOVER_OVERLAY)
        self.screen.blit(overlay, (0,0))
        
        title = FONT_TITLE.render("戰敗", True, (255, 50, 50))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//3))
        
        mx, my = pygame.mouse.get_pos()
        rect = self.rect_pause_title 
        rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100)
        
        is_hover = rect.collidepoint((mx, my))
        bg = COLOR_BTN_HOVER if is_hover else COLOR_BTN_GENERIC
        draw_chamfered_rect(self.screen, bg, rect, COLOR_UI_BORDER, 2)
        txt_s = FONT_L.render("返回標題", True, (255,255,255))
        self.screen.blit(txt_s, (rect.centerx - txt_s.get_width()//2, rect.centery - txt_s.get_height()//2))

    def draw_gear_icon(self, surface, color, center, radius):
        cx, cy = center
        pygame.draw.circle(surface, color, center, radius, 4)
        for i in range(8):
            angle = math.radians(i * 45)
            sx = cx + math.cos(angle) * (radius - 5); sy = cy + math.sin(angle) * (radius - 5)
            ex = cx + math.cos(angle) * (radius + 5); ey = cy + math.sin(angle) * (radius + 5)
            pygame.draw.line(surface, color, (sx, sy), (ex, ey), 6)
        pygame.draw.circle(surface, color, center, 4)

    def draw(self):
        if self.state == "MENU": self.draw_menu(); pygame.display.flip(); return

        self.screen.blit(self.bg_surface, (0, 0))
        
        if self.dragging_obj:
            mx, my = pygame.mouse.get_pos()
            if my < UI_SPLIT_Y:
                highlight_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                grid_step = 40
                play_rect = pygame.Rect(MAP_OFFSET_X - 50, MAP_OFFSET_Y - 50, MAP_WIDTH + 100, MAP_HEIGHT + 100)
                role = self.dragging_obj.role
                for x in range(play_rect.left + 20, play_rect.right, grid_step):
                    for y in range(play_rect.top + 20, play_rect.bottom, grid_step):
                        if self.check_can_deploy(x, y, role):
                            draw_smooth_ellipse(highlight_surf, COLOR_RANGE_VALID, (x-15, y-10, 30, 20))
                self.screen.blit(highlight_surf, (0,0))

        render_list = []
        render_list.extend(self.decorations); render_list.extend(self.units); render_list.extend(self.enemies)
        render_list.sort(key=lambda obj: obj.y)
        for obj in render_list: 
            if isinstance(obj, Decoration): obj.draw(self.screen, self.frame_count)
            else: obj.draw(self.screen)
        for p in self.projectiles: p.draw(self.screen)
        
        # UI Background
        ui_bg = pygame.Rect(0, UI_SPLIT_Y, SCREEN_WIDTH, SCREEN_HEIGHT - UI_SPLIT_Y)
        ui_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - UI_SPLIT_Y), pygame.SRCALPHA)
        ui_surf.fill(COLOR_UI_PANEL) 
        self.screen.blit(ui_surf, (0, UI_SPLIT_Y))
        pygame.draw.line(self.screen, COLOR_UI_BORDER, (0, UI_SPLIT_Y), (SCREEN_WIDTH, UI_SPLIT_Y), 3)
        
        next_xp = self.xp_table.get(self.level, 999)
        self.shop.draw(self.screen, self.gold, self.level, self.xp, next_xp)
        self.bench.draw(self.screen)
        
        pygame.draw.rect(self.screen, COLOR_SELL_ZONE, self.rect_sell, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_UI_BORDER, self.rect_sell, 2, border_radius=10)
        sell_txt = FONT_L.render("拖曳至此出售", True, (255, 200, 200))
        self.screen.blit(sell_txt, (self.rect_sell.x + 25, self.rect_sell.y + 35))
        
        info = FONT_L.render(f"金幣: {self.gold}   生命: {self.hp}   人口: {len(self.units)}/{self.level}   波次: {self.wave}", True, (255, 255, 255))
        self.screen.blit(info, (20, 20))
        
        self.draw_synergy_panel(self.screen)
        
        is_gear_hover = self.rect_gear.collidepoint(pygame.mouse.get_pos())
        gear_color = (200, 200, 200) if is_gear_hover else (100, 100, 100)
        self.draw_gear_icon(self.screen, gear_color, self.rect_gear.center, 15)

        btn_color = COLOR_BTN_START if self.state == "PLANNING" else COLOR_BTN_START_DIS
        draw_chamfered_rect(self.screen, btn_color, self.rect_start, (200, 255, 200))
        txt_start = FONT_L.render("開始戰鬥" if self.state == "PLANNING" else "戰鬥中...", True, (255, 255, 255))
        self.screen.blit(txt_start, (self.rect_start.x + 40, self.rect_start.y + 10))

        if self.message_timer > 0:
            m = FONT_XL.render(self.message, True, (255, 80, 80))
            m_bg = FONT_XL.render(self.message, True, (0, 0, 0))
            cx, cy = SCREEN_WIDTH//2 - m.get_width()//2, SCREEN_HEIGHT//2 - 100
            for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]: self.screen.blit(m_bg, (cx+dx, cy+dy))
            self.screen.blit(m, (cx, cy))
            
        # --- Fix: 計算 hover_unit ---
        hover_unit = None
        mx, my = pygame.mouse.get_pos()
        # 1. 檢查備戰區
        if my > UI_SPLIT_Y and my < UI_SPLIT_Y + 130:
            idx = self.bench.get_clicked_slot((mx, my))
            if idx is not None and self.bench.slots[idx]:
                card = self.bench.slots[idx]
                hover_unit = Unit(0, 0, card, card.star)
        # 2. 檢查地圖單位
        elif my < UI_SPLIT_Y:
            for u in self.units:
                if math.hypot(mx-u.x, my-u.y) < u.radius + 5:
                    hover_unit = u
                    break
        # ----------------------------

        if hover_unit and not self.dragging_obj:
            draw_unit_tooltip(self.screen, hover_unit, pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

        if self.dragging_obj:
            mx, my = pygame.mouse.get_pos()
            if my < UI_SPLIT_Y:
                temp_u = Unit(mx, my, self.dragging_obj, self.dragging_obj.star)
                temp_u.draw(self.screen)
            else:
                draw_card_portrait(self.screen, mx-40, my-60, 80, 80, self.dragging_obj.name)

        # Apply brightness overlay
        if self.brightness < 1.0:
            self.brightness_surface.set_alpha(int((1.0 - self.brightness) * 255))
            self.screen.blit(self.brightness_surface, (0,0))

        if self.state == "PAUSED": self.draw_pause()
        if self.state == "SETTINGS": self.draw_settings()
        if self.state == "GAME_OVER": self.draw_game_over()

        pygame.display.flip()

    def run(self):
        while True: self.handle_input(); self.update(); self.draw(); self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()