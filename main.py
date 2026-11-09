"""
================================================================================
✨ FESTIVE DIWALI ANIMATION - FESTIVAL OF LIGHTS ✨
================================================================================
A vibrant, cheerful, and polished Python animation celebrating Diwali.
Features:
  - Realistic glowing & flickering Diyas with dynamic light cast
  - Spectacular Fireworks & Rockets with multi-stage spark trails
  - Sparkler Fountains (Diwali Anar) shooting golden cascades
  - Decorative Hanging Toran & Fairy Lights across the top
  - Intricate glowing Rangoli base on a warm terrace floor
  - Elegant golden-glowing "Happy Diwali" greeting with gentle breathing pulse
  - Twinkling night sky starfield
  - Procedural Firework Audio generated dynamically with NumPy (Booms, Whooshes, Crackles)
  - Interactive: Click to launch fireworks, Space for a Grand Finale barrage!
================================================================================
"""

import math
import random
import sys
import time
import pygame

# Try importing numpy for procedural sound synthesis
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


# ==============================================================================
# CONFIGURATION - Feel free to customize text, colors, speeds, and scene details!
# ==============================================================================
CONFIG = {
    # Window & Display
    "WINDOW_WIDTH": 1024,
    "WINDOW_HEIGHT": 720,
    "FPS": 60,
    "WINDOW_TITLE": "✨ Shubh Deepavali - Festival of Lights ✨",
    
    # Audio Settings (Procedural Audio generated via NumPy)
    "ENABLE_SOUND": True,        # Set to False to disable sound
    "AUDIO_VOLUME": 0.65,        # Master sound volume (0.0 to 1.0)
    
    # Greetings & Typography
    "GREETING_MAIN": "Happy Diwali",
    "GREETING_SUB": "May the Divine Light Illuminate Your Life with Joy, Peace & Prosperity",
    "FONT_FAMILY": "georgia",    # 'georgia', 'garamond', 'timesnewroman', or None
    
    # Diyas (Oil Lamps)
    "DIYA_COUNT": 5,             # Number of diyas along the bottom
    "FLAME_SPEED": 1.0,          # Multiplier for flame flicker speed
    "FLAME_SCALE": 1.15,         # Scale of flame size
    "DIYA_GLOW_RADIUS": 140,     # Radius of the warm radial ambient glow
    "DIYA_GLOW_INTENSITY": 0.75, # Warm glow brightness (0.1 - 1.0)
    
    # Fireworks & Rockets
    "AUTO_FIREWORKS": True,
    "FIREWORK_INTERVAL": 1.1,    # Average seconds between automatic firework launches
    "BURST_PARTICLE_COUNT": 110, # Sparks per firework burst
    "GRAVITY": 0.08,             # Downward pull on firework particles
    "DRAG": 0.965,               # Air resistance (slows sparks down smoothly)
    
    # Ambient & Festive Features
    "SHOW_ANAR_FOUNTAINS": True, # Golden sparkler flowerpots on bottom corners
    "SHOW_FAIRY_LIGHTS": True,   # Hanging festive fairy lights / garland at top
    "SHOW_RANGOLI": True,        # Glowing geometric rangoli motif on the terrace
    "STAR_COUNT": 85,            # Twinkling night sky stars
    "FLOATING_SPARKLES": True,   # Ambient glittering dust in the air
    
    # Festive Fireworks Color Palettes (Rich Indian festive tones)
    "PALETTES": [
        [(255, 215, 0), (255, 140, 0), (255, 69, 0)],        # Royal Golden Saffron
        [(255, 20, 147), (255, 105, 180), (255, 240, 245)],  # Radiant Gulabi Pink
        [(0, 245, 255), (30, 144, 255), (147, 112, 219)],    # Peacock Cyan & Royal Blue
        [(50, 205, 50), (124, 252, 0), (255, 255, 160)],     # Emerald & Lime Festivity
        [(255, 69, 0), (255, 165, 0), (255, 255, 255)],      # Marigold Fire & Pure White
        [(186, 85, 211), (255, 215, 0), (255, 255, 255)],    # Regal Purple & Gold
        [(255, 50, 50), (255, 215, 0), (255, 120, 0)],       # Crimson & Amber
    ]
}


