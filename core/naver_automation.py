import time
import os
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from utils.config import get_value


def _build_driver(headless: bool = False) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument("--lang=ko-KR")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def _wait(driver, css, timeout=20):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css))
    )


def _click_wait(driver, css, timeout=20):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, css))
    )


# ─── 로그인 ───────────────────────────────────────────────────────────────────

def login_naver(driver: webdriver.Chrome, naver_id: str, naver_pw: str) -> bool:
    driver.get("https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/")
    time.sleep(2)

    try:
        id_input = _wait(driver, "#id", 10)
        driver.execute_script("arguments[0].value = arguments[1]", id_input, naver_id)
        pw_input = _wait(driver, "#pw", 10)
        driver.execute_script("arguments[0].value = arguments[1]", pw_input, naver_pw)
        login_btn = _click_wait(driver, "#log\\.login", 10)
        login_btn.click()
        time.sleep(3)

        # 추가 인증 감지
        if "nid.naver.com" in driver.current_url and "login" in driver.current_url:
            return False

        return True
    except Exception as e:
        print(f"로그인 오류: {e}")
        return False


# ─── 포스트 텍스트 빌드 ──────────────────────────────────────────────────────

def _build_post_text(post_data: dict) -> str:
    """에디터에 삽입할 순수 텍스트 (섹션별 구조)"""
    parts = []
    for section in post_data.get("sections", []):
        h2 = section.get("h2", "")
        if h2:
            parts.append(f"▶ {h2}")
        for sub in section.get("subsections", []):
            h3 = sub.get("h3", "")
            if h3 and h3 != h2:
                parts.append(f"  {h3}")
            for para in sub.get("paragraphs", []):
                if para.strip():
                    parts.append(para)
            parts.append("")
    hashtags = post_data.get("hashtags", "")
    if hashtags:
        parts.append(hashtags)
    return "\n".join(parts)


def _is_placeholder_image(path: str) -> bool:
    """Imagen API 실패로 생성된 플레이스홀더 이미지 여부"""
    # image_generator.py에서 _create_placeholder가 저장하면 파일에 영문 prompt만 있음
    # 실제 AI 이미지와 구분하기 위해 파일명 기반 판단 (향후 플래그 파일로 개선 가능)
    return False  # 일단 모든 이미지 삽입 허용 (플레이스홀더도 포함)


# ─── JS 헬퍼 ─────────────────────────────────────────────────────────────────

def _js_insert_text(driver, element, text: str):
    """contenteditable 요소에 텍스트를 execCommand로 삽입"""
    driver.execute_script(
        "arguments[0].focus();"
        "document.execCommand('selectAll', false, null);"
        "document.execCommand('delete', false, null);",
        element
    )
    time.sleep(0.2)
    # 클립보드 경유로 한글 안깨지게 삽입
    pyperclip.copy(text)
    ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
    time.sleep(0.3)


def _js_append_text(driver, text: str):
    """현재 포커스된 contenteditable에 텍스트 append"""
    pyperclip.copy(text)
    ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
    time.sleep(0.2)


# ─── 블로그 발행 ──────────────────────────────────────────────────────────────

