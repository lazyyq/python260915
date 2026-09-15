from pathlib import Path
import shutil


DOWNLOADS_FOLDER = Path("/Users/kykint/Downloads")

FILE_CATEGORIES = {
    "images": {".jpg", ".jpeg"},
    "data": {".csv", ".xlsx"},
    "docs": {".txt", ".doc", ".pdf"},
    "archive": {".zip"},
}


def get_unique_destination(destination: Path) -> Path:
    """같은 이름의 파일이 있으면 새 파일명을 반환합니다."""
    if not destination.exists():
        return destination

    counter = 1
    while True:
        candidate = destination.with_name(
            f"{destination.stem}_{counter}{destination.suffix}"
        )
        if not candidate.exists():
            return candidate
        counter += 1


def organize_downloads() -> None:
    if not DOWNLOADS_FOLDER.is_dir():
        raise FileNotFoundError(
            f"다운로드 폴더를 찾을 수 없습니다: {DOWNLOADS_FOLDER}"
        )

    for folder_name in FILE_CATEGORIES:
        (DOWNLOADS_FOLDER / folder_name).mkdir(exist_ok=True)

    moved_count = 0
    for file_path in DOWNLOADS_FOLDER.iterdir():
        if not file_path.is_file():
            continue

        category = next(
            (
                folder_name
                for folder_name, extensions in FILE_CATEGORIES.items()
                if file_path.suffix.lower() in extensions
            ),
            None,
        )
        if category is None:
            continue

        destination = get_unique_destination(
            DOWNLOADS_FOLDER / category / file_path.name
        )
        shutil.move(str(file_path), str(destination))
        print(f"이동: {file_path.name} -> {category}/{destination.name}")
        moved_count += 1

    print(f"정리 완료: {moved_count}개 파일을 이동했습니다.")


if __name__ == "__main__":
    organize_downloads()