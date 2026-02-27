# Satellite Image Processing Web Application

A comprehensive web application for digital image processing operations based on the "Digital Image Processing" textbook by Gonzalez & Woods. This academic project provides a platform for implementing and experimenting with various image processing algorithms.

## Project Structure

satellite-image-processor/
├── backend/
│   ├── app.py                 # Flask server
│   ├── requirements.txt       # Python dependencies
│   ├── processors/           # Image processing modules
│   │   ├── _init_.py
│   │   ├── module2_intensity.py
│   │   ├── module3_frequency.py
│   │   ├── module4_restoration.py
│   │   └── module5_color.py
│   ├── utils/                # Utility functions
│   │   ├── _init_.py
│   │   ├── metrics.py
│   │   └── visualization.py
│   └── uploads/              # Temporary file storage
└── frontend/
    ├── package.json          # Node.js dependencies
    ├── tailwind.config.js    # Tailwind CSS configuration
    ├── postcss.config.js     # PostCSS configuration
    └── src/
        ├── App.jsx           # Main React component
        ├── components/       # React components
        │   ├── ImageUploader.jsx
        │   ├── FilterControls.jsx
        │   ├── ComparisonSlider.jsx
        │   ├── HistogramDisplay.jsx
        │   └── MetricsPanel.jsx
        └── styles/
            └── App.css       # Custom styles with Tailwind

## Tech Stack

### Backend
- **Python 3.11** — Core programming language
- **Flask 3.0.0** — Web framework & REST API
- **Flask-CORS 4.0.0** — Cross-origin resource sharing
- **OpenCV 4.8.1.78** — Image I/O and processing operations
- **NumPy 1.24.3** — Array operations & matrix math
- **SciPy 1.11.4** — FFT operations and advanced algorithms
- **Matplotlib 3.8.2** — Spectrum visualization
- **Pillow 10.1.0** — Additional image format support
- **Werkzeug** — Secure file upload handling

### Frontend
- **React 18** (Create React App) — UI framework
- **JavaScript (JSX)** — Component logic
- **Tailwind CSS** — Utility-first CSS framework
- **Framer Motion** — Animations, transitions & AnimatePresence
- **Three.js** (`threejs-components` via CDN) — 3D neon tubes interactive background
- **Axios** — HTTP client for image uploads
- **Recharts** — Histogram & data visualization
- **Lucide React** — SVG icon library
- **Radix UI** (`@radix-ui/react-slot`) — Composable UI primitives
- **class-variance-authority** — Variant-based component styling
- **clsx + tailwind-merge** — Class name merging utility (`cn()`)

### Dev Tools
- **PostCSS + Autoprefixer** — CSS processing for Tailwind
- **npm** — Frontend package management
- **pip** — Backend package management

## Features

### Processing Modules

1. **Module 2: Intensity Transformations**
   - Point processing operations (linear, log, power transforms)
   - Histogram processing and equalization
   - Spatial filtering (smoothing, sharpening)
   - Edge detection algorithms

2. **Module 3: Frequency Domain**
   - Fourier Transform operations
   - Frequency domain filtering
   - Low-pass, high-pass, band-pass filters
   - Gaussian, Butterworth, and ideal filters

3. **Module 4: Image Restoration**
   - Noise modeling and reduction
   - Deblurring and deconvolution
   - Wiener filtering and constrained least squares
   - Morphological operations

4. **Module 5: Color Processing**
   - Color space conversions (RGB, HSV, Lab, YCbCr)
   - Color enhancement and correction
   - Color-based segmentation
   - Color quantization and transfer

## Installation

### Backend Setup

1. Navigate to the backend directory:
   bash
   cd satellite-image-processor/backend
   

2. Create a virtual environment:
   bash
   python -m venv venv
   

3. Activate the virtual environment:
   bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   

4. Install dependencies:
   bash
   pip install -r requirements.txt
   

5. Run the Flask server:
   bash
   python app.py
   

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   bash
   cd satellite-image-processor/frontend
   

2. Install dependencies:
   bash
   npm install
   

3. Start the development server:
   bash
   npm start
   ```

The frontend will be available at http://localhost:3000

# python 3.11 MANDATORY
# To restart the whole project, type
# Backend : 
cd backend 
venv\Scripts\activate
python app.py
# Frontend : 
cd frontend 
npm start

cd "C:\Users\SHARAN BIRADAR\Desktop\satellite-image-processor (1)\satellite-image-processor\frontend"
cd "C:\Users\SHARAN BIRADAR\Desktop\satellite-image-processor (1)\satellite-image-processor\backend"