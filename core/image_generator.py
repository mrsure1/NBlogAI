import io
import time
import urllib.parse
from pathlib import Path

import requests
from PIL import Image

from utils.config import get_value

IMAGE_DIR = Path(__file__).parent.parent / "images"
IMAGE_DIR.mkdir(exist_ok=True)

SIZE_MAP = {
    "소형": (800, 450),
    "중형": (1200, 675),
    "대형": (1600, 900),
}

# 대표/배너 이미지용 고정 사이즈
COVER_SIZE = (1200, 630)
SECTION_SIZE = (1000, 560)


def _pollinations_url(prompt: str, width: int, height: int) -> str:
    encoded = urllib.parse.quote(prompt, safe="")
    return (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&nologo=true&model=flux&enhance=true"
    )


def _download_image(prompt: str, width: int, height: int, save_path: Path, retries: int = 3) -> bool:
    url = _pollinations_url(prompt, width, height)
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=90, stream=True)
            resp.raise_for_status()
            img = Image.open(io.BytesIO(resp.content))
            img = img.convert("RGB")
            img.save(str(save_path), "PNG", optimize=True)
            return True
        except Exception as e:
            print(f"  이미지 생성 재시도 {attempt + 1}/{retries}: {e}")
            time.sleep(3)
    return False


def _build_cover_prompt(post_data: dict) -> str:
    """포스트 전체를 대표하는 커버 이미지 프롬프트"""
    title = post_data.get("title", "")
    keywords = post_data.get("keywords", [])
    kw_str = ", ".join(keywords[:3]) if keywords else ""

    # 첫 번째 섹션의 image_prompt가 있으면 참고
    first_prompt = ""
    for section in post_data.get("sections", []):
        for sub in section.get("subsections", []):
            if sub.get("image_prompt"):
                first_prompt = sub["image_prompt"]
                break
        if first_prompt:
            break

    base = first_prompt if first_prompt else f"professional blog cover about {kw_str or title}"
    return (
        f"{base}, "
        "professional blog banner image, high quality photography, "
        "clean composition, vibrant colors, modern aesthetic, "
        "16:9 aspect ratio, no text overlay"
    )


def _build_section_prompt(image_prompt: str, h2: str = "") -> str:
    """섹션별 배너 이미지 프롬프트"""
    base = image_prompt or f"professional illustration about {h2}"
    return (
        f"{base}, "
        "high quality blog section banner, professional photography or illustration, "
        "clean and modern design, good lighting, no text"
    )


def generate_cover_image(post_data: dict, slug: str = "post") -> str:
    """포스트 대표(커버) 이미지 생성"""
    prompt = _build_cover_prompt(post_data)
    save_path = IMAGE_DIR / f"{slug}-cover.png"
    w, h = COVER_SIZE

    print(f"  커버 이미지 생성 중... ({w}x{h})")
    success = _download_image(prompt, w, h, save_path)
    if success:
        return str(save_path)
    return ""


def generate_section_image(image_prompt: str, h2: str, filename: str) -> str:
    """섹션 배너 이미지 생성"""
    prompt = _build_section_prompt(image_prompt, h2)
    save_path = IMAGE_DIR / filename
    w, h = SECTION_SIZE

    success = _download_image(prompt, w, h, save_path)
    if success:
        return str(save_path)
    return ""


def generate_post_images(post_data: dict, size: str = "중형", slug: str = "post",
                         log_callback=None) -> dict:
    """
    포스트의 모든 이미지 생성:
    - cover: 대표 이미지 1장
    - sections: 섹션별 배너 이미지

    반환: {"cover": path, "sections": [...paths]}
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
        print(msg)

    result = {"cover": "", "sections": []}
    slug_safe = slug[:30].replace(" ", "_").replace("/", "_")

    # 1) 커버 이미지
    log("  [1] 대표 커버 이미지 생성 중... (약 20초)")
    cover_path = generate_cover_image(post_data, slug_safe)
    if cover_path:
        post_data["cover_image"] = cover_path
        result["cover"] = cover_path
        log(f"  ✓ 커버 이미지: {Path(cover_path).name}")
    else:
        log("  ✗ 커버 이미지 생성 실패")

    # 2) 섹션별 이미지
    sections = post_data.get("sections", [])
    img_count = 0
    for i, section in enumerate(sections):
        h2 = section.get("h2", "")
        for j, sub in enumerate(section.get("subsections", [])):
            image_prompt = sub.get("image_prompt", "")
            if not image_prompt and not h2:
                continue

            fname = f"{slug_safe}-s{i}-{j}.png"
            log(f"  [{img_count + 2}] 섹션 이미지 생성 중: {h2[:20]}...")
            path = generate_section_image(image_prompt, h2, fname)
            if path:
                sub["image_path"] = path
                result["sections"].append(path)
                img_count += 1
                log(f"  ✓ {Path(path).name}")
            else:
                log(f"  ✗ 섹션 이미지 실패")

            # 섹션당 최대 1장 (속도 고려)
            break

    log(f"  이미지 생성 완료: 커버 1장 + 섹션 {img_count}장")
    return result
