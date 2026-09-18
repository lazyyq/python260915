# 고객 정보 관리 프로그램 PRD

## 1. 개요

Python과 SQLite3로 고객 정보를 관리하는 데스크톱 프로그램을 구현한다. 사용자 인터페이스는 PyQt의 `QTableWidget`을 이용해 저장된 고객 목록을 표시하며, 데이터 접근 로직과 화면 로직을 분리한다.

이번 단계의 산출물은 이 설계 문서뿐이다. `MyCust.py`와 `MyCust.db` 및 실제 기능 코드는 다음 구현 단계에서 생성한다.

## 2. 산출물 및 파일 정책

| 항목 | 파일명 | 역할 |
| --- | --- | --- |
| 애플리케이션 코드 | `MyCust.py` | UI 및 데이터 관리 클래스를 포함하는 실행 파일 |
| SQLite 데이터베이스 | `MyCust.db` | 고객 정보 영속 저장소 |
| 설계 문서 | `PRD.md` | 요구사항과 구현 설계 |

### 실행 환경별 데이터베이스 위치

- 일반 Python 실행에서는 `MyCust.py`가 위치한 디렉터리에 `MyCust.db`를 생성하고 사용한다.
- PyInstaller로 패키징된 환경(`sys.frozen` 및 `sys._MEIPASS` 등 감지)에서는 임시 번들 경로가 아닌 실행 가능한 `.app` 번들 또는 실행 파일이 속한 영구 디렉터리를 기준으로 `MyCust.db`를 생성하고 사용한다.
- macOS `.app` 번들에서는 사용자 데이터가 사라지지 않도록 `Contents/MacOS` 실행 파일의 상위 `.app` 디렉터리를 기준으로 데이터베이스 경로를 산출한다. 즉, 상대 경로에 의존하지 않는다.

## 3. 데이터 모델

테이블명은 `Customers`로 고정한다.

```sql
CREATE TABLE IF NOT EXISTS Customers (
    custID INTEGER PRIMARY KEY AUTOINCREMENT,
    custName TEXT NOT NULL,
    custTitle TEXT NOT NULL
);
```

| 컬럼 | SQLite 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| `custID` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | 고객 식별자. 새 레코드 생성 시 자동 부여 |
| `custName` | `TEXT` | `NOT NULL` | 고객 이름 |
| `custTitle` | `TEXT` | `NOT NULL` | 고객 직함 또는 역할 |

## 4. UI 요구사항

메인 창은 상단 작업 영역과 하단 목록 영역으로 나눈다.

### 상단 작업 영역

- 왼쪽: 세로로 `입력`, `수정`, `삭제`, `검색`, `엑셀저장` 버튼을 배치한다.
- 오른쪽: 고객 정보를 편집할 입력 컨트롤을 배치한다.
  - `custID`: 읽기 전용 입력 컨트롤 또는 레이블. 목록 선택 시 표시한다.
  - `custName`: 고객 이름 입력용 `QLineEdit`.
  - `custTitle`: 고객 직함 입력용 `QLineEdit`.
- 기본 레이아웃은 좌측 버튼 패널과 우측 폼을 담는 `QHBoxLayout`으로 구성한다.

### 하단 목록 영역

- `QTableWidget`으로 `Customers` 데이터를 출력한다.
- 컬럼은 `custID`, `custName`, `custTitle` 순서로 표시한다.
- 행 선택 시 선택한 고객 정보를 상단 폼에 채운다.
- 목록은 입력, 수정, 삭제 후 즉시 다시 조회하여 최신 상태를 반영한다.

## 5. 기능 요구사항

| 기능 | 사용자 동작 | 기대 결과 |
| --- | --- | --- |
| 입력 | 이름과 직함을 입력하고 `입력` 클릭 | 새 고객이 저장되고 목록을 갱신하며 폼을 초기화 |
| 수정 | 목록에서 고객을 선택하고 정보를 변경한 뒤 `수정` 클릭 | 선택한 `custID`의 고객 정보만 변경하고 목록 갱신 |
| 삭제 | 목록에서 고객을 선택하고 `삭제` 클릭 | 확인 절차 후 선택 고객을 삭제하고 목록 갱신 |
| 검색 | 검색어를 입력하고 `검색` 클릭 | 이름 또는 직함에 검색어를 포함한 고객만 목록에 표시 |
| 엑셀저장 | `엑셀저장` 클릭 후 저장 경로 선택 | 저장된 전체 고객 정보를 `.xlsx` 파일로 내보냄 |
| 전체 조회 | 프로그램 시작 또는 검색어 비움 | 전체 고객 목록을 `custID` 기준으로 표시 |

