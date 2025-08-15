from __future__ import annotations
from pathlib import Path
import logging
import math

def ensure_dirs():
    for d in [Path('logs'), Path('manifests'), Path('downloads'), Path('secrets')]:
        d.mkdir(parents=True, exist_ok=True)


def init_logging():
    from datetime import datetime
    log_path = Path('logs') / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger('gdrive_backup')
    logger.info(f"Logging to {log_path}")
    return logger


def human_size(num: int, suffix='B'):
    if num is None:
        return '0B'
    if num == 0:
        return '0B'
    units = ['','K','M','G','T','P']
    idx = int(math.floor(math.log(num, 1024)))
    p = math.pow(1024, idx)
    s = round(num / p, 2)
    return f"{s}{units[idx]}{suffix}"


def write_manifest_entry(path, entry: dict):
    with open(path, 'a', encoding='utf-8') as f:
        import json
        f.write(json.dumps(entry) + '\n')
