import os
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from utils.config import get_value

IMAGE_DIR = Path(__file__).parent.parent / "images"
IMAGE_DIR.mkdir(exist_ok=True)

SIZE_MAP = {
    "소형": (512, 384),
    "중형": (800, 600),
    "대형": (1200, 800),
}


def generate_image(prompt: str, size: str = "중형", filename: str = None) -> str:
    if not filename:
        filename = f"img_{int(time.time())}.png"
    save_path = IMAGE_DIR / filename

    try:
        from google import genai
        from google.genai import types
        api_key = get_value("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)

        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=f"High quality blog illustration: {prompt}",
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/png",
            ),
        )
        image_bytes = response.generated_images[0].image.image_bytes
        w, h = SIZE_MAP.get(size, (800, 600))
        img = Image.open(__import__("io").BytesIO(image_bytes))
        img = img.resize((w, h), Image.LANCZOS)
        img.save(str(save_path))
        return str(save_path)
    except Exception:
        return _create_placeholder(prompt, size, save_path)


def _create_placeholder(prompt: str, size: str, save_path: Path) -> str:
    w, h = SIZE_MAP.get(size, (800, 600))
    colors = [
        (52, 152, 219), (46, 204, 113), (155, 89, 182),
        (231, 76, 60), (241, 196, 15), (26, 188, 156),
    ]
    idx = abs(hash(prompt)) % len(colors)
    bg_color = colors[idx]

    img = Image.new("RGB", (w, h), color=bg_color)
    draw = ImageDraw.Draw(img)

    dark_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 100))
    img_rgba = img.convert("RGBA")
    img_rgba = Image.alpha_composite(img_rgba, dark_overlay)
    img = img_rgba.convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", size=max(18, w // 22))
        font_small = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", size=max(12, w // 40))
    except Exception:
        font_large = ImageFont.load_default()
        font_small = font_large

    label = prompt[:40] + ("..." if len(prompt) > 40 else "")
    draw.text((w // 2, h // 2 - 20), label, fill="white", font=font_large, anchor="mm")
    draw.text((w // 2, h // 2 + 40), "Blog Image", fill=(200, 200, 200), font=font_small, anchor="mm")

    img.save(str(save_path))
    return str(save_path)


def generate_post_images(sections: list, size: str = "중형", slug: str = "post") -> list:
    image_paths = []
    for i, section in enumerate(sections):
        for j, sub in enumerate(section.get("subsections", [])):
            prompt = sub.get("image_prompt", section.get("h2", "blog image"))
            fname = f"{slug}-s{i}-{j}.png"
            path = generate_image(prompt, size, fname)
            sub["image_path"] = path
            image_paths.append(path)
    return image_paths