# ==============================================================================
# PROCEDURAL AUDIO SYNTHESIZER (NUMPY + PYGAME MIXER)
# ==============================================================================
class ProceduralAudioEngine:
    """
    Synthesizes authentic firework sound effects (booms, rocket whistles, crackles)
    directly in-memory using NumPy mathematical formulas and Pygame sndarray.
    Zero external WAV/MP3 files required!
    """
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.is_active = False
        self.muted = not CONFIG["ENABLE_SOUND"]
        self.volume = CONFIG["AUDIO_VOLUME"]
        
        self.launch_sounds = []
        self.boom_sounds = []
        self.crackle_sounds = []
        
        if not NUMPY_AVAILABLE:
            print("Notice: NumPy not detected. Running in silent mode.")
            return

        try:
            # Initialize Pygame audio mixer with low latency buffer
            pygame.mixer.pre_init(frequency=sample_rate, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            pygame.mixer.set_num_channels(16)
            self.generate_sound_bank()
            self.is_active = True
        except Exception as e:
            print(f"Notice: Audio mixer could not be initialized ({e}). Running in silent mode.")
            self.is_active = False

    def generate_sound_bank(self):
        """Pre-synthesizes randomized audio variations using NumPy."""
        # 1. Rocket Launch Whoosh Sounds (2 variations)
        for _ in range(2):
            snd = self._synthesize_launch_whoosh()
            if snd: self.launch_sounds.append(snd)

        # 2. Firework Explosion Booms (4 variations: deep thuds, rumbles, crackles)
        for i in range(4):
            snd = self._synthesize_explosion_boom(variation=i)
            if snd: self.boom_sounds.append(snd)

        # 3. Sparkling Crackle Sound
        crk = self._synthesize_crackle()
        if crk: self.crackle_sounds.append(crk)

    def _to_stereo_sound(self, mono_samples):
        """Converts floating point mono samples into a 16-bit signed stereo Pygame Sound."""
        # Normalize and clip
        max_val = np.max(np.abs(mono_samples))
        if max_val > 0:
            mono_samples = mono_samples / max_val
            
        int16_samples = (mono_samples * 30000).astype(np.int16)
        stereo_samples = np.column_stack((int16_samples, int16_samples))
        return pygame.sndarray.make_sound(stereo_samples)

    def _synthesize_launch_whoosh(self):
        """Generates an upward pitch-sweep rocket whoosh."""
        duration = random.uniform(0.38, 0.48)
        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        
        # Rising exponential chirp from 220Hz to 850Hz
        freq_start, freq_end = random.uniform(220, 260), random.uniform(750, 900)
        phase = 2 * np.pi * (freq_start * t + 0.5 * (freq_end - freq_start) * (t**2 / duration))
        tone = np.sin(phase)
        
        # White noise layer for thruster air whoosh
        noise = np.random.uniform(-1.0, 1.0, n_samples)
        
        # Smooth attack and decay envelope
        attack_len = int(n_samples * 0.25)
        decay_len = n_samples - attack_len
        envelope = np.concatenate([
            np.linspace(0.0, 1.0, attack_len),
            np.linspace(1.0, 0.0, decay_len) ** 1.5
        ])
        
        audio = (tone * 0.45 + noise * 0.55) * envelope
        snd = self._to_stereo_sound(audio)
        snd.set_volume(self.volume * 0.35)
        return snd

    def _synthesize_explosion_boom(self, variation=0):
        """Generates a deep, punchy atmospheric explosion thump and rumbling burst."""
        duration = random.uniform(0.85, 1.15)
        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        
        # Deep bass thump (pitch drops rapidly from 130Hz to 38Hz)
        f_start, f_end = random.uniform(115, 140), random.uniform(32, 42)
        pitch_drop = 2 * np.pi * (f_start * t + 0.5 * (f_end - f_start) * (t**2 / duration))
        bass_thump = np.sin(pitch_drop) * np.exp(-t * random.uniform(7.0, 10.0))
        
        # Filtered explosive noise body (Brownian / integrated noise)
        raw_noise = np.random.uniform(-1.0, 1.0, n_samples)
        filtered_noise = np.cumsum(raw_noise)
        filtered_noise = filtered_noise - np.mean(filtered_noise)
        max_f = np.max(np.abs(filtered_noise)) + 1e-6
        filtered_noise = filtered_noise / max_f
        
        noise_envelope = np.exp(-t * random.uniform(4.0, 6.0))
        
        # High-frequency sparkling crackle burst for variation
        crackle = np.zeros(n_samples)
        if variation % 2 == 1:
            pop_indices = np.random.randint(0, int(n_samples * 0.65), size=45)
            crackle[pop_indices] = np.random.uniform(-1.0, 1.0, size=len(pop_indices))
            crackle = np.convolve(crackle, np.hanning(15), mode='same')
            
        audio = (bass_thump * 0.55 + filtered_noise * noise_envelope * 0.40 + crackle * 0.15)
        snd = self._to_stereo_sound(audio)
        snd.set_volume(self.volume * 0.85)
        return snd

    def _synthesize_crackle(self):
        """Generates sparkling micro-crackles."""
        duration = 0.5
        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        
        crackle = np.zeros(n_samples)
        pop_indices = np.random.randint(0, n_samples, size=60)
        crackle[pop_indices] = np.random.uniform(-1.0, 1.0, size=len(pop_indices))
        crackle = np.convolve(crackle, np.hanning(10), mode='same')
        crackle = crackle * np.exp(-t * 4.5)
        
        snd = self._to_stereo_sound(crackle)
        snd.set_volume(self.volume * 0.4)
        return snd

    def play_launch(self):
        """Plays a rocket launch sound."""
        if not self.is_active or self.muted or not self.launch_sounds:
            return
        snd = random.choice(self.launch_sounds)
        snd.play()

    def play_explosion(self, ptype="peony"):
        """Plays a firework detonation explosion."""
        if not self.is_active or self.muted or not self.boom_sounds:
            return
        snd = random.choice(self.boom_sounds)
        snd.play()
        
        # If it's a crackling / glitter firework, add a subtle sparkle
        if ptype in ("glitter", "ring") and self.crackle_sounds:
            random.choice(self.crackle_sounds).play()

    def toggle_mute(self):
        """Toggles audio mute on or off."""
        self.muted = not self.muted
        return not self.muted


# ==============================================================================
# HELPER FUNCTIONS & GLOW SURFACES
# ==============================================================================
def create_radial_glow_surface(radius, color, center_alpha=200):
    """
    Creates a pre-rendered radial glow surface with smooth quadratic alpha falloff.
    Used for flame halos, fireworks glow, and fairy lights.
    """
    surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    cx, cy = radius, radius
    
    steps = max(10, min(radius, 40))
    for i in range(steps, 0, -1):
        ratio = i / steps
        current_r = int(radius * ratio)
        falloff = (1.0 - ratio) ** 1.8
        alpha = int(center_alpha * falloff)
        if alpha > 0:
            glow_col = (*color[:3], min(255, alpha))
            pygame.draw.circle(surf, glow_col, (cx, cy), current_r)
            
    return surf


# ==============================================================================
# TWINKLING NIGHT SKY STARS
# ==============================================================================
class Star:
    """A soft twinkling star in the deep midnight sky."""
    def __init__(self, screen_w, screen_h):
        self.x = random.randint(0, screen_w)
        self.y = random.randint(0, int(screen_h * 0.70))
        self.base_brightness = random.uniform(100, 220)
        self.twinkle_speed = random.uniform(1.5, 4.0)
        self.phase = random.uniform(0, math.pi * 2)
        self.size = random.choice([1, 1, 1, 2])
        self.tint = random.choice([
            (255, 255, 255), (255, 248, 220), (230, 240, 255), (255, 230, 180)
        ])

    def draw(self, surface, current_time):
        alpha_factor = 0.5 + 0.5 * math.sin(current_time * self.twinkle_speed + self.phase)
        brightness = int(self.base_brightness * alpha_factor)
        r = int(self.tint[0] * (brightness / 255))
        g = int(self.tint[1] * (brightness / 255))
        b = int(self.tint[2] * (brightness / 255))
        
        if self.size == 1:
            surface.set_at((self.x, self.y), (r, g, b))
        else:
            pygame.draw.circle(surface, (r, g, b), (self.x, self.y), self.size)


# ==============================================================================
# DECORATIVE HANGING FAIRY LIGHTS & GARLAND (TORAN)
# ==============================================================================
class FairyLights:
    """Festive draped garland with glowing, pulsing jewel-toned lights."""
    def __init__(self, screen_w):
        self.screen_w = screen_w
        self.swags = 5
        self.bulbs = []
        self.colors = [
            (255, 60, 60),    # Ruby Red
            (255, 215, 0),    # Golden
            (50, 220, 50),    # Emerald
            (0, 220, 255),    # Cyan
            (255, 140, 0),    # Saffron
            (218, 112, 214),  # Orchid Purple
        ]
        
        swag_width = screen_w / self.swags
        for s in range(self.swags):
            x_start = s * swag_width
            x_end = (s + 1) * swag_width
            bulbs_per_swag = 9
            for b in range(bulbs_per_swag):
                t = (b + 0.5) / bulbs_per_swag
                bx = x_start + t * (x_end - x_start)
                sag = 4.0 * t * (1.0 - t) * 35.0
                by = 12 + sag
                col = self.colors[(s * bulbs_per_swag + b) % len(self.colors)]
                pulse_phase = random.uniform(0, math.pi * 2)
                pulse_speed = random.uniform(2.0, 4.0)
                glow_surf = create_radial_glow_surface(18, col, center_alpha=110)
                self.bulbs.append({
                    'x': bx, 'y': by, 'color': col,
                    'phase': pulse_phase, 'speed': pulse_speed,
                    'glow_surf': glow_surf
                })

    def draw(self, surface, current_time):
        points = []
        for s in range(self.swags):
            swag_width = self.screen_w / self.swags
            x_start = s * swag_width
            x_end = (s + 1) * swag_width
            for step in range(20):
                t = step / 19.0
                x = x_start + t * (x_end - x_start)
                y = 12 + 4.0 * t * (1.0 - t) * 35.0
                points.append((int(x), int(y)))
        
        if len(points) > 1:
            pygame.draw.lines(surface, (60, 50, 40), False, points, 2)

        for b in self.bulbs:
            pulse = 0.65 + 0.35 * math.sin(current_time * b['speed'] + b['phase'])
            surface.blit(b['glow_surf'], (int(b['x'] - 18), int(b['y'] - 18)), special_flags=pygame.BLEND_ADD)
            bright_col = tuple(min(255, int(c * (0.8 + 0.4 * pulse))) for c in b['color'])
            pygame.draw.circle(surface, bright_col, (int(b['x']), int(b['y'])), 4)
            pygame.draw.circle(surface, (255, 255, 240), (int(b['x']), int(b['y'] - 1)), 2)


# ==============================================================================
# DIYA (OIL LAMP) WITH MULTI-LAYERED FLICKERING FLAME & AMBIENT GLOW
# ==============================================================================
class DiyaFlameSpark:
    """A tiny golden spark floating up from a diya's dancing flame."""
    def __init__(self, x, y):
        self.x = x + random.uniform(-3, 3)
        self.y = y
        self.vx = random.uniform(-0.4, 0.4)
        self.vy = random.uniform(-1.2, -2.4)
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.04)
        self.size = random.uniform(1.2, 2.5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(self.life * 255)
        color = (255, int(180 * self.life), int(60 * self.life))
        spark_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(spark_surf, (*color, alpha), (3, 3), max(1, int(self.size * self.life)))
        surface.blit(spark_surf, (int(self.x - 3), int(self.y - 3)), special_flags=pygame.BLEND_ADD)


class Diya:
    """
    An ornate Indian earthen lamp (Diya) with dynamic multi-layered flame,
    rising sparks, and a rich warm pulsating radial ambient glow.
    """
    def __init__(self, x, y, scale=1.0, is_center=False):
        self.x = x
        self.y = y
        self.scale = scale
        self.is_center = is_center
        self.phase = random.uniform(0, math.pi * 2)
        self.sparks = []
        
        glow_r = int(CONFIG["DIYA_GLOW_RADIUS"] * scale)
        warm_amber = (255, 140, 25)
        self.glow_surf = create_radial_glow_surface(glow_r, warm_amber, center_alpha=int(180 * CONFIG["DIYA_GLOW_INTENSITY"]))
        self.glow_radius = glow_r

    def update(self):
        flame_tip_y = self.y - 30 * self.scale
        if random.random() < 0.28:
            self.sparks.append(DiyaFlameSpark(self.x, flame_tip_y))
            
        self.sparks = [s for s in self.sparks if s.update()]

    def draw_bowl(self, surface):
        s = self.scale
        cx, cy = self.x, self.y
        
        bowl_pts = [
            (cx - 36 * s, cy - 2 * s),
            (cx - 38 * s, cy + 4 * s),
            (cx - 24 * s, cy + 18 * s),
            (cx, cy + 22 * s),
            (cx + 24 * s, cy + 18 * s),
            (cx + 38 * s, cy + 4 * s),
            (cx + 36 * s, cy - 2 * s),
            (cx + 12 * s, cy + 2 * s),
            (cx, cy + 3 * s),
            (cx - 12 * s, cy + 2 * s),
        ]
        
        shadow_rect = pygame.Rect(int(cx - 30 * s), int(cy + 19 * s), int(60 * s), int(8 * s))
        shadow_surf = pygame.Surface((int(60 * s), int(8 * s)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (15, 8, 12, 160), shadow_surf.get_rect())
        surface.blit(shadow_surf, shadow_rect.topleft)

        terracotta = (175, 65, 30)
        pygame.draw.polygon(surface, terracotta, bowl_pts)
        
        inner_pts = [
            (cx - 34 * s, cy),
            (cx - 20 * s, cy + 14 * s),
            (cx, cy + 17 * s),
            (cx + 20 * s, cy + 14 * s),
            (cx + 34 * s, cy),
            (cx, cy + 3 * s),
        ]
        pygame.draw.polygon(surface, (140, 45, 20), inner_pts)
        
        pygame.draw.lines(surface, (255, 200, 50), False, bowl_pts[:7], max(1, int(2.5 * s)))
        
        dot_count = 7
        for i in range(dot_count):
            t = (i + 0.5) / dot_count
            dot_x = cx - 32 * s + t * 64 * s
            dot_y = cy + 4 * s + math.sin(t * math.pi) * 8 * s
            pygame.draw.circle(surface, (255, 230, 100), (int(dot_x), int(dot_y)), max(1, int(2 * s)))

    def draw_flame(self, surface, current_time):
        s = self.scale * CONFIG["FLAME_SCALE"]
        spd = CONFIG["FLAME_SPEED"]
        cx = self.x
        base_y = self.y - 2 * self.scale
        
        t = current_time * spd
        tip_offset_x = (math.sin(t * 6.5 + self.phase) * 3.5 + 
                        math.sin(t * 13.0 + self.phase * 2.1) * 1.5) * s
        flicker_h = (math.sin(t * 8.0 + self.phase * 1.5) * 3.0 + 
                     math.cos(t * 17.0 + self.phase) * 1.2) * s
        
        flame_h = (36 * s) + flicker_h
        tip_x = cx + tip_offset_x
        tip_y = base_y - flame_h

        # Outer Flame
        outer_w = 14 * s
        outer_pts = [
            (cx - outer_w, base_y),
            (cx - outer_w * 0.9, base_y - flame_h * 0.35),
            (cx - outer_w * 0.5, base_y - flame_h * 0.70),
            (tip_x, tip_y),
            (cx + outer_w * 0.5, base_y - flame_h * 0.70),
            (cx + outer_w * 0.9, base_y - flame_h * 0.35),
            (cx + outer_w, base_y),
        ]
        pygame.draw.polygon(surface, (255, 80, 10), outer_pts)

        # Middle Flame
        mid_w = 9 * s
        mid_h = flame_h * 0.82
        mid_tip_x = cx + tip_offset_x * 0.75
        mid_tip_y = base_y - mid_h
        mid_pts = [
            (cx - mid_w, base_y),
            (cx - mid_w * 0.85, base_y - mid_h * 0.4),
            (mid_tip_x, mid_tip_y),
            (cx + mid_w * 0.85, base_y - mid_h * 0.4),
            (cx + mid_w, base_y),
        ]
        pygame.draw.polygon(surface, (255, 205, 25), mid_pts)

        # Inner Core Flame
        core_w = 4.5 * s
        core_h = flame_h * 0.55
        core_tip_x = cx + tip_offset_x * 0.4
        core_tip_y = base_y - core_h
        core_pts = [
            (cx - core_w, base_y),
            (core_tip_x, core_tip_y),
            (cx + core_w, base_y),
        ]
        pygame.draw.polygon(surface, (255, 255, 220), core_pts)

        # Flame wick
        pygame.draw.line(surface, (40, 20, 10), (int(cx), int(base_y + 2)), (int(cx), int(base_y - 4 * s)), max(1, int(2 * s)))

    def draw_glow(self, surface, current_time):
        s = self.scale
        spd = CONFIG["FLAME_SPEED"]
        flicker = 0.88 + 0.12 * math.sin(current_time * 7.5 * spd + self.phase)
        
        flame_center_y = self.y - 18 * s
        gx = int(self.x - self.glow_radius)
        gy = int(flame_center_y - self.glow_radius)
        
        surface.blit(self.glow_surf, (gx, gy), special_flags=pygame.BLEND_ADD)

    def draw(self, surface, current_time):
        self.draw_bowl(surface)
        self.draw_flame(surface, current_time)
        for spark in self.sparks:
            spark.draw(surface)


# ==============================================================================
# CELEBRATION FIREWORKS & ROCKET PARTICLES
# ==============================================================================
class FireworkParticle:
    """A colorful glowing spark from a firework explosion with physics and trails."""
    def __init__(self, x, y, color, speed, angle, ptype="peony"):
        self.x = x
        self.y = y
        self.ptype = ptype
        self.color = color
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        if ptype == "willow":
            self.life = random.uniform(1.3, 2.0)
            self.gravity = 0.05
            self.decay = random.uniform(0.012, 0.018)
            self.drag = 0.975
        elif ptype == "ring":
            self.life = random.uniform(0.9, 1.4)
            self.gravity = 0.06
            self.decay = random.uniform(0.018, 0.026)
            self.drag = 0.96
        else:
            self.life = random.uniform(1.0, 1.5)
            self.gravity = CONFIG["GRAVITY"]
            self.decay = random.uniform(0.016, 0.025)
            self.drag = CONFIG["DRAG"]
            
        self.max_life = self.life
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)

        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= self.drag
        self.vy *= self.drag
        self.life -= self.decay
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0:
            return
        
        ratio = max(0.0, self.life / self.max_life)
        alpha = int(255 * ratio)
        
        r = int(self.color[0] * (0.6 + 0.4 * ratio))
        g = int(self.color[1] * (0.5 + 0.5 * ratio))
        b = int(self.color[2] * ratio)
        cur_col = (r, g, b)

        if len(self.trail) > 1:
            for idx, pt in enumerate(self.trail):
                t_ratio = (idx + 1) / len(self.trail) * ratio
                t_alpha = int(120 * t_ratio)
                t_col = (r, g, b, t_alpha)
                t_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(t_surf, t_col, (2, 2), 1)
                surface.blit(t_surf, (int(pt[0] - 2), int(pt[1] - 2)), special_flags=pygame.BLEND_ADD)

        spark_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        radius = max(1, int(2.5 * ratio))
        pygame.draw.circle(spark_surf, (*cur_col, alpha), (4, 4), radius)
        pygame.draw.circle(spark_surf, (255, 255, 255, int(180 * ratio)), (4, 4), max(1, radius - 1))
        surface.blit(spark_surf, (int(self.x - 4), int(self.y - 4)), special_flags=pygame.BLEND_ADD)


class Rocket:
    """A firework rocket that launches upwards, leaving sparks, then bursts."""
    def __init__(self, target_x, target_y, start_x=None, palette=None):
        self.x = start_x if start_x is not None else random.randint(150, CONFIG["WINDOW_WIDTH"] - 150)
        self.y = CONFIG["WINDOW_HEIGHT"]
        self.target_x = target_x
        self.target_y = target_y
        
        distance_y = self.y - self.target_y
        self.vy = -math.sqrt(max(10, 2.0 * 0.12 * distance_y))
        time_to_apex = abs(self.vy) / 0.12
        self.vx = (self.target_x - self.x) / max(1.0, time_to_apex)
        
        self.palette = palette if palette else random.choice(CONFIG["PALETTES"])
        self.exploded = False
        self.trail_sparks = []
        self.ptype = random.choice(["peony", "willow", "ring", "glitter"])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.12
        
        if random.random() < 0.75:
            self.trail_sparks.append({
                'x': self.x + random.uniform(-1.5, 1.5),
                'y': self.y + random.uniform(2, 6),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(0.5, 2.0),
                'life': 1.0,
                'decay': random.uniform(0.04, 0.08)
            })

        for s in self.trail_sparks:
            s['x'] += s['vx']
            s['y'] += s['vy']
            s['life'] -= s['decay']
        self.trail_sparks = [s for s in self.trail_sparks if s['life'] > 0]

        if self.vy >= -0.5 or self.y <= self.target_y:
            self.exploded = True

        return not self.exploded

    def draw(self, surface):
        head_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(head_surf, (255, 250, 180, 240), (4, 4), 3)
        surface.blit(head_surf, (int(self.x - 4), int(self.y - 4)), special_flags=pygame.BLEND_ADD)
        
        for s in self.trail_sparks:
            alpha = int(s['life'] * 220)
            col = (255, int(160 * s['life']), int(40 * s['life']), alpha)
            tsurf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(tsurf, col, (3, 3), max(1, int(2.5 * s['life'])))
            surface.blit(tsurf, (int(s['x'] - 3), int(s['y'] - 3)), special_flags=pygame.BLEND_ADD)

    def explode(self):
        """Creates an explosion of firework sparks."""
        particles = []
        count = CONFIG["BURST_PARTICLE_COUNT"]
        
        if self.ptype == "ring":
            base_col = random.choice(self.palette)
            for i in range(count):
                angle = (i / count) * math.pi * 2
                speed = random.uniform(3.2, 4.0)
                particles.append(FireworkParticle(self.x, self.y, base_col, speed, angle, ptype="ring"))
        else:
            for _ in range(count):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(1.2, 5.0)
                col = random.choice(self.palette)
                particles.append(FireworkParticle(self.x, self.y, col, speed, angle, ptype=self.ptype))
                
        return particles


# ==============================================================================
# SPARKLER FOUNTAIN (DIWALI ANAR / FLOWERPOT)
# ==============================================================================
class AnarSpark:
    """A sizzling crackling spark erupted from a flowerpot fountain."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = -math.pi / 2 + random.uniform(-0.35, 0.35)
        speed = random.uniform(6.0, 13.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.gravity = 0.22
        self.drag = 0.965
        self.life = 1.0
        self.decay = random.uniform(0.018, 0.038)
        self.color = random.choice([
            (255, 245, 200),
            (255, 215, 0),
            (255, 170, 30),
            (255, 120, 20),
        ])
        self.size = random.uniform(1.5, 3.0)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= self.drag
        self.vy *= self.drag
        self.life -= self.decay
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(self.life * 255)
        r, g, b = self.color
        surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(surf, (r, g, b, alpha), (4, 4), max(1, int(self.size * self.life)))
        surface.blit(surf, (int(self.x - 4), int(self.y - 4)), special_flags=pygame.BLEND_ADD)


class AnarFountain:
    """A traditional Diwali earthen flowerpot sparkler (Anar)."""
    def __init__(self, x, y, scale=1.0):
        self.x = x
        self.y = y
        self.scale = scale
        self.sparks = []
        self.nozzle_y = y - 32 * scale
        glow_r = int(75 * scale)
        self.glow_surf = create_radial_glow_surface(glow_r, (255, 180, 50), center_alpha=120)
        self.glow_r = glow_r

    def update(self):
        for _ in range(4):
            self.sparks.append(AnarSpark(self.x + random.uniform(-2, 2), self.nozzle_y))
        self.sparks = [s for s in self.sparks if s.update()]

    def draw(self, surface):
        s = self.scale
        cx, cy = self.x, self.y
        
        cone_pts = [
            (cx - 16 * s, cy),
            (cx - 5 * s, self.nozzle_y),
            (cx + 5 * s, self.nozzle_y),
            (cx + 16 * s, cy),
        ]
        pygame.draw.polygon(surface, (150, 55, 25), cone_pts)
        pygame.draw.lines(surface, (255, 215, 0), False, cone_pts, 2)
        
        surface.blit(self.glow_surf, (int(cx - self.glow_r), int(self.nozzle_y - self.glow_r)), special_flags=pygame.BLEND_ADD)

        for spk in self.sparks:
            spk.draw(surface)


# ==============================================================================
# AMBIENT FLOATING DUST SPARKLES
# ==============================================================================
class AmbientSparkle:
    """Glittering ambient festive dust floating gently across the screen."""
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.x = random.uniform(0, screen_w)
        self.y = random.uniform(screen_h * 0.2, screen_h * 0.85)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.4, 0.2)
        self.phase = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(2.0, 4.5)
        self.color = random.choice([
            (255, 225, 120), (255, 200, 80), (255, 240, 200), (255, 180, 220)
        ])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0: self.x = self.screen_w
        if self.x > self.screen_w: self.x = 0
        if self.y < self.screen_h * 0.2: self.y = self.screen_h * 0.85
        if self.y > self.screen_h * 0.85: self.y = self.screen_h * 0.2

    def draw(self, surface, current_time):
        alpha = int(140 * (0.5 + 0.5 * math.sin(current_time * self.speed + self.phase)))
        if alpha > 10:
            surf = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (2, 2), 1)
            surface.blit(surf, (int(self.x - 2), int(self.y - 2)), special_flags=pygame.BLEND_ADD)


# ==============================================================================
# RANGOLI FLOOR MOTIF & TERRACE PLATFORM
# ==============================================================================
def draw_terrace_and_rangoli(surface, screen_w, screen_h, current_time):
    """Draws a warm-lit terrace ledge and an intricate glowing Rangoli pattern."""
    terrace_y = int(screen_h * 0.84)
    terrace_rect = pygame.Rect(0, terrace_y, screen_w, screen_h - terrace_y)
    
    pygame.draw.rect(surface, (24, 14, 22), terrace_rect)
    pygame.draw.line(surface, (180, 110, 40), (0, terrace_y), (screen_w, terrace_y), 3)
    pygame.draw.line(surface, (255, 215, 80), (0, terrace_y + 3), (screen_w, terrace_y + 3), 1)

    if not CONFIG["SHOW_RANGOLI"]:
        return

    cx = screen_w // 2
    cy = int(screen_h * 0.885)
    rangoli_surf = pygame.Surface((280, 100), pygame.SRCALPHA)
    rcx, rcy = 140, 50

    pulse = 0.85 + 0.15 * math.sin(current_time * 2.0)
    gold_col = (255, 205, 50, int(90 * pulse))
    white_col = (255, 245, 220, int(80 * pulse))
    pink_col = (255, 105, 180, int(60 * pulse))

    pygame.draw.ellipse(rangoli_surf, gold_col, (rcx - 120, rcy - 36, 240, 72), 2)
    pygame.draw.ellipse(rangoli_surf, pink_col, (rcx - 90, rcy - 27, 180, 54), 1)
    pygame.draw.ellipse(rangoli_surf, white_col, (rcx - 60, rcy - 18, 120, 36), 1)

    for i in range(12):
        angle = i * (math.pi / 6)
        px = rcx + math.cos(angle) * 75
        py = rcy + math.sin(angle) * 22
        pygame.draw.circle(rangoli_surf, gold_col, (int(px), int(py)), 3)
        pygame.draw.line(rangoli_surf, white_col, (rcx, rcy), (int(px), int(py)), 1)

    surface.blit(rangoli_surf, (cx - 140, cy - 50), special_flags=pygame.BLEND_ADD)


# ==============================================================================
# GREETING TEXT BANNER WITH LAYERED GOLDEN GLOW
# ==============================================================================
class GreetingBanner:
    """Renders the festive Diwali greeting with glowing gold halos and breathing animation."""
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        
        font_name = CONFIG["FONT_FAMILY"]
        self.main_font = None
        self.sub_font = None
        
        fonts_to_try = [font_name, "georgia", "garamond", "timesnewroman", "segoeui"]
        for f in fonts_to_try:
            if f:
                try:
                    self.main_font = pygame.font.SysFont(f, 62, bold=True)
                    self.sub_font = pygame.font.SysFont(f, 21, italic=True)
                    break
                except Exception:
                    continue
                    
        if self.main_font is None:
            self.main_font = pygame.font.Font(None, 70)
            self.sub_font = pygame.font.Font(None, 26)

    def draw(self, surface, current_time):
        cx = self.screen_w // 2
        
        float_y = math.sin(current_time * 2.2) * 5.0
        pulse = 0.88 + 0.12 * math.sin(current_time * 3.5)
        main_y = int(self.screen_h * 0.22 + float_y)
        
        text_str = f"✨  {CONFIG['GREETING_MAIN'].upper()}  ✨"
        
        glow1 = self.main_font.render(text_str, True, (255, 120, 20))
        glow1.set_alpha(int(90 * pulse))
        
        glow2 = self.main_font.render(text_str, True, (255, 215, 0))
        glow2.set_alpha(int(140 * pulse))
        
        core_text = self.main_font.render(text_str, True, (255, 255, 230))
        rect = core_text.get_rect(center=(cx, main_y))
        
        for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2)]:
            surface.blit(glow1, (rect.x + dx, rect.y + dy), special_flags=pygame.BLEND_ADD)
            
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            surface.blit(glow2, (rect.x + dx, rect.y + dy), special_flags=pygame.BLEND_ADD)
            
        surface.blit(core_text, rect)
        
        sub_str = CONFIG["GREETING_SUB"]
        sub_y = main_y + 54
        sub_glow = self.sub_font.render(sub_str, True, (255, 190, 80))
        sub_glow.set_alpha(int(120 * pulse))
        sub_core = self.sub_font.render(sub_str, True, (255, 245, 210))
        sub_rect = sub_core.get_rect(center=(cx, sub_y))
        
        surface.blit(sub_glow, (sub_rect.x, sub_rect.y + 1), special_flags=pygame.BLEND_ADD)
        surface.blit(sub_core, sub_rect)


# ==============================================================================
# MAIN ANIMATION APPLICATION
# ==============================================================================
class DiwaliAnimationApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(CONFIG["WINDOW_TITLE"])
        
        self.width = CONFIG["WINDOW_WIDTH"]
        self.height = CONFIG["WINDOW_HEIGHT"]
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.is_fullscreen = False
        self.show_help = True
        
        # Initialize Procedural Audio Engine (NumPy-powered)
        self.audio = ProceduralAudioEngine()
        
        # Create gradient night sky background
        self.bg_surface = pygame.Surface((self.width, self.height))
        self.render_sky_gradient()
        
        # Starfield
        self.stars = [Star(self.width, self.height) for _ in range(CONFIG["STAR_COUNT"])]
        
        # Hanging Fairy Lights
        self.fairy_lights = FairyLights(self.width)
        
        # Diyas (arranged symmetrically along the terrace)
        self.diyas = self.create_diyas()
        
        # Anar Fountains (Bottom corners)
        terrace_y = int(self.height * 0.84)
        self.anar_left = AnarFountain(75, terrace_y, scale=1.1)
        self.anar_right = AnarFountain(self.width - 75, terrace_y, scale=1.1)
        
        # Fireworks & Rockets
        self.rockets = []
        self.particles = []
        self.last_auto_firework = time.time()
        
        # Floating sparkles
        self.sparkles = [AmbientSparkle(self.width, self.height) for _ in range(35)]
        
        # Greeting Banner
        self.banner = GreetingBanner(self.width, self.height)
        
        # UI Font for controls overlay
        self.ui_font = pygame.font.SysFont("segoeui, arial", 16)
        
        # Launch initial welcoming firework pair
        self.launch_firework(self.width * 0.3, self.height * 0.28)
        self.launch_firework(self.width * 0.7, self.height * 0.28)

    def render_sky_gradient(self):
        top_color = (10, 8, 28)
        mid_color = (26, 14, 42)
        bottom_color = (48, 20, 36)
        
        for y in range(self.height):
            ratio = y / float(self.height)
            if ratio < 0.6:
                sub_r = ratio / 0.6
                r = int(top_color[0] + (mid_color[0] - top_color[0]) * sub_r)
                g = int(top_color[1] + (mid_color[1] - top_color[1]) * sub_r)
                b = int(top_color[2] + (mid_color[2] - top_color[2]) * sub_r)
            else:
                sub_r = (ratio - 0.6) / 0.4
                r = int(mid_color[0] + (bottom_color[0] - mid_color[0]) * sub_r)
                g = int(mid_color[1] + (bottom_color[1] - mid_color[1]) * sub_r)
                b = int(mid_color[2] + (bottom_color[2] - mid_color[2]) * sub_r)
                
            pygame.draw.line(self.bg_surface, (r, g, b), (0, y), (self.width, y))

    def create_diyas(self):
        diyas = []
        count = CONFIG["DIYA_COUNT"]
        terrace_y = int(self.height * 0.84)
        
        cx = self.width // 2
        spacing = min(150, (self.width - 250) // max(1, count - 1))
        
        for i in range(count):
            offset_idx = i - (count - 1) / 2.0
            x = cx + offset_idx * spacing
            is_center = (i == count // 2)
            scale = 1.35 if is_center else 1.05
            y = terrace_y - (6 if is_center else 0)
            diyas.append(Diya(x, y, scale=scale, is_center=is_center))
            
        return diyas

    def launch_firework(self, target_x, target_y, start_x=None, palette=None):
        """Launches a single rocket aimed at target coordinates and plays audio whoosh."""
        rocket = Rocket(target_x, target_y, start_x=start_x, palette=palette)
        self.rockets.append(rocket)
        # Play rocket launch whoosh sound
        self.audio.play_launch()

    def trigger_celebration_barrage(self):
        """Fires a grand festive barrage across the sky."""
        for _ in range(5):
            tx = random.randint(120, self.width - 120)
            ty = random.randint(int(self.height * 0.15), int(self.height * 0.45))
            sx = random.randint(100, self.width - 100)
            self.launch_firework(tx, ty, start_x=sx)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.is_running = False
                elif event.key == pygame.K_SPACE:
                    self.trigger_celebration_barrage()
                elif event.key == pygame.K_s:
                    self.audio.toggle_mute()
                elif event.key == pygame.K_h:
                    self.show_help = not self.show_help
                elif event.key == pygame.K_a:
                    CONFIG["SHOW_ANAR_FOUNTAINS"] = not CONFIG["SHOW_ANAR_FOUNTAINS"]
                elif event.key == pygame.K_l:
                    CONFIG["SHOW_FAIRY_LIGHTS"] = not CONFIG["SHOW_FAIRY_LIGHTS"]
                elif event.key == pygame.K_f:
                    self.is_fullscreen = not self.is_fullscreen
                    if self.is_fullscreen:
                        self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    target_y = min(my, int(self.height * 0.6))
                    self.launch_firework(mx, target_y)

    def update(self):
        now = time.time()
        
        if CONFIG["AUTO_FIREWORKS"] and now - self.last_auto_firework > CONFIG["FIREWORK_INTERVAL"]:
            tx = random.randint(120, self.width - 120)
            ty = random.randint(int(self.height * 0.12), int(self.height * 0.42))
            self.launch_firework(tx, ty)
            self.last_auto_firework = now + random.uniform(-0.35, 0.45)

        for diya in self.diyas:
            diya.update()

        if CONFIG["SHOW_ANAR_FOUNTAINS"]:
            self.anar_left.update()
            self.anar_right.update()

        surviving_rockets = []
        for rocket in self.rockets:
            if rocket.update():
                surviving_rockets.append(rocket)
            else:
                # Rocket exploded! Spawn sparks and play boom sound
                new_sparks = rocket.explode()
                self.particles.extend(new_sparks)
                self.audio.play_explosion(ptype=rocket.ptype)
                
        self.rockets = surviving_rockets
        self.particles = [p for p in self.particles if p.update()]

        if CONFIG["FLOATING_SPARKLES"]:
            for spk in self.sparkles:
                spk.update()

    def draw(self):
        current_time = time.time()
        
        # 1. Base Sky Gradient
        self.screen.blit(self.bg_surface, (0, 0))

        # 2. Twinkling Stars
        for star in self.stars:
            star.draw(self.screen, current_time)

        # 3. Fireworks & Rockets
        for rocket in self.rockets:
            rocket.draw(self.screen)
        for particle in self.particles:
            particle.draw(self.screen)

        # 4. Ambient floating sparkles
        if CONFIG["FLOATING_SPARKLES"]:
            for spk in self.sparkles:
                spk.draw(self.screen, current_time)

        # 5. Festive Hanging Fairy Lights
        if CONFIG["SHOW_FAIRY_LIGHTS"]:
            self.fairy_lights.draw(self.screen, current_time)

        # 6. Terrace Platform & Rangoli
        draw_terrace_and_rangoli(self.screen, self.width, self.height, current_time)

        # 7. Diya Ambient Glow Halos
        for diya in self.diyas:
            diya.draw_glow(self.screen, current_time)

        # 8. Diya Lamps & Flickering Flames
        for diya in self.diyas:
            diya.draw(self.screen, current_time)

        # 9. Anar Sparkler Fountains
        if CONFIG["SHOW_ANAR_FOUNTAINS"]:
            self.anar_left.draw(self.screen)
            self.anar_right.draw(self.screen)

        # 10. Diwali Greeting Banner
        self.banner.draw(self.screen, current_time)

        # 11. Control Hints HUD (Including Sound status)
        if self.show_help:
            sound_status = "MUTED" if self.audio.muted else "ON"
            hint_str = f"✨ Click: Firework  |  Space: Grand Finale  |  S: Sound [{sound_status}]  |  A: Anar  |  F: Fullscreen  |  H: Hide Help  |  Esc: Exit"
            hint_surf = self.ui_font.render(hint_str, True, (255, 230, 160))
            hint_surf.set_alpha(175)
            hx = (self.width - hint_surf.get_width()) // 2
            hy = self.height - 24
            self.screen.blit(hint_surf, (hx, hy))

        pygame.display.flip()

    def run(self):
        while self.is_running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(CONFIG["FPS"])
            
        pygame.quit()
        sys.exit()


# ==============================================================================
# ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    app = DiwaliAnimationApp()
    app.run()