### 입력 검증 및 예외 처리

- 이름과 직함은 공백만으로 저장할 수 없다.
- 수정과 삭제는 반드시 목록에서 고객을 선택한 상태에서만 가능하다.
- 데이터베이스 예외가 발생하면 사용자에게 오류 메시지를 표시하고 애플리케이션이 비정상 종료되지 않게 한다.
- SQL은 값 바인딩(parameterized query)을 사용한다.
- 엑셀 저장은 `openpyxl`을 사용하며, 저장할 데이터가 없거나 파일 저장에 실패하면 사용자에게 안내한다.

## 6. 클래스 설계

### `CustomerManager`

SQLite 데이터베이스 연결, 테이블 초기화, CRUD를 전담한다. 화면 위젯을 직접 다루지 않는다.

| 메서드 | 책임 |
| --- | --- |
| `__init__(db_path)` | DB 경로를 보관하고 연결 준비 |
| `initialize_database()` | `Customers` 테이블이 없으면 생성 |
| `create_customer(name, title)` | 고객 1건 생성, 생성된 ID 반환 |
| `get_customers(keyword=None)` | 전체 목록 또는 이름·직함 기준 검색 결과 반환 |
| `update_customer(cust_id, name, title)` | 지정 고객 정보 수정 |
| `delete_customer(cust_id)` | 지정 고객 삭제 |
| `close()` | 연결이 유지되는 구조라면 DB 연결 종료 |

반환 데이터는 UI가 쉽게 소비할 수 있도록 `custID`, `custName`, `custTitle`을 포함한 튜플 또는 데이터 클래스의 목록으로 통일한다.

### `CustomerView`

`QMainWindow`를 상속하여 화면 생성과 사용자 상호작용을 전담한다. SQL을 직접 작성하거나 실행하지 않고 `CustomerManager`를 호출한다.

| 메서드 | 책임 |
| --- | --- |
| `setup_ui()` | 버튼, 입력 폼, 테이블 및 레이아웃 생성 |
| `connect_signals()` | 버튼 클릭과 테이블 선택 이벤트 연결 |
| `load_customers(keyword=None)` | Manager에서 받은 데이터를 `QTableWidget`에 렌더링 |
| `handle_create()` | 입력 검증 후 생성 요청 |
| `handle_update()` | 선택·입력 검증 후 수정 요청 |
| `handle_delete()` | 선택 확인 및 삭제 요청 |
| `handle_search()` | 검색어로 목록 요청 |
| `populate_form_from_selection()` | 선택 행 데이터를 폼에 반영 |
| `clear_form()` | 입력 폼 및 선택 상태 초기화 |
| `handle_export_excel()` | 저장 경로 선택 후 전체 고객 데이터를 엑셀 파일로 저장 |

## 7. 구현 흐름

1. 애플리케이션 시작 시 실행 환경을 감지하여 DB의 절대 경로를 결정한다.
2. `CustomerManager`가 `Customers` 테이블을 초기화한다.
3. `CustomerView`가 UI를 구성하고 전체 고객 목록을 로드한다.
4. 사용자의 CRUD 또는 검색 이벤트는 View의 핸들러로 전달된다.
5. View는 검증 후 Manager를 호출하고, 성공 시 테이블을 다시 로드한다.

## 8. 완료 기준

- `MyCust.py` 실행 시 지정된 구조의 화면이 보인다.
- `MyCust.db`에 `Customers` 테이블과 요구된 컬럼·자동증가 기본키가 생성된다.
- 입력, 수정, 삭제, 검색 결과가 `QTableWidget`에 정확히 반영된다.
- 일반 실행과 PyInstaller 패키지 실행 모두에서 데이터베이스 경로가 영속 가능한 위치로 결정된다.
- `CustomerManager`와 `CustomerView`의 책임이 분리되어 있다.
