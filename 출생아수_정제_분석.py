from pathlib import Path
import re
import warnings

import matplotlib.pyplot as plt
import pandas as pd


INPUT_FILE = Path("출생아수__합계출산율__자연증가_등.xlsx")
OUTPUT_CSV = Path("출생아수_정제데이터.csv")
OUTPUT_XLSX = Path("출생아수_정제데이터.xlsx")
OUTPUT_PLOT = Path("출생아수_연도별_라인그래프.png")
OUTPUT_REPORT = Path("출생아수_분석보고서.md")


def extract_year(value: object) -> int:
    match = re.search(r"(19|20)\d{2}", str(value))
    if match is None:
        raise ValueError(f"연도를 추출할 수 없습니다: {value!r}")
    return int(match.group())


def load_and_clean(path: Path) -> pd.DataFrame:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Workbook contains no default style")
        raw = pd.read_excel(path, sheet_name="데이터", header=None)

    years = [extract_year(value) for value in raw.iloc[0, 1:]]
    indicator_names = raw.iloc[1:, 0].astype("string").str.strip()
    values = raw.iloc[1:, 1:].apply(pd.to_numeric, errors="coerce")
    values.index = indicator_names
    values.columns = years

    cleaned = values.transpose().reset_index(names="연도")
    cleaned["연도"] = pd.to_numeric(cleaned["연도"], errors="raise").astype("int64")
    cleaned = cleaned.sort_values("연도").reset_index(drop=True)

    if cleaned["연도"].duplicated().any():
        raise ValueError("중복된 연도가 있습니다.")
    if cleaned["연도"].tolist() != list(range(1970, 2024)):
        raise ValueError("연도 범위가 예상과 다릅니다.")

    return cleaned


def configure_korean_font() -> None:
    available_fonts = {font.name for font in plt.matplotlib.font_manager.fontManager.ttflist}
    for font_name in ("AppleGothic", "NanumGothic", "Malgun Gothic"):
        if font_name in available_fonts:
            plt.rcParams["font.family"] = font_name
            break
    plt.rcParams["axes.unicode_minus"] = False


def make_line_plot(data: pd.DataFrame, path: Path) -> None:
    configure_korean_font()
    figure, axis = plt.subplots(figsize=(13, 6.5), dpi=150)
    axis.plot(
        data["연도"],
        data["출생아수(명)"],
        color="#1769aa",
        linewidth=2.2,
        marker="o",
        markersize=2.8,
    )
    axis.set_title("대한민국 연도별 출생아 수 (1970~2023)", fontsize=16, pad=12)
    axis.set_xlabel("연도")
    axis.set_ylabel("출생아 수 (명)")
    axis.grid(axis="y", alpha=0.25)
    axis.set_xlim(data["연도"].min(), data["연도"].max())
    figure.tight_layout()
    figure.savefig(path, bbox_inches="tight")
    plt.close(figure)


