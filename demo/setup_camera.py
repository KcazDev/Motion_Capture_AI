"""Download the official lightweight pose model once; no camera access."""
from pathlib import Path
import urllib.request

MODEL = Path(__file__).resolve().parents[1] / 'models' / 'pose_landmarker_lite.task'
URL = 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task'

def main():
    if MODEL.is_file():
        print(f'Model already present: {MODEL}')
        return
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    temporary = MODEL.with_suffix('.download')
    try:
        urllib.request.urlretrieve(URL, temporary)
        temporary.replace(MODEL)
    finally:
        temporary.unlink(missing_ok=True)
    print(f'Model ready: {MODEL}')

if __name__ == '__main__':
    main()
