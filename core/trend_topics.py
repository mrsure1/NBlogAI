"""
AI/IT 최신 트렌드 토픽 풀 관리
- data/trending_topics.json 에 토픽 30개 저장
- 한 주 단위로 갱신 (수동 새로고침 가능)
- 발행 완료된 토픽은 자동 제거
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
TOPICS_FILE = DATA_DIR / "trending_topics.json"
REFRESH_INTERVAL_DAYS = 7


# 기본 풀: AI/IT 최신 트렌드 30개 (2026년 1분기 기준)
DEFAULT_TOPICS = [
    # ── AI 모델 / 서비스 ────────────────────────────────────────
    {"topic": "Claude Opus 4.7 활용법", "trend_kw": "AI 코딩 보조", "category": "AI"},
    {"topic": "GPT-5 출시 임팩트", "trend_kw": "OpenAI 2026", "category": "AI"},
    {"topic": "Gemini 3.0 한국어 성능 비교", "trend_kw": "구글 AI", "category": "AI"},
    {"topic": "Llama 4 오픈소스 활용", "trend_kw": "메타 AI", "category": "AI"},
    {"topic": "AI 에이전트 자동화 워크플로우", "trend_kw": "에이전틱 AI", "category": "AI"},
    {"topic": "프롬프트 엔지니어링 실전 가이드", "trend_kw": "프롬프트 2026", "category": "AI"},
    {"topic": "RAG 시스템 구축 입문", "trend_kw": "검색증강생성", "category": "AI"},
    {"topic": "AI 코딩 어시스턴트 비교 (Cursor vs Copilot vs Claude Code)", "trend_kw": "AI 개발도구", "category": "AI"},
    {"topic": "MCP(Model Context Protocol) 완벽 이해", "trend_kw": "AI 표준", "category": "AI"},
    {"topic": "AI 부업으로 월 100만원 벌기", "trend_kw": "AI 수익화", "category": "AI"},
    # ── AI 이미지/영상 ──────────────────────────────────────────
    {"topic": "Sora 2로 영상 만들기", "trend_kw": "AI 영상생성", "category": "AI영상"},
    {"topic": "미드저니 V7 신기능 정리", "trend_kw": "AI 이미지", "category": "AI영상"},
    {"topic": "Runway Gen-4 활용 사례", "trend_kw": "AI 영상편집", "category": "AI영상"},
    {"topic": "AI 썸네일 자동 생성 워크플로우", "trend_kw": "콘텐츠 자동화", "category": "AI영상"},
    # ── 개발 / 코딩 ─────────────────────────────────────────────
    {"topic": "바이브 코딩으로 SaaS 만들기", "trend_kw": "vibe coding", "category": "개발"},
    {"topic": "Python 3.14 신기능 활용", "trend_kw": "파이썬 2026", "category": "개발"},
    {"topic": "Next.js 15 App Router 베스트 프랙티스", "trend_kw": "리액트 2026", "category": "개발"},
    {"topic": "Rust로 백엔드 만들기", "trend_kw": "러스트 성능", "category": "개발"},
    {"topic": "AI 시대의 풀스택 개발자 로드맵", "trend_kw": "개발자 커리어", "category": "개발"},
    {"topic": "GitHub Copilot 워크스페이스 활용법", "trend_kw": "AI 협업", "category": "개발"},
    # ── 클라우드 / 인프라 ──────────────────────────────────────
    {"topic": "AWS 비용 절감 2026 전략", "trend_kw": "클라우드 최적화", "category": "클라우드"},
    {"topic": "쿠버네티스 vs 서버리스 어느 쪽을?", "trend_kw": "인프라 트렌드", "category": "클라우드"},
    {"topic": "엣지 컴퓨팅 실전 사례", "trend_kw": "엣지 AI", "category": "클라우드"},
    # ── 보안 / 데이터 ───────────────────────────────────────────
    {"topic": "AI 시대 개인정보 보호 가이드", "trend_kw": "프라이버시", "category": "보안"},
    {"topic": "딥페이크 탐지와 대응 방법", "trend_kw": "AI 보안", "category": "보안"},
    {"topic": "양자내성암호 도입 준비하기", "trend_kw": "PQC 2026", "category": "보안"},
    # ── 디바이스 / 하드웨어 ────────────────────────────────────
    {"topic": "아이폰 17 Pro 한 달 사용 후기", "trend_kw": "애플 2026", "category": "디바이스"},
    {"topic": "갤럭시 S26 울트라 AI 기능", "trend_kw": "삼성 2026", "category": "디바이스"},
    {"topic": "Apple Vision Pro 2 한국 출시 정보", "trend_kw": "VR 헤드셋", "category": "디바이스"},
    {"topic": "AI PC NPU 성능 비교", "trend_kw": "AI 노트북", "category": "디바이스"},
]


def _now_iso() -> str:
    return datetime.now().isoformat()


def _save(data: dict):
    TOPICS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_raw() -> dict | None:
    if not TOPICS_FILE.exists():
        return None
    try:
        return json.loads(TOPICS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def _needs_refresh(data: dict) -> bool:
    last = data.get("updated_at")
    if not last:
        return True
    try:
        last_dt = datetime.fromisoformat(last)
        return (datetime.now() - last_dt) > timedelta(days=REFRESH_INTERVAL_DAYS)
    except Exception:
        return True


def refresh_topics(force: bool = False) -> dict:
    """트렌드 토픽 풀 갱신 (기본값으로 채움). 향후 외부 뉴스 API 연동 시 여기 확장."""
    data = _load_raw() or {}
    existing_titles = {t["topic"] for t in data.get("topics", [])}

    # 기존 + 신규(중복 제외) 병합
    merged = list(data.get("topics", []))
    for t in DEFAULT_TOPICS:
        if t["topic"] not in existing_titles:
            merged.append({**t, "added_at": _now_iso()})

    out = {
        "updated_at": _now_iso(),
        "topics": merged[:30],
    }
    _save(out)
    return out


def load_topics() -> list[dict]:
    """현재 풀에서 토픽 리스트 반환 (없으면 자동 채움)."""
    data = _load_raw()
    if data is None or not data.get("topics"):
        data = refresh_topics(force=True)
    elif _needs_refresh(data):
        data = refresh_topics()
    return data.get("topics", [])


def remove_topic(topic: str) -> bool:
    """발행된 토픽을 풀에서 제거."""
    data = _load_raw()
    if not data:
        return False
    before = len(data.get("topics", []))
    data["topics"] = [t for t in data.get("topics", []) if t.get("topic") != topic]
    _save(data)
    return len(data["topics"]) < before


def add_custom_topic(topic: str, trend_kw: str = "", category: str = "직접 입력"):
    """사용자가 직접 토픽 추가."""
    data = _load_raw() or {"topics": []}
    data.setdefault("topics", []).insert(0, {
        "topic": topic,
        "trend_kw": trend_kw,
        "category": category,
        "added_at": _now_iso(),
    })
    data["updated_at"] = _now_iso()
    _save(data)
