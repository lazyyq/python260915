from pathlib import Path

from openpyxl import Workbook


PRODUCT_NAMES = [
    "스마트폰",
    "노트북",
    "태블릿",
    "스마트워치",
    "무선이어폰",
    "모니터",
    "키보드",
    "마우스",
    "프린터",
    "외장하드",
]


def create_product_file(product_count=100):
    workbook = Workbook()
    worksheet = workbook.active
    if worksheet is None:
        raise RuntimeError("워크시트를 만들 수 없습니다.")
    worksheet.title = "전자제품"

    worksheet.append(["제품ID", "제품명", "가격", "수량"])

    for product_id in range(1, product_count + 1):
        product_name = PRODUCT_NAMES[(product_id - 1) % len(PRODUCT_NAMES)]
        price = 30000 + product_id * 10000
        quantity = 10 + (product_id * 7) % 91
        worksheet.append([product_id, product_name, price, quantity])

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions
    worksheet.column_dimensions["A"].width = 12
    worksheet.column_dimensions["B"].width = 16
    worksheet.column_dimensions["C"].width = 14
    worksheet.column_dimensions["D"].width = 12

    output_path = Path(__file__).with_name("ProductList.xlsx")
    workbook.save(output_path)
    return output_path


if __name__ == "__main__":
    output_path = create_product_file()
    print(f"{output_path}에 제품 데이터 100개를 저장했습니다.")