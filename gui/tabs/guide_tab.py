from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit


GUIDE_TEXT = """
# NBlogAI — 사용 가이드

## 빠른 시작 (5분)

1. **공통 설정** (상단) → 네이버 ID/PW, Gemini API 키 입력 → [설정 저장]
2. **블로그 자동 포스팅** 탭 → 주제 키워드 입력
3. **① 포스트 생성** → **② 이미지 생성** → **③ 블로그 발행**

---

## 공통 설정

| 항목 | 설명 |
|------|------|
| Naver ID | 네이버 로그인 아이디 |
| Naver PW | 네이버 비밀번호 (로컬 .env 파일에만 저장) |
| Gemini API Key | Google AI Studio에서 발급 (https://aistudio.google.com/app/apikey) |

---

## 블로그 자동 포스팅 탭

### 입력 항목
- **주제 키워드**: 쓰고 싶은 블로그 주제
- **트렌드 키워드**: 유행하는 키워드와 연결 (선택사항)
- **시리즈 편수**: 1~5편 연속 생성
- **글 분량**: 짧음(500자) / 표준(1000자) / 길게(2000자)
- **이미지 크기**: 소형 / 중형 / 대형

### 3단계 버튼
1. **① 포스트 생성 (AI)**: Gemini AI로 제목, 개요, 본문 작성 (~30초)
2. **② 이미지 생성**: 각 섹션에 맞는 이미지 자동 생성 (~20초)
3. **③ 블로그 발행**: Selenium으로 네이버 블로그에 자동 발행

### 사이드 패널 기능
- **📅 예약 발행 큐**: 글을 예약 시간에 자동 발행
- **📊 SEO 분석**: 글의 SEO 점수와 개선 팁 제공
- **📂 외부 JSON 발행**: 다른 도구에서 만든 JSON 파일 발행
- **♻ 글 리라이터**: 현재 글을 다른 스타일로 재작성

---

## 이웃 늘리기 탭

- **서로이웃 신청 봇**: 키워드로 블로거를 찾아 자동 이웃 신청
- **최신글 좋아요**: 이웃 신청 전 최신 글에 자동 좋아요
- **AI 맞춤 메시지**: 상대방 글 내용에 맞는 진심 어린 메시지 자동 작성
- **이웃 피드 공감**: 피드의 글들에 자동으로 공감
- **AI 댓글 자동 답글**: 내 블로그 댓글에 AI가 자동 답글

---

## 성과 분석 탭

- 내 블로그 포스트별 조회수, 공감수, 댓글수 통계
- 어떤 주제의 글이 잘 받는지 분석

---

## 문제 해결

**네이버 로그인 실패**
→ 2단계 인증 해제 후 재시도
→ 브라우저 창에서 직접 로그인 완료 후 계속 진행됩니다

**이미지 생성 실패**
→ Gemini API 무료 티어는 Imagen을 지원하지 않을 수 있습니다
→ 이 경우 자동으로 플레이스홀더 이미지가 생성됩니다

**발행 버튼을 못 찾는 경우**
→ 네이버가 UI를 변경했을 수 있습니다
→ 브라우저 창이 열리면 수동으로 발행 버튼을 클릭할 수 있습니다

---

## Gemini API 키 발급 방법

1. https://aistudio.google.com/app/apikey 접속
2. Google 계정 로그인
3. [Create API key] 클릭
4. 생성된 키를 복사하여 공통 설정에 입력

---

**행복한 블로그 운영이 되세요! 🎉**
"""


class GuideTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        viewer = QTextEdit()
        viewer.setReadOnly(True)
        viewer.setMarkdown(GUIDE_TEXT)
        viewer.setStyleSheet("""
            QTextEdit {
                background-color: #24273a;
                color: #cdd6f4;
                font-size: 13px;
                padding: 16px;
                border: none;
            }
        """)
        layout.addWidget(viewer)
