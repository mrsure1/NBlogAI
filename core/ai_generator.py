import json
import re
from google import genai
from google.genai import types
from utils.config import get_value

WRITING_STYLES = [
    "정보형 가이드 스타일 (객관적이고 유익한 정보 중심)",
    "체험 후기형 스타일 (개인 경험과 감정을 담은 생생한 후기)",
    "비교 분석형 스타일 (여러 옵션을 비교하는 전문적 분석)",
    "Q&A형 스타일 (독자의 궁금증을 질문-답변 형식으로 해결)",
    "랭킹형 스타일 (TOP 리스트 형태로 핵심 정보 전달)",
    "스토리텔링형 스타일 (흥미로운 이야기 흐름으로 정보 전달)",
    "전문가 칼럼형 스타일 (권위 있는 전문가 시각의 깊이 있는 분석)",
    "초보자 가이드형 스타일 (쉽고 친절한 단계별 설명)",
    "트렌드 분석형 스타일 (최신 트렌드와 연결된 현대적 시각)",
    "문제 해결형 스타일 (독자의 고민을 해결하는 솔루션 중심)",
    "인터뷰형 스타일 (가상 인터뷰 형식의 생동감 있는 구성)",
    "체크리스트형 스타일 (실용적인 체크리스트와 요약 중심)",
    "비하인드 스토리형 스타일 (알려지지 않은 흥미로운 이면 공개)",
]

LENGTH_TOKENS = {"짧음": 500, "표준": 1000, "길게": 2000}


def _get_client():
    api_key = get_value("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Gemini API 키가 설정되지 않았습니다.")
    return genai.Client(api_key=api_key)


def _generate_json(prompt: str) -> str:
    client = _get_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            max_output_tokens=8192,
            response_mime_type="application/json",
        ),
    )
    return response.text.strip()


def _generate_text(prompt: str) -> str:
    client = _get_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            max_output_tokens=2048,
        ),
    )
    return response.text.strip()


def _parse_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def generate_post(topic: str, trend_kw: str = "", length: str = "표준", style_index: int = 0) -> dict:
    style = WRITING_STYLES[style_index % len(WRITING_STYLES)]
    target_length = LENGTH_TOKENS.get(length, 1000)
    trend_part = f"트렌드 키워드: {trend_kw}\n" if trend_kw else ""

    prompt = f"""당신은 한국 네이버 블로그 전문 작가입니다.
주어진 주제로 SEO에 최적화된 블로그 포스트를 {style}로 작성해주세요.

주제: {topic}
{trend_part}목표 글자 수: 약 {target_length}자

반드시 아래 JSON 형식으로만 응답하세요 (코드블록 없이 순수 JSON):
{{
  "title": "클릭을 유도하는 매력적인 제목",
  "description": "검색 결과에 표시될 메타 설명 (150자 이내)",
  "keywords": ["핵심키워드1", "핵심키워드2", "핵심키워드3", "키워드4", "키워드5"],
  "sections": [
    {{
      "h2": "섹션 제목",
      "subsections": [
        {{
          "h3": "소제목",
          "paragraphs": ["단락1 내용...", "단락2 내용..."],
          "image_prompt": "이 섹션에 어울리는 이미지 설명 (영어로)"
        }}
      ]
    }}
  ],
  "hashtags": "#해시태그1 #해시태그2 #해시태그3 #해시태그4 #해시태그5 #해시태그6 #해시태그7 #해시태그8 #해시태그9 #해시태그10"
}}

섹션은 최소 4개 이상, 각 섹션은 최소 1개의 subsection을 포함해야 합니다.
글자 수는 모든 paragraphs 합산 기준 {target_length}자 이상 작성해주세요."""

    text = _generate_json(prompt)
    return _parse_json(text)


def rewrite_post(original_content: str, style_index: int = 0) -> dict:
    style = WRITING_STYLES[style_index % len(WRITING_STYLES)]

    prompt = f"""다음 블로그 글을 {style}로 완전히 새롭게 재작성해주세요.
내용의 핵심 정보는 유지하되, 문체와 구성을 완전히 바꿔주세요.

원본 글:
{original_content[:2000]}

반드시 아래 JSON 형식으로만 응답하세요:
{{
  "title": "새로운 제목",
  "description": "새로운 메타 설명",
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "sections": [
    {{
      "h2": "섹션 제목",
      "subsections": [
        {{
          "h3": "소제목",
          "paragraphs": ["단락 내용..."],
          "image_prompt": "image description in English"
        }}
      ]
    }}
  ],
  "hashtags": "#해시태그1 #해시태그2"
}}"""

    text = _generate_json(prompt)
    return _parse_json(text)


def generate_neighbor_comment(blog_content: str) -> str:
    prompt = f"""다음 블로그 글을 읽고 진심 어린 서로이웃 신청 댓글을 작성해주세요.
댓글은 자연스럽고 진정성 있어야 하며, 100자 이내로 작성해주세요.
글 내용을 구체적으로 언급하여 실제로 읽었다는 것을 보여주세요.

블로그 글 내용:
{blog_content[:500]}

댓글만 작성해주세요 (따옴표나 설명 없이):"""

    return _generate_text(prompt)


def generate_reply_comment(original_comment: str) -> str:
    prompt = f"""블로그에 달린 다음 댓글에 대한 자연스럽고 친근한 답글을 작성해주세요.
50자 이내로 간결하게 작성해주세요.

댓글: {original_comment}

답글만 작성해주세요:"""

    return _generate_text(prompt)
