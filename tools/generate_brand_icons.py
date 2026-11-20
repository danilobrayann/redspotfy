import os, sys, struct, io, math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
import pathlib

_ROOT = pathlib.Path(r"c:\Users\danil\OneDrive\Documentos\GitHub\ytm-rs")
SRC_PATH = r"C:\Users\danil\.gemini\antigravity\brain\a38c7cf3-61ba-4178-a111-e70d4c49d35f\.user_uploaded\media_1795043714392_8c5f9ee9.png"
ASSETS_ICON = str(_ROOT / "assets" / "icon")
VARIANTS_DIR = str(_ROOT / "assets" / "icon" / "variants")
BADGE_DIR = str(_ROOT / "site" / "badge")

SIZES = [16, 24, 32, 48, 64, 128, 256]

def make_png_ico(master_img, out_ico_path):
    # Remove arquivo antigo se existir (pode estar read-only)
    try:
        if os.path.exists(out_ico_path):
            os.chmod(out_ico_path, 0o777)
            os.remove(out_ico_path)
    except Exception:
        pass
    # Pillow redimensiona a imagem para cada tamanho pedido e grava como PNG no ICO
    master_img.convert("RGBA").save(
        out_ico_path,
        format="ICO",
        sizes=[(s, s) for s in SIZES]
    )

def make_badge(master_img, out_badge_path):
    badge = master_img.resize((128, 128), Image.Resampling.LANCZOS)
    badge.save(out_badge_path, format='PNG')

# 1. Carregar imagem original e enquadrar em quadrado
orig = Image.open(SRC_PATH).convert('RGBA')
w, h = orig.size
max_dim = max(w, h)
square = Image.new('RGBA', (max_dim, max_dim), (0, 0, 0, 0))
offset_x = (max_dim - w) // 2
offset_y = (max_dim - h) // 2
square.paste(orig, (offset_x, offset_y), orig)
base_img = square.resize((512, 512), Image.Resampling.LANCZOS)

# 2. Salvar ícone original principal
os.makedirs(ASSETS_ICON, exist_ok=True)
os.makedirs(VARIANTS_DIR, exist_ok=True)
os.makedirs(BADGE_DIR, exist_ok=True)

base_img.save(os.path.join(ASSETS_ICON, "icon.png"), format='PNG')
make_png_ico(base_img, os.path.join(ASSETS_ICON, "icon.ico"))
make_badge(base_img, os.path.join(BADGE_DIR, "classic.png"))

# 3. Criar variantes

# Variante 1: RedSpotfy (Vermelho / Red)
def make_redspotfy(img):
    out = img.copy()
    r, g, b, a = out.split()
    # Converte verdes e azuis para vermelhos vibrantes
    pixels = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            pr, pg, pb, pa = pixels[x, y]
            if pa > 10:
                # Se for esverdeado
                if pg > pr and pg > pb:
                    intensity = pg / 255.0
                    pixels[x, y] = (int(min(255, 230 * intensity + 25)), int(20 * intensity), int(35 * intensity), pa)
                # Se for azulado
                elif pb > pr and pb > pg:
                    intensity = pb / 255.0
                    pixels[x, y] = (int(min(255, 180 * intensity + 30)), int(10 * intensity), int(60 * intensity), pa)
    return out

