# Image Defect Generation Service

This repository provides an example of how to deploy a Stable Diffusion based
image defect generator on CentOS 7. The service exposes a simple HTTP API that
accepts an input image and a defect type (0, 1 or 2) and returns an image with
the requested defect applied. If the uploaded image matches one of the
pre-generated samples (checked via MD5), the server returns the pre-generated
result instead of creating a new image.

The repository contains:

- `requirements.txt` – Python package requirements.
- `server.py` – FastAPI service that runs the model and performs MD5 checking.
- `dataset_md5.py` – helper script to build a JSON mapping of MD5 hashes to
  existing defect images.
- `package_env.sh` – optional script showing how to download all required
  Python wheels for offline installation.

## 1. Preparing CentOS 7

1. Install system packages:
   ```bash
   sudo yum install -y epel-release
   sudo yum install -y git python3 python3-venv
   ```

2. (Optional) Install NVIDIA drivers and CUDA if GPU acceleration is needed.
   Refer to the official NVIDIA documentation for CentOS 7.

## 2. Create Python Environment

1. Clone this repository and enter it:
   ```bash
   git clone <repo-url>
   cd Defect
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

If running on a machine without internet access, execute `package_env.sh` on a
machine that does have internet. It will download all required wheels into
`wheels/`. Copy that directory to the target machine and install with
`pip install wheels/*`.

## 3. Prepare the MD5 Mapping

Use `dataset_md5.py` to create a JSON file containing MD5 hashes of the normal
images mapped to the corresponding defect images. Example:

```bash
python dataset_md5.py data/md5_map.json \
  --pairs "/path/to/设备破损/ref" "/path/to/设备破损/def" \
  --pairs "/path/to/设备烟火/ref" "/path/to/设备烟火/def" \
  --pairs "/path/to/渗漏油/ref" "/path/to/渗漏油/def"
```

The resulting `data/md5_map.json` will be loaded by `server.py` at runtime.

## 4. Running the API Service

Start the API with:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

Request format:

- **URL:** `/generate`
- **Method:** `POST`
- **Form fields:**
  - `defect_type` – integer `0`, `1` or `2`.
  - `file` – image file to process.

Example using `curl`:

```bash
curl -F defect_type=1 -F file=@input.jpg http://localhost:8000/generate --output result.png
```

The service will respond with the defect image. If the uploaded image matches an
entry in `md5_map.json`, the corresponding pre-generated image is returned.
Otherwise the model generates a new image using Stable Diffusion.

## 5. Packaging for Deployment on Multiple Servers

1. On a machine with internet access, run `package_env.sh`. This downloads all
   Python wheels specified in `requirements.txt` into the `wheels/` directory.
2. Copy the repository and the `wheels/` directory to the target server.
3. Create a virtual environment and install the wheels:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install wheels/*
   ```
4. Copy or recreate the `data/md5_map.json` file on each server.
5. Start the API as shown above.

With this approach you can replicate the same environment on multiple CentOS 7
servers without re-downloading packages from the internet.