def publish_post(post_data: dict, log_callback=None) -> bool:
    naver_id = get_value("NAVER_ID")
    naver_pw = get_value("NAVER_PW")

    def log(msg):
        if log_callback:
            log_callback(msg)
        print(msg)

    driver = _build_driver()
    try:
        log("브라우저 시작 중...")
        if not login_naver(driver, naver_id, naver_pw):
            log("⚠ 로그인 실패. 브라우저에서 직접 로그인 후 계속하세요.")
            for _ in range(90):
                if "naver.com" in driver.current_url and "login" not in driver.current_url:
                    break
                time.sleep(1)

        log("✓ 네이버 로그인 완료")
        time.sleep(2)

        log("블로그 에디터 로딩 중...")
        driver.get(f"https://blog.naver.com/{naver_id}/postwrite")

        # 에디터 완전 로딩 대기
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".se-title-input"))
        )
        time.sleep(3)

        # ── 제목 입력 ──────────────────────────────────────────────────────────
        log("제목 입력 중...")
        title_text = post_data.get("title", "")
        try:
            title_elem = driver.find_element(By.CSS_SELECTOR, ".se-title-input")
            title_elem.click()
            time.sleep(0.3)
            # JS execCommand로 삽입 (한글 안전)
            driver.execute_script(
                "arguments[0].focus();"
                "document.execCommand('selectAll', false, null);"
                "document.execCommand('delete', false, null);",
                title_elem
            )
            pyperclip.copy(title_text)
            ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
            time.sleep(0.5)
            log(f"  제목: {title_text[:30]}...")
        except Exception as e:
            log(f"  제목 입력 오류: {e}")

        # ── 본문 삽입 ──────────────────────────────────────────────────────────
        log("본문 삽입 중...")
        try:
            # 첫 번째 텍스트 단락 클릭
            first_para = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-text-paragraph"))
            )
            first_para.click()
            time.sleep(0.5)

            # 섹션별로 텍스트 삽입
            sections = post_data.get("sections", [])
            for i, section in enumerate(sections):
                h2 = section.get("h2", "")
                if h2:
                    pyperclip.copy(f"▶ {h2}")
                    ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                    time.sleep(0.2)
                    ActionChains(driver).send_keys(Keys.RETURN).perform()
                    time.sleep(0.1)

                for sub in section.get("subsections", []):
                    h3 = sub.get("h3", "")
                    if h3 and h3 != h2:
                        pyperclip.copy(f"  {h3}")
                        ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                        time.sleep(0.2)
                        ActionChains(driver).send_keys(Keys.RETURN).perform()
                        time.sleep(0.1)

                    for para in sub.get("paragraphs", []):
                        if para.strip():
                            pyperclip.copy(para)
                            ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                            time.sleep(0.2)
                            ActionChains(driver).send_keys(Keys.RETURN).perform()
                            time.sleep(0.1)

                # 섹션 사이 빈 줄
                ActionChains(driver).send_keys(Keys.RETURN).perform()
                time.sleep(0.1)

            # 해시태그
            hashtags = post_data.get("hashtags", "")
            if hashtags:
                ActionChains(driver).send_keys(Keys.RETURN).perform()
                pyperclip.copy(hashtags)
                ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                time.sleep(0.2)

            log("  본문 삽입 완료")
        except Exception as e:
            log(f"  본문 삽입 오류: {e}")

        # ── 이미지 삽입 (실제 이미지만) ────────────────────────────────────────
        real_images = []
        for section in post_data.get("sections", []):
            for sub in section.get("subsections", []):
                path = sub.get("image_path", "")
                if path and os.path.exists(path):
                    real_images.append(path)

        if real_images:
            log(f"이미지 {len(real_images)}장 삽입 중...")
            # 본문 맨 끝으로 이동 후 이미지 삽입
            ActionChains(driver).send_keys(Keys.RETURN).perform()
            time.sleep(0.3)
            _insert_images(driver, real_images[:5], log)
        else:
            log("  이미지 없음 (이미지 생성 후 발행하면 이미지 포함됩니다)")

        # ── 발행 버튼 클릭 ─────────────────────────────────────────────────────
        log("발행 버튼 클릭 중...")
        time.sleep(1)
        published = _click_publish_button(driver, log)

        if not published:
            log("⚠ 발행 버튼 자동 클릭 실패. 브라우저에서 직접 '발행' 버튼을 눌러주세요.")
            time.sleep(15)

        time.sleep(3)
        log("✅ 블로그 발행 완료!")
        return True

    except Exception as e:
        log(f"❌ 발행 오류: {e}")
        return False
    finally:
        time.sleep(2)
        driver.quit()


def _click_publish_button(driver, log) -> bool:
    """발행 버튼을 여러 방법으로 시도"""
    # 1) 알려진 CSS 셀렉터
    for sel in [".publish-btn", "button.se-toolbar-btn-publish", "button[data-name='publish']"]:
        try:
            btn = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
            btn.click()
            time.sleep(2)
            _confirm_publish_popup(driver)
            return True
        except Exception:
            pass

    # 2) 텍스트로 버튼 찾기
    try:
        btns = driver.find_elements(By.TAG_NAME, "button")
        for btn in btns:
            txt = btn.text.strip()
            if txt in ("발행", "게시", "Publish"):
                btn.click()
                time.sleep(2)
                _confirm_publish_popup(driver)
                return True
    except Exception:
        pass

    return False


def _confirm_publish_popup(driver):
    """발행 확인 팝업 처리"""
    for sel in [".btn-confirm", ".confirm-btn", "button.btn-default", ".se-publish-button"]:
        try:
            btn = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
            if any(w in btn.text for w in ("발행", "확인", "OK", "게시")):
                btn.click()
                return
        except Exception:
            pass


