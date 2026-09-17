import csv
import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup


MARKET_URL = "https://stock.naver.com/market/stock/kr"
STOCK_API_URL = "https://m.stock.naver.com/api/stocks/marketValue/{market}"
OUTPUT_FILE = Path("naver_stock_data.csv")
PAGES_PER_MARKET = 20
REQUEST_DELAY = 0.3
TIMEOUT = 15

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Referer": MARKET_URL,
}


def clean_text(value):
    return " ".join(value.split())


def get_soup(session, url, params=None):
    response = session.get(url, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return BeautifulSoup(response.text, "html.parser")


def check_market_page(session):
    soup = get_soup(session, MARKET_URL)
    title = soup.select_one("title")
    if title is None or "증권" not in clean_text(title.get_text()):
        raise RuntimeError("네이버 증권 시장 페이지를 확인하지 못했습니다.")


def get_stock_data(session, market_code, market_name, page):
    response = session.get(
        STOCK_API_URL.format(market=market_code),
        params={"page": page, "pageSize": 20},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    payload = json.loads(response.text)
    rows = []

    for stock in payload.get("stocks", []):
        rows.append(
            {
                "시장": market_name,
                "종목명": stock.get("stockName", ""),
                "종목코드": stock.get("itemCode", ""),
                "현재가": stock.get("closePrice", ""),
                "전일비": stock.get("compareToPreviousClosePrice", ""),
                "등락률": stock.get("fluctuationsRatio", ""),
                "거래량": stock.get("dealQuantity", ""),
                "거래대금": stock.get("amount", ""),
                "시가총액": stock.get("marketValue", ""),
            }
        )

    return rows


def crawl_stocks(pages_per_market=PAGES_PER_MARKET):
    stocks = []
    with requests.Session() as session:
        session.headers.update(HEADERS)
        check_market_page(session)

        for market_code, market_name in ((0, "코스피"), (1, "코스닥")):
            for page in range(1, pages_per_market + 1):
                page_stocks = get_stock_data(
                    session,
                    "KOSPI" if market_code == 0 else "KOSDAQ",
                    market_name,
                    page,
                )
                if not page_stocks:
                    break

                stocks.extend(page_stocks)
                print(f"{market_name} {page}페이지: {len(page_stocks)}건 수집")
                time.sleep(REQUEST_DELAY)

    return stocks


def save_csv(stocks, output_file=OUTPUT_FILE):
    if not stocks:
        raise RuntimeError("수집된 종목 데이터가 없습니다. 페이지 구조를 확인하세요.")

    fieldnames = list(stocks[0].keys())
    with output_file.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(stocks)


def main():
    try:
        stocks = crawl_stocks()
    except requests.RequestException as error:
        print(f"네이버 증권 요청 실패: {error}")
        return

    save_csv(stocks)
    print(f"총 {len(stocks)}건 저장 완료: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()