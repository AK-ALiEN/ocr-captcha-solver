# OCR CAPTCHA Solver API

A lightweight Flask-based OCR CAPTCHA solver API built with **OpenCV** and **Tesseract OCR**.

This API can process CAPTCHA images from either:

- Image URLs
- Base64-encoded images

It extracts alphanumeric CAPTCHA text using image preprocessing and OCR techniques.



## Features

- Solve CAPTCHA images from remote URLs
- Solve CAPTCHA images from Base64 strings
- Image preprocessing using OpenCV
- OCR using Tesseract
- REST API endpoints
- Health check endpoint
- JSON responses
- Error handling and debugging support



## Tech Stack

- Python
- Flask
- OpenCV (`cv2`)
- Tesseract OCR (`pytesseract`)
- NumPy
- Requests



## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

#### Windows

Download and install Tesseract OCR:

https://github.com/UB-Mannheim/tesseract/wiki

Then update this line if needed:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

#### Linux

```bash
sudo apt install tesseract-ocr
```

#### macOS

```bash
brew install tesseract
```



## Running the API

```bash
python ocr_captcha_solver.py
```

Server will start on:

```txt
http://localhost:8080
```



# API Endpoints

## 1. Solve CAPTCHA (GET)

### Request

```http
GET /getcode?url=IMAGE_URL
```

### Example

```bash
curl "http://localhost:8080/getcode?url=https://example.com/captcha.jpg"
```

### Response

```json
{
  "success": true,
  "captcha_text": "AB12CD",
  "image_url": "https://example.com/captcha.jpg"
}
```



## 2. Solve CAPTCHA (POST with URL)

### Request

```http
POST /getcode
Content-Type: application/json
```

### Body

```json
{
  "url": "https://example.com/captcha.jpg"
}
```

### Example

```bash
curl -X POST http://localhost:8080/getcode \
-H "Content-Type: application/json" \
-d "{\"url\":\"https://example.com/captcha.jpg\"}"
```



## 3. Solve CAPTCHA (POST with Base64)

### Body

```json
{
  "base64": "BASE64_IMAGE_STRING"
}
```

### Example

```bash
curl -X POST http://localhost:8080/getcode \
-H "Content-Type: application/json" \
-d "{\"base64\":\"YOUR_BASE64_IMAGE\"}"
```

### Response

```json
{
  "success": true,
  "captcha_text": "X7P9K",
  "base64_provided": true
}
```



## Health Check

### Request

```http
GET /health
```

### Response

```json
{
  "status": "healthy",
  "service": "captcha-solver-api"
}
```



# How It Works

The script performs several preprocessing steps before OCR:

1. Convert image to grayscale
2. Apply Gaussian blur
3. Apply OTSU thresholding
4. Run Tesseract OCR with:
   - Page segmentation mode (`psm 7`)
   - Character whitelist for alphanumeric characters only



## OCR Configuration

```python
config = r"--oem 3 --psm 7 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
```

This improves recognition accuracy for common CAPTCHA formats.



## Example Project Structure

```txt
project/
│
├── ocr_captcha_solver.py
├── requirements.txt
└── README.md
```



## Suggested requirements.txt

```txt
flask
requests
opencv-python
pytesseract
numpy
```



## Notes

- Best suited for simple alphanumeric CAPTCHA images
- Complex distorted CAPTCHA systems may require additional preprocessing or ML models
- Ensure Tesseract OCR is correctly installed and accessible



## License

MIT License



## Disclaimer

This project is intended for educational and research purposes only.

Use responsibly and comply with the terms of service of any platform you interact with.
