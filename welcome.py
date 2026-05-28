# ═══════════════════════════════════════════════════════════
#  🖼️ نظام صور الترحيب والتوديع
# ═══════════════════════════════════════════════════════════

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import os
import requests as http_requests

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

def _get_font(size):
    """يحاول تحميل خط عربي، وإلا يستخدم الخط الافتراضي"""
    font_path = os.path.join(ASSETS_DIR, "font.ttf")
    try:
        return ImageFont.truetype(font_path, size)
    except:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()

def _download_avatar(avatar_url):
    """يحمل صورة الأفاتار من الرابط"""
    try:
        if avatar_url:
            resp = http_requests.get(avatar_url, timeout=5)
            if resp.status_code == 200:
                return Image.open(io.BytesIO(resp.content)).convert("RGBA")
    except:
        pass
    # صورة افتراضية
    img = Image.new("RGBA", (200, 200), (100, 100, 100, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([10, 10, 190, 190], fill=(150, 150, 150, 255))
    draw.text((65, 70), "👤", fill="white", font=_get_font(60))
    return img

def _make_circle_avatar(avatar, size=180):
    """يقص الصورة بشكل دائري"""
    avatar = avatar.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([0, 0, size, size], fill=255)
    output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    output.paste(avatar, (0, 0), mask)
    return output

def generate_welcome_image(username, avatar_url=None):
    """يولد صورة ترحيب جميلة"""
    W, H = 800, 400

    # خلفية متدرجة
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        r = int(20 + (y / H) * 30)
        g = int(100 + (y / H) * 55)
        b = int(180 + (y / H) * 40)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # إطار ديكوري
    draw.rectangle([10, 10, W-10, H-10], outline=(255, 255, 255, 80), width=2)
    draw.rectangle([20, 20, W-20, H-20], outline=(255, 215, 0), width=1)

    # نجوم / زخارف
    import random
    random.seed(hash(username))
    for _ in range(30):
        x = random.randint(30, W-30)
        y_star = random.randint(30, H-30)
        size_s = random.randint(1, 3)
        alpha = random.randint(100, 255)
        draw.ellipse([x, y_star, x+size_s, y_star+size_s], fill=(255, 255, 255))

    # أفاتار دائري
    avatar_raw = _download_avatar(avatar_url)
    avatar_circle = _make_circle_avatar(avatar_raw, 150)

    # حلقة حول الأفاتار
    ring = Image.new("RGBA", (170, 170), (0, 0, 0, 0))
    ring_draw = ImageDraw.Draw(ring)
    ring_draw.ellipse([0, 0, 170, 170], outline=(255, 215, 0), width=3)
    img.paste(ring.convert("RGB"), (W//2 - 85, 30), ring.split()[3])
    img.paste(avatar_circle.convert("RGB"), (W//2 - 75, 40), avatar_circle.split()[3])

    # نص "أهلاً وسهلاً"
    title_font = _get_font(45)
    name_font = _get_font(35)
    sub_font = _get_font(20)

    # عنوان
    title = "🌟 أهلاً وسهلاً 🌟"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 210), title, fill=(255, 215, 0), font=title_font)

    # اسم المستخدم
    name_text = f"مرحباً بك يا {username}!"
    bbox2 = draw.textbbox((0, 0), name_text, font=name_font)
    nw = bbox2[2] - bbox2[0]
    draw.text(((W - nw) // 2, 270), name_text, fill=(255, 255, 255), font=name_font)

    # نص إضافي
    sub_text = "نتمنى لك وقت ممتع معنا 💫"
    bbox3 = draw.textbbox((0, 0), sub_text, font=sub_font)
    sw = bbox3[2] - bbox3[0]
    draw.text(((W - sw) // 2, 330), sub_text, fill=(200, 200, 255), font=sub_font)

    # حفظ
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def generate_goodbye_image(username, avatar_url=None):
    """يولد صورة توديع"""
    W, H = 800, 400

    # خلفية متدرجة (أحمر غامق)
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        r = int(120 + (y / H) * 30)
        g = int(30 + (y / H) * 20)
        b = int(40 + (y / H) * 30)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # إطار
    draw.rectangle([10, 10, W-10, H-10], outline=(255, 255, 255, 80), width=2)
    draw.rectangle([20, 20, W-20, H-20], outline=(200, 100, 100), width=1)

    # أفاتار دائري
    avatar_raw = _download_avatar(avatar_url)
    avatar_circle = _make_circle_avatar(avatar_raw, 150)

    ring = Image.new("RGBA", (170, 170), (0, 0, 0, 0))
    ring_draw = ImageDraw.Draw(ring)
    ring_draw.ellipse([0, 0, 170, 170], outline=(200, 100, 100), width=3)
    img.paste(ring.convert("RGB"), (W//2 - 85, 30), ring.split()[3])
    img.paste(avatar_circle.convert("RGB"), (W//2 - 75, 40), avatar_circle.split()[3])

    # نصوص
    title_font = _get_font(45)
    name_font = _get_font(35)
    sub_font = _get_font(20)

    title = "👋 مع السلامة 👋"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 210), title, fill=(255, 180, 180), font=title_font)

    name_text = f"وداعاً يا {username}"
    bbox2 = draw.textbbox((0, 0), name_text, font=name_font)
    nw = bbox2[2] - bbox2[0]
    draw.text(((W - nw) // 2, 270), name_text, fill=(255, 255, 255), font=name_font)

    sub_text = "نتمنى نشوفك مرة ثانية 💔"
    bbox3 = draw.textbbox((0, 0), sub_text, font=sub_font)
    sw = bbox3[2] - bbox3[0]
    draw.text(((W - sw) // 2, 330), sub_text, fill=(200, 180, 180), font=sub_font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
