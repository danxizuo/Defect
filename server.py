import hashlib
import json
import os
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from PIL import Image
import torch
from diffusers import StableDiffusionPipeline

MD5_MAP_PATH = os.environ.get('MD5_MAP_PATH', 'data/md5_map.json')
RESULT_DIR = Path(os.environ.get('RESULT_DIR', 'results'))
TMP_DIR = Path(os.environ.get('TMP_DIR', 'tmp'))

RESULT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

with open(MD5_MAP_PATH, 'r') as f:
    MD5_MAP: Dict[str, str] = json.load(f)

defect_prompts = {
    0: "photo of equipment with damage",
    1: "photo of equipment on fire",
    2: "photo of equipment leaking oil",
}

app = FastAPI()

device = 'cuda' if torch.cuda.is_available() else 'cpu'
pipe = StableDiffusionPipeline.from_pretrained(
    'runwayml/stable-diffusion-v1-5'
)
pipe.to(device)


def compute_md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


@app.post('/generate')
async def generate(defect_type: int, file: UploadFile = File(...)):
    if defect_type not in defect_prompts:
        raise HTTPException(status_code=400, detail='invalid defect type')

    content = await file.read()
    md5 = compute_md5_bytes(content)

    if md5 in MD5_MAP:
        return FileResponse(MD5_MAP[md5])

    tmp_path = TMP_DIR / file.filename
    with open(tmp_path, 'wb') as f:
        f.write(content)

    image = Image.open(tmp_path).convert('RGB')
    prompt = defect_prompts[defect_type]
    with torch.autocast(device):
        result = pipe(prompt, image).images[0]

    out_path = RESULT_DIR / f"{md5}.png"
    result.save(out_path)
    return FileResponse(out_path)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
