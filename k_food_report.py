from __future__ import annotations

from datetime import datetime
from html import unescape
from pathlib import Path
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt


SEARCH_TERMS = ["K푸드", "한국 음식", "K-food"]
MAX_ITEMS = 15
OUTPUT_PATH = Path(__file__).with_name("k-food.docx")


def clean_text(text: str | None) -> str:
    """RSS 내용에 포함된 HTML 태그와 공백을 정리합니다."""
    if not text:
        return "내용 없음"
    without_tags = text.replace("<b>", "").replace("</b>", "")
    return " ".join(unescape(without_tags).split())


def collect_news(search_term: str, limit: int = MAX_ITEMS) -> list[dict[str, str]]:
    """Google News RSS에서 검색어에 맞는 최신 기사 목록을 가져옵니다."""
    rss_url = (
        "https://news.google.com/rss/search?q="
        f"{quote(search_term)}&hl=ko&gl=KR&ceid=KR:ko"
    )
    request = Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})

    with urlopen(request, timeout=15) as response:
        root = ElementTree.fromstring(response.read())

    articles: list[dict[str, str]] = []
    for item in root.findall("./channel/item"):
        title = clean_text(item.findtext("title"))
        link = item.findtext("link", "")
        description = clean_text(item.findtext("description"))
        published_at = item.findtext("pubDate", "")

        source = item.find("source")
        source_name = source.text.strip() if source is not None and source.text else "출처 미상"

        articles.append(
            {
                "title": title,
                "link": link,
                "description": description,
                "published_at": published_at,
                "source": source_name,
                "domain": urlparse(link).netloc,
            }
        )

        if len(articles) >= limit:
            break

    return articles


def collect_k_food_news() -> list[dict[str, str]]:
    """여러 검색어로 수집하고 같은 링크의 중복 기사를 제거합니다."""
    unique_articles: dict[str, dict[str, str]] = {}

    for search_term in SEARCH_TERMS:
        try:
            articles = collect_news(search_term)
        except Exception as error:
            print(f"'{search_term}' 수집 실패: {error}")
            continue

        for article in articles:
            unique_articles.setdefault(article["link"], article)

    return list(unique_articles.values())[:MAX_ITEMS]


def create_word_file(articles: list[dict[str, str]], output_path: Path = OUTPUT_PATH) -> Path:
    document = Document()
    normal_style = document.styles["Normal"]
    normal_style.font.name = "Malgun Gothic"
    normal_style.font.size = Pt(10)

    title = document.add_heading("K-Food 최신 자료 모음", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    document.add_paragraph(
        f"수집일: {datetime.now():%Y년 %m월 %d일 %H:%M} | 자료 수: {len(articles)}건"
    )
    document.add_paragraph(
        "Google News RSS에서 'K푸드', '한국 음식', 'K-food'를 검색해 수집한 기사 목록입니다."
    )

    if not articles:
        document.add_paragraph("수집된 자료가 없습니다. 인터넷 연결을 확인해 주세요.")
    else:
        for number, article in enumerate(articles, start=1):
            document.add_heading(f"{number}. {article['title']}", level=2)
            document.add_paragraph(f"출처: {article['source']} ({article['domain']})")
            document.add_paragraph(f"게시일: {article['published_at']}")
            document.add_paragraph(f"요약: {article['description']}")
            document.add_paragraph(f"원문 링크: {article['link']}")

    document.save(output_path)
    return output_path


if __name__ == "__main__":
    news = collect_k_food_news()
    saved_path = create_word_file(news)
    print(f"{len(news)}건의 K-Food 자료를 {saved_path}에 저장했습니다.")