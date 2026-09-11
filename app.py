import os
import base64
import sys
import argparse
from io import BytesIO
from pathlib import Path

import requests
from flask import Flask, request, render_template_string

API_KEY = "API_KEY_REMOVEBG"
API_URL = "https://api.remove.bg/v1.0/removebg"

def remove_bg(file_path=None, image_url=None, size="auto"):
    data = {"size": size}
    files = {}
    if file_path:
        files["image_file"] = open(file_path, "rb")
    elif image_url:
        data["image_url"] = image_url
    else:
        raise ValueError("Provide either file_path or image_url")
    headers = {"X-Api-Key": API_KEY}
    try:
        resp = requests.post(API_URL, data=data, files=files, headers=headers)
        resp.raise_for_status()
        return resp.content
    except requests.exceptions.HTTPError:
        return None
    finally:
        if files:
            files["image_file"].close()

app = Flask(__name__)

HTML_FORM = """
<!doctype html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <title>Remove Background</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }
    
    body {
      background-color: #f8fafc;
      color: #334155;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px;
    }
    
    .container {
      width: 100%;
      max-width: 720px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    .card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
      padding: 36px 32px;
      text-align: center;
    }

    h1 {
      font-size: 1.75rem;
      color: #0f172a;
      font-weight: 600;
      margin-bottom: 8px;
    }

    p.subtitle {
      color: #64748b;
      font-size: 0.95rem;
      margin-bottom: 24px;
    }
    
    .dropzone {
      border: 2px dashed #cbd5e1;
      border-radius: 12px;
      padding: 36px 20px;
      background: #f1f5f9;
      transition: border-color 0.2s, background-color 0.2s;
      cursor: pointer;
      position: relative;
    }

    .dropzone:hover {
      border-color: #2563eb;
      background: #eff6ff;
    }

    .dropzone input[type="file"] {
      position: absolute;
      top: 0; left: 0;
      width: 100%; height: 100%;
      opacity: 0;
      cursor: pointer;
    }

    .dropzone-icon {
      width: 40px;
      height: 40px;
      margin: 0 auto 12px;
      fill: #2563eb;
    }

    .dropzone-text {
      font-size: 0.9rem;
      color: #64748b;
    }

    #file-name {
      margin-top: 10px;
      font-size: 0.85rem;
      color: #2563eb;
    }
    
    .btn-group {
      display: flex;
      gap: 12px;
      justify-content: center;
      margin-top: 20px;
    }

    .btn {
      background: #2563eb;
      color: #ffffff;
      border: none;
      padding: 10px 24px;
      font-size: 0.95rem;
      border-radius: 8px;
      cursor: pointer;
      transition: background-color 0.2s;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
    }

    .btn:hover {
      background: #1d4ed8;
    }

    .btn-secondary {
      background: #ffffff;
      color: #334155;
      border: 1px solid #cbd5e1;
    }

    .btn-secondary:hover {
      background: #f1f5f9;
    }
    
    .result-container {
      margin-top: 28px;
      padding-top: 20px;
      border-top: 1px solid #e2e8f0;
    }

    .result-title {
      font-size: 0.95rem;
      color: #475569;
      margin-bottom: 16px;
    }

    .img-wrapper {
      background-color: #ffffff;
      background-image: 
        linear-gradient(45deg, #e2e8f0 25%, transparent 25%), 
        linear-gradient(-45deg, #e2e8f0 25%, transparent 25%), 
        linear-gradient(45deg, transparent 75%, #e2e8f0 75%), 
        linear-gradient(-45deg, transparent 75%, #e2e8f0 75%);
      background-size: 16px 16px;
      background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
      border-radius: 8px;
      border: 1px solid #e2e8f0;
      display: inline-block;
      overflow: hidden;
      padding: 6px;
      max-width: 100%;
    }

    .img-wrapper img {
      max-width: 100%;
      max-height: 350px;
      display: block;
      border-radius: 4px;
    }

    /* Skeleton Cards Section */
    .skeleton-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      width: 100%;
    }

    .skeleton-card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .skeleton-avatar {
      width: 32px;
      height: 32px;
      border-radius: 6px;
      background: #e2e8f0;
    }

    .skeleton-line {
      height: 12px;
      border-radius: 4px;
      background: #e2e8f0;
    }

    .skeleton-line.title {
      width: 60%;
    }

    .skeleton-line.body-1 {
      width: 90%;
    }

    .skeleton-line.body-2 {
      width: 75%;
    }
  </style>
</head>
<body>
  <div class='container'>
    <div class='card'>
      <h1>Remove Image Background</h1>
      <p class='subtitle'>Upload gambar untuk menghapus latar belakang secara otomatis</p>
      
      <form method='post' enctype='multipart/form-data'>
        <div class='dropzone'>
          <div class='dropzone-text'>Drag and drop gambar di sini, atau klik untuk memilih file</div>
          <input type='file' name='image' accept='image/*' required onchange="document.getElementById('file-name').innerText = this.files[0].name">
        </div>
        <div id="file-name"></div>
        
        <div class="btn-group">
          <button type='submit' class='btn'>Upload Gambar</button>
        </div>
      </form>
      
      {% if result_img %}
        <div class='result-container'>
          <div class='result-title'>Hasil Pemotongan</div>
          <div class='img-wrapper'>
            <img src='data:image/png;base64,{{ result_img }}' alt='Result'>
          </div>
          <div class="btn-group">
            <a href="data:image/png;base64,{{ result_img }}" download="no-bg.png" class="btn btn-secondary">Download PNG</a>
          </div>
        </div>
      {% endif %}
    </div>

    <!-- Skeleton Loader Cards -->
    <div class="skeleton-grid">
      <div class="skeleton-card">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-line title"></div>
        <div class="skeleton-line body-1"></div>
        <div class="skeleton-line body-2"></div>
      </div>
      <div class="skeleton-card">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-line title"></div>
        <div class="skeleton-line body-1"></div>
        <div class="skeleton-line body-2"></div>
      </div>
      <div class="skeleton-card">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-line title"></div>
        <div class="skeleton-line body-1"></div>
        <div class="skeleton-line body-2"></div>
      </div>
    </div>
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        img = request.files["image"]
        if img:
            out = remove_bg(file_path=save_temp(img))
            if out is None:
                error_html = """<script>alert('Gagal menghapus background. Periksa kembali file gambar atau API Key.');</script>"""
                return render_template_string(error_html + HTML_FORM, result_img=None)
            b64 = base64.b64encode(out).decode('utf-8')
            return render_template_string(HTML_FORM, result_img=b64)
    return render_template_string(HTML_FORM, result_img=None)

def save_temp(upload):
    tmp = Path("tmp")
    tmp.mkdir(exist_ok=True)
    path = tmp / upload.filename
    upload.save(path)
    return str(path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove bg CLI")
    parser.add_argument("--file", help="Path to local image")
    parser.add_argument("--url", help="Public image URL")
    parser.add_argument("--size", default="auto", help="Output size")
    parser.add_argument("--out", default="output.png", help="Result path")
    parser.add_argument("--serve", action="store_true", help="Run web UI")
    args = parser.parse_args()

    if args.serve:
        app.run(debug=True)
    else:
        result = remove_bg(file_path=args.file, image_url=args.url, size=args.size)
        if result:
            Path(args.out).write_bytes(result)
            print(f"Saved result to {args.out}")
        else:
            print("Gagal mengambil gambar dari API.")