import re


def analyze_seo(post_data: dict) -> dict:
    score = 0
    tips = []

    title = post_data.get("title", "")
    description = post_data.get("description", "")
    keywords = post_data.get("keywords", [])
    sections = post_data.get("sections", [])

    all_text = title + " " + description
    for sec in sections:
        for sub in sec.get("subsections", []):
            all_text += " " + " ".join(sub.get("paragraphs", []))

    total_chars = len(all_text.replace(" ", ""))

    # 제목 분석
    if 20 <= len(title) <= 60:
        score += 20
    elif len(title) < 20:
        tips.append("제목이 너무 짧습니다. 20~60자를 권장합니다.")
        score += 10
    else:
        tips.append("제목이 너무 깁니다. 60자 이내를 권장합니다.")
        score += 10

    # 메타 설명
    if 80 <= len(description) <= 160:
        score += 15
    elif description:
        tips.append("메타 설명은 80~160자가 최적입니다.")
        score += 8
    else:
        tips.append("메타 설명이 없습니다. 검색 노출에 중요합니다.")

    # 키워드 밀도
    if keywords:
        main_kw = keywords[0]
        kw_count = all_text.lower().count(main_kw.lower())
        kw_density = (kw_count / max(len(all_text.split()), 1)) * 100
        if 1 <= kw_density <= 3:
            score += 20
            tips.append(f"키워드 밀도 양호: '{main_kw}' {kw_density:.1f}%")
        elif kw_density < 1:
            tips.append(f"핵심 키워드 '{main_kw}'를 본문에 더 자주 사용하세요.")
            score += 10
        else:
            tips.append(f"키워드 과다 사용 주의: '{main_kw}' {kw_density:.1f}%")
            score += 8

    # 글 길이
    if total_chars >= 2000:
        score += 20
    elif total_chars >= 1000:
        score += 15
        tips.append("글 길이가 좋습니다. 2000자 이상이면 더 좋습니다.")
    else:
        score += 5
        tips.append("글이 너무 짧습니다. 최소 1000자 이상을 권장합니다.")

    # 구조 (H2/H3)
    h2_count = len(sections)
    if h2_count >= 4:
        score += 15
    elif h2_count >= 2:
        score += 10
        tips.append("섹션을 4개 이상 구성하면 가독성이 높아집니다.")
    else:
        tips.append("섹션 구성이 부족합니다.")
        score += 5

    # 이미지
    has_images = any(
        sub.get("image_path") or sub.get("images")
        for sec in sections
        for sub in sec.get("subsections", [])
    )
    if has_images:
        score += 10
    else:
        tips.append("이미지를 추가하면 SEO와 체류시간이 향상됩니다.")

    return {
        "score": min(score, 100),
        "grade": _grade(score),
        "tips": tips,
        "stats": {
            "total_chars": total_chars,
            "title_len": len(title),
            "desc_len": len(description),
            "sections": h2_count,
            "keywords": len(keywords),
        },
    }


def _grade(score: int) -> str:
    if score >= 85:
        return "A+"
    elif score >= 75:
        return "A"
    elif score >= 65:
        return "B+"
    elif score >= 55:
        return "B"
    elif score >= 45:
        return "C"
    else:
        return "D"