# Variante 2: Feliz (Happy Face)
def make_happy(img):
    out = img.copy()
    draw = ImageDraw.Draw(out)
    w, h = out.size
    cx, cy = w // 2, h // 2
    
    # Olho esquerdo (arco feliz ^)
    draw.arc([cx - 75, cy - 45, cx - 25, cy - 5], start=190, end=350, fill=(255, 255, 255, 250), width=9)
    draw.arc([cx - 75, cy - 45, cx - 25, cy - 5], start=190, end=350, fill=(20, 20, 25, 255), width=6)
    
    # Olho direito (arco feliz ^)
    draw.arc([cx + 25, cy - 45, cx + 75, cy - 5], start=190, end=350, fill=(255, 255, 255, 250), width=9)
    draw.arc([cx + 25, cy - 45, cx + 75, cy - 5], start=190, end=350, fill=(20, 20, 25, 255), width=6)
    
    # Bochechas rosadas blush
    blush_overlay = Image.new('RGBA', out.size, (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(blush_overlay)
    bdraw.ellipse([cx - 85, cy - 5, cx - 45, cy + 20], fill=(255, 100, 150, 160))
    bdraw.ellipse([cx + 45, cy - 5, cx + 85, cy + 20], fill=(255, 100, 150, 160))
    blush_overlay = blush_overlay.filter(ImageFilter.GaussianBlur(5))
    out = Image.alpha_composite(out, blush_overlay)
    
    draw = ImageDraw.Draw(out)
    # Boca sorridente aberta
    mouth_box = [cx - 36, cy + 12, cx + 36, cy + 62]
    draw.chord(mouth_box, start=0, end=180, fill=(220, 40, 70, 255), outline=(20, 20, 25, 255), width=4)
    # Língua
    draw.chord([cx - 20, cy + 38, cx + 20, cy + 62], start=0, end=180, fill=(255, 130, 160, 255))
    # Brilho nos olhinhos
    draw.ellipse([cx - 48, cy - 35, cx - 40, cy - 27], fill=(255, 255, 255, 255))
    draw.ellipse([cx + 40, cy - 35, cx + 48, cy - 27], fill=(255, 255, 255, 255))
    return out

# Variante 3: Triste (Sad Face)
def make_sad(img):
    out = img.copy()
    draw = ImageDraw.Draw(out)
    w, h = out.size
    cx, cy = w // 2, h // 2
    
    # Olho esquerdo triste (arco voltado para baixo)
    draw.arc([cx - 75, cy - 35, cx - 25, cy + 5], start=10, end=170, fill=(255, 255, 255, 250), width=9)
    draw.arc([cx - 75, cy - 35, cx - 25, cy + 5], start=10, end=170, fill=(20, 20, 25, 255), width=6)
    
    # Olho direito triste
    draw.arc([cx + 25, cy - 35, cx + 75, cy + 5], start=10, end=170, fill=(255, 255, 255, 250), width=9)
    draw.arc([cx + 25, cy - 35, cx + 75, cy + 5], start=10, end=170, fill=(20, 20, 25, 255), width=6)
    
    # Boca triste curvada para baixo
    draw.arc([cx - 32, cy + 30, cx + 32, cy + 70], start=190, end=350, fill=(255, 255, 255, 250), width=8)
    draw.arc([cx - 32, cy + 30, cx + 32, cy + 70], start=190, end=350, fill=(30, 30, 35, 255), width=5)
    
    # Gotinha de lágrima caindo do olho direito
    tear_pts = [
        (cx + 62, cy + 10),
        (cx + 56, cy + 26),
        (cx + 62, cy + 34),
        (cx + 68, cy + 26),
    ]
    draw.polygon(tear_pts, fill=(80, 200, 255, 240), outline=(255, 255, 255, 220))
    draw.ellipse([cx + 56, cy + 22, cx + 68, cy + 34], fill=(80, 200, 255, 240), outline=(255, 255, 255, 220))
    # Brilho na lágrima
    draw.ellipse([cx + 59, cy + 24, cx + 63, cy + 28], fill=(255, 255, 255, 255))
    return out

# Variante 4: Natal (Christmas Hat)
def make_natal(img):
    out = img.copy()
    hat_layer = Image.new('RGBA', out.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(hat_layer)
    w, h = out.size
    
    # Gorro de Papai Noel colocado sobre o topo
    # Base do gorro (vermelho)
    # Polígono curvo do gorro vermelho
    pts = [
        (130, 95),   # canto esquerdo
        (260, 20),   # pico alto
        (370, 75),   # dobra à direita
        (385, 150),  # ponta caída
        (330, 110),  # borda interna
        (150, 105),  # base
    ]
    draw.polygon(pts, fill=(215, 25, 45, 255), outline=(170, 15, 30, 255))
    
    # Sombra e dobra do gorro
    draw.polygon([(260, 20), (370, 75), (340, 90)], fill=(185, 20, 35, 255))
    
    # Faixa branca felpuda na base
    band_pts = [
        (120, 85), (345, 95), (340, 130), (115, 120)
    ]
    # Nuvens/círculos brancos na faixa
    for bx in range(120, 350, 16):
        by = int(95 + (bx - 120) * 0.08)
        draw.ellipse([bx - 12, by - 6, bx + 16, by + 22], fill=(245, 248, 255, 255))
        draw.ellipse([bx - 10, by - 4, bx + 14, by + 20], fill=(255, 255, 255, 255))
    
    # Pompom branco na ponta
    px, py = 385, 150
    for r in range(22, 6, -3):
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(240, 245, 255, 255))
    draw.ellipse([px - 14, py - 14, px + 14, py + 14], fill=(255, 255, 255, 255))
    
    # Sombra suave sob o gorro
    shadow = hat_layer.filter(ImageFilter.GaussianBlur(6))
    out = Image.alpha_composite(out, shadow)
    out = Image.alpha_composite(out, hat_layer)
    return out

# Variante 5: Gold (Dourado Nobre)
def make_gold(img):
    out = img.copy()
    pixels = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            pr, pg, pb, pa = pixels[x, y]
            if pa > 10:
                gray = (pr * 0.299 + pg * 0.587 + pb * 0.114) / 255.0
                gold_r = int(min(255, 255 * (gray ** 0.8) + 20))
                gold_g = int(min(255, 205 * (gray ** 0.9) + 10))
                gold_b = int(min(255, 55 * gray))
                pixels[x, y] = (gold_r, gold_g, gold_b, pa)
    return out

# Variante 6: Neon Cyberpunk (Roxo e Ciano)
def make_neon(img):
    out = img.copy()
    pixels = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            pr, pg, pb, pa = pixels[x, y]
            if pa > 10:
                if pg > pr and pg > pb:
                    intensity = pg / 255.0
                    pixels[x, y] = (int(min(255, 255 * intensity)), int(20 * intensity), int(min(255, 240 * intensity)), pa)
                elif pb > pr and pb > pg:
                    intensity = pb / 255.0
                    pixels[x, y] = (int(10 * intensity), int(min(255, 240 * intensity)), int(min(255, 255 * intensity)), pa)
    return out

# Variante 7: Dark Mode (Prata & Preto)
def make_dark(img):
    out = img.copy()
    pixels = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            pr, pg, pb, pa = pixels[x, y]
            if pa > 10:
                gray = int(pr * 0.299 + pg * 0.587 + pb * 0.114)
                # Escurece mantendo brilho prateado
                silver = int(gray * 0.75 + 30)
                pixels[x, y] = (silver, int(silver * 1.02), int(silver * 1.06), pa)
    return out

variants = [
    ("redspotfy", make_redspotfy(base_img)),
    ("happy", make_happy(base_img)),
    ("sad", make_sad(base_img)),
    ("natal", make_natal(base_img)),
    ("gold", make_gold(base_img)),
    ("neon", make_neon(base_img)),
    ("dark", make_dark(base_img)),
]

for name, var_img in variants:
    ico_path = os.path.join(VARIANTS_DIR, f"{name}.ico")
    badge_path = os.path.join(BADGE_DIR, f"{name}.png")
    make_png_ico(var_img, ico_path)
    make_badge(var_img, badge_path)
    print(f"Generated variant: {name}")

print("All icons successfully generated!")
