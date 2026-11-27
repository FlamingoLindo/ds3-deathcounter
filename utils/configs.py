"""_summary_
    """
import os
from pathlib import Path
from db.death_repository import DB


class Configs:
    def start_up():
        screenshots_dir = Path(os.getenv(
            "SCREENSHOTS_DIR", "screenshots"))
        dirs = [
            screenshots_dir,
            screenshots_dir / "masked",
            screenshots_dir / ".temp",
            screenshots_dir / "deaths",
        ]

        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)

        db_path = os.getenv("DB_PATH", "db.sqlite")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        db = DB(db_path)
        return db

    def image_exists(path):
        image = Path(path)
        if not image.is_file():
            raise FileNotFoundError(path)
        return str(image)
