🛰️ Satellite Image Processing Web App

An interactive web application for experimenting with Digital Image Processing techniques based on Gonzalez & Woods.

This project provides a modular platform to apply, visualize, and compare spatial, frequency-domain, restoration, and color processing algorithms on satellite imagery.

✨ Features

📤 Upload and process satellite images

🔍 Real-time filter application

📊 Histogram visualization

🆚 Before/after comparison slider

📈 Quality metrics display

🎨 Modern animated React UI

🧠 Processing Modules
Module 2 — Intensity Transformations

Linear, Log, and Power-law transforms

Histogram equalization

Spatial smoothing & sharpening

Edge detection

Module 3 — Frequency Domain

Fourier Transform

Low-pass / High-pass / Band-pass filters

Ideal, Gaussian, Butterworth filters

Module 4 — Image Restoration

Noise modeling & reduction

Deblurring & deconvolution

Wiener filtering

Morphological operations

Module 5 — Color Processing

RGB, HSV, Lab, YCbCr conversions

Color enhancement

Color segmentation

Color quantization

🏗️ Project Structure
satellite-image-processor/
│
├── backend/
│   ├── app.py
│   ├── processors/
│   ├── utils/
│   └── uploads/
│
└── frontend/
    ├── src/
    └── components/
🛠️ Tech Stack
Backend

Python 3.11 ⚠️ (MANDATORY)

Flask

OpenCV

NumPy

SciPy

Matplotlib

Pillow

Frontend

React 18

Tailwind CSS

Framer Motion

Three.js

Recharts

Axios

🚀 Installation
1️⃣ Clone Repository
git clone https://github.com/your-username/satellite-image-processor.git
cd satellite-image-processor
2️⃣ Backend Setup
cd backend
python -m venv venv

Activate environment:

Windows

venv\Scripts\activate

macOS/Linux

source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Run server:

python app.py

Backend runs at:

http://localhost:5000
3️⃣ Frontend Setup
cd frontend
npm install
npm start

Frontend runs at:

http://localhost:3000
🔄 Restarting the Project
Backend
cd backend
venv\Scripts\activate
python app.py
Frontend
cd frontend
npm start
📌 Requirements

Python 3.11 required

Node.js 18+

npm

📚 Academic Context

This project is inspired by:

Gonzalez, R. C., & Woods, R. E. — Digital Image Processing

Designed for educational and experimental purposes.