def make_report(data: pd.DataFrame, path: Path) -> None:
    birth = data["출생아수(명)"]
    fertility = data["합계출산율(명)"]
    natural = data["자연증가건수(명)"]
    first_birth = birth.iloc[0]
    last_birth = birth.iloc[-1]
    birth_change = (last_birth / first_birth - 1) * 100
    peak_birth_row = data.loc[birth.idxmax()]
    low_birth_row = data.loc[birth.idxmin()]
    peak_fertility_row = data.loc[fertility.idxmax()]
    low_fertility_row = data.loc[fertility.idxmin()]
    negative_natural_year = data.loc[natural < 0, "연도"]
    yearly_change = birth.pct_change() * 100
    largest_drop_year = data.loc[yearly_change.idxmin(), "연도"]
    period_summary = (
        data.assign(기간=(data["연도"] // 10) * 10)
        .groupby("기간")[["출생아수(명)", "합계출산율(명)", "자연증가건수(명)"]]
        .mean()
        .round(2)
    )
    correlation = data[["출생아수(명)", "합계출산율(명)"]].corr().iloc[0, 1]
    recent = data.tail(10)
    recent_change = (recent["출생아수(명)"].iloc[-1] / recent["출생아수(명)"].iloc[0] - 1) * 100
    decline_table = (
        data.assign(전년대비변화율=yearly_change)
        .dropna(subset=["전년대비변화율"])
        .nsmallest(5, "전년대비변화율")[["연도", "전년대비변화율"]]
        .round(2)
        .to_string(index=False)
    )

    report = f"""# 출생아 수 및 출산 지표 분석

## 데이터 정제

- 원본: `{INPUT_FILE.name}`, `데이터` 시트
- 분석 기간: {data['연도'].min()}~{data['연도'].max()}년 ({len(data)}개 연도)
- 분석 지표: {', '.join(data.columns[1:])}
- 정제 방법: 연도 헤더에서 연도 추출, 지표별 문자열 공백 제거, 측정값 숫자 변환, 연도 오름차순 정렬
- 결측값 수: {int(data.isna().sum().sum())}개

## 핵심 결과

- 출생아 수: {first_birth:,.0f}명({data['연도'].iloc[0]}년)에서 {last_birth:,.0f}명({data['연도'].iloc[-1]}년)으로 {abs(birth_change):.1f}% {'감소' if birth_change < 0 else '증가'}
- 출생아 수 최고: {int(peak_birth_row['연도'])}년, {peak_birth_row['출생아수(명)']:,.0f}명
- 출생아 수 최저: {int(low_birth_row['연도'])}년, {low_birth_row['출생아수(명)']:,.0f}명
- 합계출산율 최고: {int(peak_fertility_row['연도'])}년, {peak_fertility_row['합계출산율(명)']:.3f}명
- 합계출산율 최저: {int(low_fertility_row['연도'])}년, {low_fertility_row['합계출산율(명)']:.3f}명
- 전년 대비 출생아 수 최대 감소율이 나타난 연도: {int(largest_drop_year)}년
- 자연증가건수가 음수로 전환된 첫해: {int(negative_natural_year.iloc[0])}년
- 출생아 수와 합계출산율의 피어슨 상관계수: {correlation:.3f}
- 최근 10년({int(recent['연도'].iloc[0])}~{int(recent['연도'].iloc[-1])}년) 출생아 수 변화: {abs(recent_change):.1f}% {'감소' if recent_change < 0 else '증가'}

## 10년 단위 평균

```text
{period_summary.to_string()}
```

## 전년 대비 출생아 수 감소율 상위 5개 연도

```text
{decline_table}
```

## 기술통계

```text
{data.describe().round(3).to_string()}
```

## 산출물

- `출생아수_정제데이터.csv`: 분석용 정제 데이터
- `출생아수_정제데이터.xlsx`: 분석용 정제 데이터 엑셀
- `출생아수_연도별_라인그래프.png`: 연도별 출생아 수 라인그래프
"""
    path.write_text(report, encoding="utf-8")


def main() -> None:
    data = load_and_clean(INPUT_FILE)
    data.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    data.to_excel(OUTPUT_XLSX, index=False)
    make_line_plot(data, OUTPUT_PLOT)
    make_report(data, OUTPUT_REPORT)

    print(f"정제 데이터 크기: {data.shape[0]}행 x {data.shape[1]}열")
    print(f"결측값 수: {int(data.isna().sum().sum())}")
    print(f"출생아 수 최고 연도: {int(data.loc[data['출생아수(명)'].idxmax(), '연도'])}년")
    print(f"출생아 수 최저 연도: {int(data.loc[data['출생아수(명)'].idxmin(), '연도'])}년")
    print(f"생성 파일: {OUTPUT_CSV}, {OUTPUT_XLSX}, {OUTPUT_PLOT}, {OUTPUT_REPORT}")


if __name__ == "__main__":
    main()