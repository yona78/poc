from __future__ import annotations

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from services.video_metadata_service.app import app


def main() -> None:
    """Generate OpenAPI schema for the video metadata service."""
    schema = app.openapi()
    docs_dir = BASE_DIR / "docs"
    docs_dir.mkdir(exist_ok=True)
    out_file = docs_dir / "openapi.json"
    out_file.write_text(json.dumps(schema, indent=2))
    print(f"OpenAPI schema written to {out_file}")


if __name__ == "__main__":
    main()
