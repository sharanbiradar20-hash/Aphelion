# 🛰️ Satellite Image Processing Web App

An interactive web application for experimenting with Digital Image Processing techniques based on **Gonzalez & Woods**.

An interactive web application for exploring Digital Image Processing through real satellite imagery, inspired by Gonzalez & Woods. Aphelion transforms traditionally abstract image-processing concepts into an intuitive, visual experience, allowing users to apply, visualize, and compare spatial, frequency-domain, restoration, and color-processing techniques in real time. With interactive filtering, histogram visualization, before-and-after comparisons, and quality metrics, the platform makes it easier to understand not only **what** an algorithm does, but **how and why** it changes an image.


![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-black?logo=flask&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📋 Table of Contents

- [Features](#-features)
- [Processing Modules](#-processing-modules)
- [Project Structure](#️-project-structure)
- [Tech Stack](#️-tech-stack)
- [Installation](#-installation)
- [Restarting the Project](#-restarting-the-project)
- [Requirements](#-requirements)
- [Academic Context](#-academic-context)
- [License](#-license)

---

## ✨ Features

| | |
|---|---|
| 📤 | Upload and process satellite images |
| 🔍 | Real-time filter application |
| 📊 | Histogram visualization |
| 🆚 | Before/after comparison slider |
| 📈 | Quality metrics display |
| 🎨 | Modern, animated React UI |

---

## 🧠 Processing Modules

### Module 2 — Intensity Transformations
- Linear, log, and power-law transforms
- Histogram equalization
- Spatial smoothing & sharpening
- Edge detection

### Module 3 — Frequency Domain
- Fourier Transform
- Low-pass / high-pass / band-pass filters
- Ideal, Gaussian, and Butterworth filters

### Module 4 — Image Restoration
- Noise modeling & reduction
- Deblurring & deconvolution
- Wiener filtering
- Morphological operations

### Module 5 — Color Processing
- RGB, HSV, Lab, and YCbCr conversions
- Color enhancement
- Color segmentation
- Color quantization

---

## 🏗️ Project Structure

```
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
```

---

## 🛠️ Tech Stack

**Backend**
- Python 3.11 ⚠️ *(mandatory)*
- Flask
- OpenCV
- NumPy
- SciPy
- Matplotlib
- Pillow

**Frontend**
- React 18
- Tailwind CSS
- Framer Motion
- Three.js
- Recharts
- Axios

---

## 🚀 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/satellite-image-processor.git
cd satellite-image-processor
```

### 2️⃣ Backend setup

```bash
cd backend
python -m venv venv
```

Activate the virtual environment:

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

Install dependencies and run the server:

```bash
pip install -r requirements.txt
python app.py
```

The backend runs at **http://localhost:5000**

### 3️⃣ Frontend setup

```bash
cd frontend
npm install
npm start
```

The frontend runs at **http://localhost:3000**

---

## 🔄 Restarting the Project

**Backend**

```bash
cd backend
venv\Scripts\activate
python app.py
```

**Frontend**

```bash
cd frontend
npm start
```

---

## 📌 Requirements

- Python 3.11 (required)
- Node.js 18+
- npm

---

## 📚 Academic Context

This project is inspired by:

> Gonzalez, R. C., & Woods, R. E. — *Digital Image Processing*

Designed for educational and experimental purposes.

---

This project is intended for educational use.
