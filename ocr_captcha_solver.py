from flask import Flask, request, jsonify
import requests
import cv2
import pytesseract
import os
from io import BytesIO
import numpy as np
import traceback
import base64
import re

app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def download_image(image_url: str) -> np.ndarray:
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(image_url, headers=headers, timeout=10)
    response.raise_for_status()

    image_bytes = BytesIO(response.content)
    img_array = np.frombuffer(image_bytes.read(), np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Failed to decode image from URL")
    
    return img

def decode_base64_image(base64_string: str) -> np.ndarray:
    if ',' in base64_string:
        base64_string = base64_string.split(',', 1)[1]
    
    image_bytes = base64.b64decode(base64_string)
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Failed to decode base64 image")
    
    return img

def extract_text_from_image(img: np.ndarray) -> str:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config = r"--oem 3 --psm 7 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    text = pytesseract.image_to_string(th, config=config)

    return "".join(text.split()).strip()

@app.route('/getcode', methods=['GET', 'POST'])
def solve_captcha():
    try:
        image_url = None
        image_base64 = None
        
        if request.method == 'GET':
            image_url = request.args.get('url')
        
        elif request.method == 'POST':
            data = request.get_json()
            if data:
                image_url = data.get('url')
                image_base64 = data.get('base64') or data.get('image_base64')
        
        if not image_url and not image_base64:
            return jsonify({
                'success': False,
                'error': 'Missing image source. Use URL parameter for GET or provide "url" or "base64" in POST JSON body'
            }), 400
        
        if image_base64:
            print("Processing base64 image")
            img = decode_base64_image(image_base64)
            source_info = {'type': 'base64'}
        else:
            print(f"Processing image from URL: {image_url}")
            img = download_image(image_url)
            source_info = {'type': 'url', 'image_url': image_url}
        
        captcha_text = extract_text_from_image(img)
        
        if not captcha_text:
            response = {
                'success': False,
                'error': 'No text could be extracted from the image'
            }
            if image_url:
                response['image_url'] = image_url
            return jsonify(response), 400
        
        response = {
            'success': True,
            'captcha_text': captcha_text
        }
        
        if image_url:
            response['image_url'] = image_url
        if image_base64:
            response['base64_provided'] = True
        
        return jsonify(response)
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Failed to download image: {str(e)}',
            'image_url': image_url if 'image_url' in locals() else 'unknown'
        }), 400
        
    except Exception as e:
        print(f"Error processing captcha: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}',
            'image_url': image_url if 'image_url' in locals() else 'unknown'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'captcha-solver-api',
        'endpoints': {
            'solve_captcha': '/getcode?url=IMAGE_URL (GET) or POST JSON with {"url": "URL"} or {"base64": "BASE64_STRING"}',
            'health_check': '/health'
        }
    })

@app.route('/')
def index():
    return """
    <h1>Captcha Solver API</h1>
    <p>Usage:</p>
    <p><strong>GET:</strong> /getcode?url=IMAGE_URL</p>
    <p><strong>POST:</strong> /getcode with JSON body containing "url" or "base64"</p>
    <p>Examples:</p>
    <ul>
        <li><a href="/getcode?url=https://wapkiz.org/captcha_code.php?id=3074796619">GET example</a></li>
        <li>POST example with URL: {"url": "https://example.com/captcha.jpg"}</li>
        <li>POST example with base64: {"base64": "iVBORw0KGgoAAAANS..."}</li>
    </ul>
    <p>Health check: <a href="/health">/health</a></p>
    """

if __name__ == '__main__':
    os.makedirs('img', exist_ok=True)

    print("Starting Captcha Solver API...")
    print("API will be available at: http://localhost:8080")
    print("GET example: http://localhost:8080/getcode?url=IMAGE_URL")
    print("POST example with base64: curl -X POST http://localhost:8080/getcode -H 'Content-Type: application/json' -d '{\"base64\":\"YOUR_BASE64_IMAGE\"}'")
    app.run(host='0.0.0.0', port=8080, debug=True)
