import math
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

IMAGE_DIR = Path(__file__).parent.parent / "images"
IMAGE_DIR.mkdir(exist_ok=True)

FONT_PATH = "C:/Windows/Fonts/malgunbd.ttf"   # 맑은 고딕 Bold
FONT_PATH_REG = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕 Regular

COVER_SIZE = (1200, 400)
SECTION_SIZE = (1200, 280)

# 색상 팔레트 (start_left, start_right, text, accent)
COLOR_SCHEMES = [
    ((10, 25, 80),  (20, 55, 130), (255, 255, 255), (100, 180, 255)),   # 딥 블루
    ((15, 55, 25),  (30, 95, 45),  (255, 255, 255), (100, 230, 140)),   # 딥 그린
    ((55, 10, 75),  (90, 25, 120), (255, 255, 255), (210, 140, 255)),   # 딥 퍼플
    ((10, 50, 65),  (25, 85, 105), (255, 255, 255), (90, 220, 235)),    # 딥 틸
    ((70, 25, 10),  (120, 50, 15), (255, 255, 255), (255, 190, 100)),   # 딥 오렌지
    ((20, 10, 55),  (50, 25, 90),  (255, 255, 255), (175, 155, 255)),   # 인디고
    ((55, 10, 30),  (100, 20, 55), (255, 255, 255), (255, 140, 180)),   # 딥 로즈
    ((10, 40, 55),  (20, 70, 90),  (255, 255, 255), (120, 220, 255)),   # 오션
]


def _get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    path = FONT_PATH if bold else FONT_PATH_REG
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _gradient_bg(size: tuple, c_left: tuple, c_right: tuple) -> Image.Image:
    """좌→우 수평 그라디언트 배경"""
    w, h = size
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for x in range(w):
        t = x / (w - 1)
        r = int(c_left[0] + (c_right[0] - c_left[0]) * t)
        g = int(c_left[1] + (c_right[1] - c_left[1]) * t)
        b = int(c_left[2] + (c_right[2] - c_left[2]) * t)
        draw.line([(x, 0), (x, h)], fill=(r, g, b))
    return img


def _draw_deco_circles(draw: ImageDraw.Draw, cx: int, cy: int,
                       accent: tuple, count: int = 4):
    """오른쪽 장식 원형 아크"""
    for i in range(count, 0, -1):
        r = i * 38
        alpha = int(60 + (count - i) * 30)
        color = (*accent, alpha)
        try:
            draw.arc(
                [cx - r, cy - r, cx + r, cy + r],
                start=200, end=340,
                fill=accent,
                width=max(2, 5 - i),
            )
        except Exception:
            pass


def _draw_dot_grid(draw: ImageDraw.Draw, x0: int, y0: int,
                   accent: tuple, cols: int = 5, rows: int = 4):
    """작은 점 그리드 장식"""
    gap = 18
    for row in range(rows):
        for col in range(cols):
            cx = x0 + col * gap
            cy = y0 + row * gap
            opacity = 80 + col * 20
            r = 2
            draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                         fill=(*accent[:3], min(opacity, 200)))


def _wrap_text(text: str, font: ImageFont.FreeTypeFont,
               max_width: int) -> list[str]:
    """텍스트를 max_width에 맞게 줄바꿈"""
    words = text
    lines = []
    current = ""
    for char in words:
        test = current + char
        bbox = font.getbbox(test)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def _draw_text_shadow(draw, pos, text, font, fill, shadow_offset=2):
    """그림자 효과 텍스트"""
    x, y = pos
    draw.text((x + shadow_offset, y + shadow_offset), text,
              font=font, fill=(0, 0, 0, 100))
    draw.text((x, y), text, font=font, fill=fill)