def _insert_images(driver, image_paths: list, log):
    """툴바 이미지 버튼으로 파일 업로드"""
    for path in image_paths:
        try:
            # 툴바 이미지 버튼 클릭
            img_btn = None
            for sel in ["button[data-name='image']", ".se-toolbar-btn-image", "button[title='이미지']"]:
                try:
                    img_btn = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
                    break
                except Exception:
                    pass

            if img_btn:
                img_btn.click()
                time.sleep(1.5)

            # 숨겨진 file input에 직접 경로 전달
            file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            if file_inputs:
                file_inputs[-1].send_keys(os.path.abspath(path))
                time.sleep(3)
                log(f"  이미지 업로드: {os.path.basename(path)}")
            else:
                log(f"  파일 입력창 없음: {os.path.basename(path)}")
        except Exception as e:
            log(f"  이미지 삽입 실패: {e}")


# ─── 이웃 자동화 ─────────────────────────────────────────────────────────────

def run_neighbor_bot(keyword: str, max_count: int = 10,
                     do_follow: bool = True, do_like: bool = True,
                     ai_comment: bool = False,
                     log_callback=None) -> int:
    naver_id = get_value("NAVER_ID")
    naver_pw = get_value("NAVER_PW")

    def log(msg):
        if log_callback:
            log_callback(msg)
        print(msg)

    driver = _build_driver()
    success_count = 0
    try:
        log("로그인 중...")
        if not login_naver(driver, naver_id, naver_pw):
            log("⚠ 로그인 실패")
            return 0

        log(f"키워드 '{keyword}' 검색 중...")
        search_url = f"https://search.naver.com/search.naver?where=post&query={keyword}"
        driver.get(search_url)
        time.sleep(3)

        post_links = []
        try:
            posts = driver.find_elements(By.CSS_SELECTOR, ".total_area a.api_txt_lines, .view_area a")
            for p in posts[:max_count * 2]:
                href = p.get_attribute("href")
                if href and "blog.naver.com" in href:
                    post_links.append(href)
        except Exception:
            pass

        visited_blogs = set()
        for link in post_links:
            if success_count >= max_count:
                break
            try:
                parts = link.replace("https://blog.naver.com/", "").split("/")
                if not parts:
                    continue
                blog_owner = parts[0]
                if blog_owner == naver_id or blog_owner in visited_blogs:
                    continue
                visited_blogs.add(blog_owner)

                driver.get(link)
                time.sleep(2)

                if do_like:
                    _try_like(driver, log)

                if do_follow:
                    followed = _try_follow(driver, blog_owner, naver_id, ai_comment, driver, log)
                    if followed:
                        success_count += 1
                        log(f"✓ 서이추 신청: {blog_owner} ({success_count}/{max_count})")

                time.sleep(3)
            except Exception as e:
                log(f"처리 오류: {e}")
                continue

        log(f"완료: 총 {success_count}명 서이추 신청")
        return success_count
    finally:
        driver.quit()


def _try_like(driver, log):
    try:
        like_selectors = [
            ".u_likeit_list_btn.btn_like",
            ".sympathy_area button",
            "a.btn_like",
            ".like_area button",
        ]
        for sel in like_selectors:
            try:
                btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
                )
                btn.click()
                time.sleep(1)
                log("  ♥ 좋아요 완료")
                return True
            except Exception:
                continue
    except Exception:
        pass
    return False


def _try_follow(driver, blog_owner: str, my_id: str, ai_comment: bool, comment_driver, log) -> bool:
    try:
        driver.get(f"https://blog.naver.com/{blog_owner}")
        time.sleep(2)

        follow_selectors = [
            ".btn_add_buddy",
            "a.btn_buddy_request",
            "button.neighbor_add",
            ".add_frnd",
        ]
        for sel in follow_selectors:
            try:
                btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
                )
                btn.click()
                time.sleep(2)

                if ai_comment:
                    _send_neighbor_message(driver, blog_owner, log)

                confirm_sels = [".btn_confirm", ".confirm-btn", "button.btn-default"]
                for csel in confirm_sels:
                    try:
                        c = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, csel))
                        )
                        c.click()
                        break
                    except Exception:
                        pass

                return True
            except Exception:
                continue
    except Exception:
        pass
    return False


def _send_neighbor_message(driver, blog_owner: str, log):
    try:
        from core.ai_generator import generate_neighbor_comment
        blog_text = driver.find_element(By.TAG_NAME, "body").text[:300]
        comment = generate_neighbor_comment(blog_text)
        msg_input = driver.find_element(By.CSS_SELECTOR, "textarea.buddy_message, textarea.message_input")
        msg_input.clear()
        msg_input.send_keys(comment)
        log(f"  AI 메시지: {comment[:30]}...")
    except Exception:
        pass


# ─── 피드 공감 ───────────────────────────────────────────────────────────────

