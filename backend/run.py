import shutil
import subprocess
from pathlib import Path

import uvicorn

from app.config import settings

FRONTEND_DIR = Path(__file__).resolve().parents[1] / 'frontend'


def start_frontend():
    """Поднимает Vite рядом с бэкендом. Возвращает процесс либо None."""
    npm = shutil.which('npm')
    if npm is None:
        print('! npm не найден — фронт не запущен, работает только API на :8000')
        return None

    if not (FRONTEND_DIR / 'node_modules').is_dir():
        print('> npm install (первый запуск)')
        subprocess.run([npm, 'install'], cwd=FRONTEND_DIR, check=True)

    print('> Фронт: http://localhost:5173')
    return subprocess.Popen([npm, 'run', 'dev'], cwd=FRONTEND_DIR)


if __name__ == '__main__':
    # ponytail: в debug фронт крутится на Vite ради HMR и ходит в API через прокси.
    # В проде фронт не нужен отдельным процессом — main.py отдаёт собранный dist сам.
    frontend = start_frontend() if settings.debug else None
    try:
        uvicorn.run(
            'app.main:app',
            host='0.0.0.0',
            port=8000,
            reload=settings.debug,
            log_level='info',
        )
    finally:
        if frontend:
            frontend.terminate()
            frontend.wait()