def create_banner(title: str, subtitle: str = "",
                  size: tuple = COVER_SIZE,
                  scheme_idx: int = None) -> Image.Image:
    """
    타이틀+부제목이 올라간 그라디언트 배너 이미지 생성
    """
    if scheme_idx is None:
        scheme_idx = abs(hash(title)) % len(COLOR_SCHEMES)

    c_left, c_right, text_color, accent = COLOR_SCHEMES[scheme_idx % len(COLOR_SCHEMES)]
    w, h = size

    # ── 배경 ──────────────────────────────────────────────────────────────────
    img = _gradient_bg(size, c_left, c_right)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 장식 요소 ──────────────────────────────────────────────────────────────
    # 오른쪽 아크
    _draw_deco_circles(draw, cx=w - 80, cy=h // 2, accent=accent, count=5)
    # 점 그리드 (우하단)
    _draw_dot_grid(draw, x0=w - 160, y0=h - 90, accent=accent, cols=5, rows=3)
    # 좌측 하단 장식 라인
    for i in range(3):
        y_line = h - 30 + i * 8
        draw.line([(60, y_line), (200, y_line)],
                  fill=(*accent[:3], 60 + i * 30), width=2)

    # ── 제목 텍스트 ────────────────────────────────────────────────────────────
    margin_left = 70
    text_max_w = int(w * 0.65)
    y_cursor = int(h * 0.18)

    # 제목 폰트 크기 자동 조정
    title_font_size = max(32, min(54, int(h * 0.13)))
    title_font = _get_font(title_font_size, bold=True)

    title_lines = _wrap_text(title, title_font, text_max_w)
    # 최대 2줄
    for i, line in enumerate(title_lines[:2]):
        _draw_text_shadow(draw, (margin_left, y_cursor), line,
                          title_font, fill=text_color)
        y_cursor += title_font_size + 8

    # ── 부제목 텍스트 ───────────────────────────────────────────────────────────
    if subtitle:
        y_cursor += 10
        sub_font_size = max(16, int(title_font_size * 0.42))
        sub_font = _get_font(sub_font_size, bold=False)
        sub_lines = _wrap_text(subtitle, sub_font, text_max_w)
        for line in sub_lines[:2]:
            sub_color = tuple(min(255, c + 60) for c in text_color[:3])
            draw.text((margin_left, y_cursor), line,
                      font=sub_font, fill=sub_color)
            y_cursor += sub_font_size + 4

    # ── 하단 강조 바 ───────────────────────────────────────────────────────────
    bar_h = max(4, h // 80)
    draw.rectangle([0, h - bar_h, w, h],
                   fill=(*accent[:3], 180))

    return img.convert("RGB")


def generate_cover_image(post_data: dict, slug: str = "post",
                         scheme_idx: int = None) -> str:
    """포스트 대표 커버 배너 생성"""
    title = post_data.get("title", "")
    description = post_data.get("description", "")
    if scheme_idx is None:
        scheme_idx = abs(hash(title)) % len(COLOR_SCHEMES)

    save_path = IMAGE_DIR / f"{slug}-cover.png"
    img = create_banner(title, description, size=COVER_SIZE,
                        scheme_idx=scheme_idx)
    img.save(str(save_path), "PNG")
    return str(save_path)


def generate_section_image(h2: str, h3: str = "",
                           filename: str = "section.png",
                           scheme_idx: int = None) -> str:
    """섹션 배너 이미지 생성 (h2 타이틀 + h3 부제목)"""
    if scheme_idx is None:
        # 커버와 다른 색상 스킴 사용 (커버+1)
        scheme_idx = (abs(hash(h2)) % len(COLOR_SCHEMES))

    save_path = IMAGE_DIR / filename
    img = create_banner(h2, h3, size=SECTION_SIZE, scheme_idx=scheme_idx)
    img.save(str(save_path), "PNG")
    return str(save_path)


def generate_post_images(post_data: dict, size: str = "중형",
                         slug: str = "post",
                         log_callback=None) -> dict:
    """
    포스트 전체 배너 이미지 일괄 생성
    - cover: 대표 이미지 (title + description)
    - sections: 섹션별 배너 (h2 + h3)
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
        print(msg)

    slug_safe = slug[:30].replace(" ", "_").replace("/", "_")
    title = post_data.get("title", "")
    base_scheme = abs(hash(title)) % len(COLOR_SCHEMES)
    result = {"cover": "", "sections": []}

    # ── 커버 이미지 ────────────────────────────────────────────────────────────
    log("  [커버] 대표 배너 이미지 생성 중...")
    try:
        cover_path = generate_cover_image(post_data, slug_safe, scheme_idx=base_scheme)
        post_data["cover_image"] = cover_path
        result["cover"] = cover_path
        log(f"  [OK] 커버: {Path(cover_path).name}")
    except Exception as e:
        log(f"  [FAIL] 커버 실패: {e}")

    # ── 섹션별 배너 ────────────────────────────────────────────────────────────
    sections = post_data.get("sections", [])
    for i, section in enumerate(sections):
        h2 = section.get("h2", "")
        if not h2:
            continue
        # 각 섹션마다 색상 순환
        scheme = (base_scheme + i + 1) % len(COLOR_SCHEMES)
        fname = f"{slug_safe}-s{i}.png"

        # 첫 번째 subsection의 h3 사용
        h3 = ""
        subs = section.get("subsections", [])
        if subs and subs[0].get("h3") and subs[0]["h3"] != h2:
            h3 = subs[0]["h3"]

        log(f"  [섹션 {i+1}] {h2[:25]}...")
        try:
            path = generate_section_image(h2, h3, fname, scheme_idx=scheme)
            # 섹션의 모든 subsection에 이미지 경로 공유
            for sub in subs:
                sub["image_path"] = path
            result["sections"].append(path)
            log(f"  [OK] {fname}")
        except Exception as e:
            log(f"  [FAIL] 섹션 {i+1} 실패: {e}")

    total = (1 if result["cover"] else 0) + len(result["sections"])
    log(f"  완료: 총 {total}장 생성 (커버 1 + 섹션 {len(result['sections'])})")
    return result