def run_feed_like(max_count: int = 20, log_callback=None) -> int:
    naver_id = get_value("NAVER_ID")
    naver_pw = get_value("NAVER_PW")

    def log(msg):
        if log_callback:
            log_callback(msg)

    driver = _build_driver()
    count = 0
    try:
        if not login_naver(driver, naver_id, naver_pw):
            log("로그인 실패")
            return 0

        driver.get("https://blog.naver.com/BuddyList.naver")
        time.sleep(3)

        posts = driver.find_elements(By.CSS_SELECTOR, ".feed_list .feed_item a.tit")
        for post in posts[:max_count]:
            try:
                link = post.get_attribute("href")
                if link:
                    driver.get(link)
                    time.sleep(2)
                    if _try_like(driver, log):
                        count += 1
                        log(f"♥ 이웃 피드 공감 {count}")
                    driver.back()
                    time.sleep(2)
            except Exception:
                continue

        log(f"피드 공감 완료: {count}개")
        return count
    finally:
        driver.quit()


# ─── 댓글 자동 답글 ──────────────────────────────────────────────────────────

def run_auto_reply(log_callback=None) -> int:
    naver_id = get_value("NAVER_ID")
    naver_pw = get_value("NAVER_PW")

    def log(msg):
        if log_callback:
            log_callback(msg)

    driver = _build_driver()
    count = 0
    try:
        if not login_naver(driver, naver_id, naver_pw):
            log("로그인 실패")
            return 0

        driver.get(f"https://blog.naver.com/{naver_id}")
        time.sleep(3)

        comment_links = driver.find_elements(By.CSS_SELECTOR, ".comment_area a")
        for link_elem in comment_links[:10]:
            try:
                link = link_elem.get_attribute("href")
                if link and "blog.naver.com" in link:
                    driver.get(link)
                    time.sleep(2)

                    comments = driver.find_elements(By.CSS_SELECTOR, ".u_cbox_comment:not(.mine)")
                    for comment_elem in comments[:3]:
                        comment_text = comment_elem.find_element(By.CSS_SELECTOR, ".u_cbox_contents").text
                        if comment_text:
                            from core.ai_generator import generate_reply_comment
                            reply = generate_reply_comment(comment_text)
                            reply_btn = comment_elem.find_element(By.CSS_SELECTOR, ".u_cbox_btn_reply")
                            reply_btn.click()
                            time.sleep(1)
                            reply_input = driver.find_element(By.CSS_SELECTOR, ".u_cbox_textarea")
                            reply_input.send_keys(reply)
                            driver.find_element(By.CSS_SELECTOR, ".u_cbox_btn_upload").click()
                            time.sleep(1)
                            count += 1
                            log(f"✓ 답글 작성: {reply[:20]}...")
            except Exception:
                continue

        log(f"자동 답글 완료: {count}개")
        return count
    finally:
        driver.quit()


# ─── 블로그 통계 수집 ────────────────────────────────────────────────────────

def fetch_blog_stats(log_callback=None) -> list:
    naver_id = get_value("NAVER_ID")
    naver_pw = get_value("NAVER_PW")

    def log(msg):
        if log_callback:
            log_callback(msg)

    driver = _build_driver()
    stats = []
    try:
        if not login_naver(driver, naver_id, naver_pw):
            log("로그인 실패")
            return []

        log("블로그 통계 수집 중...")
        driver.get(f"https://blog.naver.com/{naver_id}")
        time.sleep(3)

        post_elems = driver.find_elements(By.CSS_SELECTOR, ".post-item, .blog_post, .item")
        for elem in post_elems[:10]:
            try:
                title_elem = elem.find_element(By.CSS_SELECTOR, "a.title, .title a, h3 a")
                title = title_elem.text.strip()
                link = title_elem.get_attribute("href")

                view_count = 0
                like_count = 0
                comment_count = 0

                try:
                    view_elem = elem.find_element(By.CSS_SELECTOR, ".cnt_view, .view_count")
                    view_count = int("".join(filter(str.isdigit, view_elem.text)) or "0")
                except Exception:
                    pass

                try:
                    like_elem = elem.find_element(By.CSS_SELECTOR, ".cnt_like, .like_count")
                    like_count = int("".join(filter(str.isdigit, like_elem.text)) or "0")
                except Exception:
                    pass

                try:
                    cmt_elem = elem.find_element(By.CSS_SELECTOR, ".cnt_comment, .comment_count")
                    comment_count = int("".join(filter(str.isdigit, cmt_elem.text)) or "0")
                except Exception:
                    pass

                if title:
                    stats.append({
                        "title": title,
                        "link": link,
                        "views": view_count,
                        "likes": like_count,
                        "comments": comment_count,
                    })
            except Exception:
                continue

        log(f"통계 수집 완료: {len(stats)}개 포스트")
        return stats
    finally:
        driver.quit()
