

import os
import shutil
import logging
import argparse
from pathlib import Path
from collections import defaultdict



CATEGORY_MAP = {
   
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images",
    ".gif": "Images", ".bmp": "Images", ".svg": "Images",
    ".webp": "Images", ".tiff": "Images", ".ico": "Images",
   
    ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents",
    ".txt": "Documents", ".odt": "Documents", ".rtf": "Documents",
    ".xls": "Documents", ".xlsx": "Documents", ".ppt": "Documents",
    ".pptx": "Documents", ".csv": "Documents",
 
    ".mp4": "Videos", ".mkv": "Videos", ".avi": "Videos",
    ".mov": "Videos", ".wmv": "Videos", ".flv": "Videos",
    ".webm": "Videos",
  
    ".mp3": "Music", ".wav": "Music", ".flac": "Music",
    ".aac": "Music", ".ogg": "Music", ".m4a": "Music",
  
    ".py": "Code", ".js": "Code", ".ts": "Code", ".html": "Code",
    ".css": "Code", ".java": "Code", ".c": "Code", ".cpp": "Code",
    ".h": "Code", ".sh": "Code", ".json": "Code", ".xml": "Code",
    ".yaml": "Code", ".yml": "Code", ".md": "Code", ".sql": "Code",
  
    ".zip": "Archives", ".tar": "Archives", ".gz": "Archives",
    ".rar": "Archives", ".7z": "Archives",
}
DEFAULT_FOLDER = "Others"




def setup_logging(log_path: Path):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )



def categorize(file_path: Path) -> str:
    """Return the target folder name for a given file."""
    return CATEGORY_MAP.get(file_path.suffix.lower(), DEFAULT_FOLDER)


def unique_destination(dest: Path) -> Path:
    """If dest exists, append _1, _2, … until the name is free."""
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    counter = 1
    while True:
        candidate = dest.parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1



def organize(source_dir: Path, dry_run: bool = False):
    """
    Walk source_dir, categorize each file, and move it to the
    appropriate subfolder. Hidden files and subdirectories are skipped.
    """
    if not source_dir.is_dir():
        logging.error("Source directory does not exist: %s", source_dir)
        return

    log_path = source_dir / "organizer.log"
    setup_logging(log_path)

    mode_label = "[DRY RUN] " if dry_run else ""
    logging.info("%sOrganizing: %s", mode_label, source_dir)

    stats = defaultdict(int)   

    for item in source_dir.iterdir():
       
        if item.name.startswith(".") or item.name == "organizer.log":
            continue
        if item.is_dir():
            logging.info("SKIP (dir)   %s", item.name)
            continue

        folder_name  = categorize(item)
        target_dir   = source_dir / folder_name
        destination  = unique_destination(target_dir / item.name)

        if dry_run:
            logging.info("WOULD MOVE  %s  →  %s/%s",
                         item.name, folder_name, destination.name)
        else:
            target_dir.mkdir(exist_ok=True)
            shutil.move(str(item), str(destination))
            logging.info("MOVED       %s  →  %s/%s",
                         item.name, folder_name, destination.name)

        stats[folder_name] += 1

    total = sum(stats.values())
    print("\n" + "═" * 50)
    print(f"  {'SUMMARY':^46}")
    print("═" * 50)
    print(f"  {'Folder':<20}  {'Files':>6}")
    print("  " + "─" * 28)
    for folder, count in sorted(stats.items()):
        print(f"  {folder:<20}  {count:>6}")
    print("  " + "─" * 28)
    print(f"  {'TOTAL':<20}  {total:>6}")
    print("═" * 50)
    if dry_run:
        print("  (Dry run — no files were actually moved)")
    print()




def main():
    parser = argparse.ArgumentParser(
        description="Organize a directory by sorting files into typed subfolders."
    )
    parser.add_argument(
        "source",
        help="Path to the source directory to organize."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without moving any files."
    )
    args = parser.parse_args()
    organize(Path(args.source), dry_run=args.dry_run)


if __name__ == "__main__":
    main()
