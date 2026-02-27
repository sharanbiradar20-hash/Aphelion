"""
Satellite Image Processing Web Application
Flask backend server for digital image processing operations
Based on "Digital Image Processing" by Gonzalez & Woods

Comprehensive REST API with all processing modules and utilities.
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import cv2
import numpy as np
import base64
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from io import BytesIO
import uuid
from typing import Dict

# Getting image properties
def get_image_properties(image_path: str) -> Dict:
    """
    Extract comprehensive image properties and metadata.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        dict with keys: 'width', 'height', 'channels', 'dtype', 'size_bytes', 
                       'color_space', 'file_size', 'aspect_ratio', 'pixel_count'
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image cannot be loaded
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image from: {image_path}")
        
        # Get file size
        file_size = os.path.getsize(image_path)
        
        # Extract properties
        height, width = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1
        
        # Determine color space
        if channels == 1:
            color_space = "Grayscale"
        elif channels == 3:
            color_space = "BGR"  # OpenCV default
        elif channels == 4:
            color_space = "BGRA"
        else:
            color_space = f"{channels}-channel"
        
        # Calculate memory size
        size_bytes = image.nbytes
        
        # Calculate aspect ratio
        aspect_ratio = width / height
        
        # Calculate total pixels
        pixel_count = width * height
        
        return {
            'success': True,
            'width': int(width),
            'height': int(height),
            'channels': int(channels),
            'dtype': str(image.dtype),
            'size_bytes': int(size_bytes),
            'color_space': color_space,
            'file_size': int(file_size),
            'aspect_ratio': float(aspect_ratio),
            'pixel_count': int(pixel_count),
            'min_value': int(image.min()),
            'max_value': int(image.max()),
            'mean_value': float(image.mean())
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Import processing modules
from processors.module2_intensity import (
    image_negative, log_transform, power_law_transform, piecewise_linear_transform,
    histogram_equalization, histogram_specification, spatial_smoothing, spatial_sharpening
)
from processors.module3_frequency import (
    compute_dft_2d, ideal_lowpass_filter, ideal_highpass_filter,
    butterworth_lowpass_filter, butterworth_highpass_filter,
    gaussian_lowpass_filter, gaussian_highpass_filter, visualize_frequency_domain
)
from processors.module4_restoration import (
    add_noise, periodic_noise_removal, inverse_filtering, wiener_filtering,
    constrained_least_squares_filtering, motion_blur_kernel, atmospheric_turbulence_degradation
)
from processors.module5_color import (
    rgb_to_hsi, hsi_to_rgb, intensity_slicing, false_color_composite,
    process_rgb_channels, color_image_smoothing, color_image_sharpening,
    pseudocolor_processing
    #   calculate_ndvi, multispectral_band_selection
)

# Import utilities
from utils.metrics import (
    calculate_psnr, calculate_mse, calculate_ssim, calculate_snr,
    sharpness_index, contrast_measure, entropy_measure, edge_strength,
    calculate_image_metrics, calculate_histogram_features, calculate_texture_features
)
from utils.visualization import (
    plot_histogram, plot_frequency_spectrum, plot_comparison_grid,
    create_metrics_report, create_histogram, create_color_histogram
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
VISUALIZATIONS_FOLDER = 'visualizations'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'tif'} ################################ add more 

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VISUALIZATIONS_FOLDER'] = VISUALIZATIONS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VISUALIZATIONS_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File management
file_registry = {}  # Store file metadata and cleanup times
cleanup_interval = 3600  # 1 hour in seconds


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def image_to_base64(image):
    """Convert numpy image array to base64 string"""
    try:
        if len(image.shape) == 3:
            # Color image
            _, buffer = cv2.imencode('.png', image)
        else:
            # Grayscale image
            _, buffer = cv2.imencode('.png', image)
        
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return image_base64
    except Exception as e:
        logger.error(f"Error converting image to base64: {str(e)}")
        return None


def base64_to_image(base64_string):
    """Convert base64 string to numpy image array"""
    try:
        image_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        logger.error(f"Error converting base64 to image: {str(e)}")
        return None


def cleanup_old_files():
    """Clean up files older than 1 hour"""
    current_time = time.time()
    files_to_remove = []
    
    for file_id, metadata in file_registry.items():
        if current_time - metadata['upload_time'] > cleanup_interval:
            files_to_remove.append(file_id)
    
    for file_id in files_to_remove:
        try:
            filepath = file_registry[file_id]['filepath']
            if os.path.exists(filepath):
                os.remove(filepath)
            del file_registry[file_id]
            logger.info(f"Cleaned up file: {file_id}")
        except Exception as e:
            logger.error(f"Error cleaning up file {file_id}: {str(e)}")


def start_cleanup_thread():
    """Start background thread for file cleanup"""
    def cleanup_worker():
        while True:
            time.sleep(300)  # Check every 5 minutes
            cleanup_old_files()
    
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()


# Start cleanup thread
start_cleanup_thread()


@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Satellite Image Processing API is running',
        'version': '1.0.0',
        'modules': ['fundamentals', 'intensity', 'frequency', 'restoration', 'color'],
        'active_files': len(file_registry)
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle image file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        
        # Save file
        file.save(filepath)
        
        # Read image and get properties
        img = cv2.imread(filepath)
        if img is None:
            return jsonify({'error': 'Invalid image file'}), 400
        
        # Get image properties
        properties = get_image_properties(filepath)
        
        # Register file
        file_registry[file_id] = {
            'filename': filename,
            'filepath': filepath,
            'upload_time': time.time(),
            'properties': properties
        }
        
        logger.info(f"File uploaded: {file_id} - {filename}")
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': filename,
            'image_properties': properties
        })
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# @app.route('/api/process/module1', methods=['POST'])
# def process_module1():
#     """Process images using Module 1: Image Fundamentals"""
#     try:
#         data = request.get_json()
#         file_id = data.get('file_id')
#         operation = data.get('operation')
#         parameters = data.get('parameters', {})
        
#         if not file_id or not operation:
#             return jsonify({'error': 'file_id and operation required'}), 400
        
#         if file_id not in file_registry:
#             return jsonify({'error': 'File not found'}), 404
        
#         # Load image
#         filepath = file_registry[file_id]['filepath']
#         image = cv2.imread(filepath)
        
#         if image is None:
#             return jsonify({'error': 'Could not load image'}), 400
        
#         result = None
        
#         if operation == 'resample':
#             scale_factor = parameters.get('scale_factor', 1.0)
#             method = parameters.get('method', 'bilinear')
#             result = resample_image(image, scale_factor, method)
            
#         elif operation == 'quantize':
#             bits = parameters.get('bits_per_channel', 4)
#             result = quantize_image(image, bits)
            
#         elif operation == 'analyze_properties':
#             result = get_image_properties(filepath)
            
#         elif operation == 'analyze_connectivity':
#             x = parameters.get('x', 0)
#             y = parameters.get('y', 0)
#             result = analyze_pixel_connectivity(image, x, y)
            
#         else:
#             return jsonify({'error': f'Invalid operation: {operation}'}), 400
        
#         if result and result.get('success'):
#             # Convert processed image to base64 if available
#             processed_image_b64 = None
#             if 'processed_image' in result:
#                 processed_image_b64 = image_to_base64(result['processed_image'])
            
#             response_data = {
#                 'success': True,
#                 'operation': operation,
#                 'parameters': parameters,
#                 'processed_image': processed_image_b64,
#                 'original_histogram': result.get('original_histogram', []),
#                 'processed_histogram': result.get('processed_histogram', []),
#                 'statistics': result.get('statistics', {})
#             }
            
#             return jsonify(response_data)
#         else:
#             return jsonify({'error': result.get('error', 'Processing failed')}), 500
            
#     except Exception as e:
#         logger.error(f"Module1 processing error: {str(e)}")
#         return jsonify({'error': str(e)}), 500


@app.route('/api/process/module2', methods=['POST'])
def process_module2():
    """Process images using Module 2: Intensity Transformations"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        operation = data.get('operation')
        parameters = data.get('parameters', {})
        
        if not file_id or not operation:
            return jsonify({'error': 'file_id and operation required'}), 400
        
        if file_id not in file_registry:
            return jsonify({'error': 'File not found'}), 404
        
        # Load image
        filepath = file_registry[file_id]['filepath']
        image = cv2.imread(filepath)
        
        if image is None:
            return jsonify({'error': 'Could not load image'}), 400
        
        result = None
        
        if operation == 'negative':
            result = image_negative(image)
            
        elif operation == 'log':
            c = parameters.get('c', 1.0)
            result = log_transform(image, c)
            
        elif operation == 'power_law':
            gamma = parameters.get('gamma', -1.0)######################## already fixed gamma from 1(no change) to -1.0 (making dark areas bright)
            c = parameters.get('c', -1.0)
            result = power_law_transform(image, gamma, c)
            
        elif operation == 'histogram_eq':
            result = histogram_equalization(image)
            
        elif operation == 'sharpen':
            method = parameters.get('method', 'laplacian')
            k = parameters.get('k', 1.0)
            result = spatial_sharpening(image, method, k)
            
        elif operation == 'smooth':
            kernel_size = parameters.get('kernel_size', 5)
            method = parameters.get('method', 'gaussian')
            result = spatial_smoothing(image, kernel_size, method)
            
        elif operation == 'piecewise_linear':
            points = parameters.get('points', [(0, 0), (30, 5), (80, 20), (130, 210), (255, 255)])
            # points = parameters.get('points', [(0, 0), (255, 255)])
            result = piecewise_linear_transform(image, points)
            
        else:
            return jsonify({'error': f'Invalid operation: {operation}'}), 400
        
        if result and result.get('success'):
            # Convert processed image to base64
            processed_image_b64 = image_to_base64(result['processed_image'])
            
            response_data = {
                'success': True,
                'operation': operation,
                'parameters': parameters,
                'processed_image': processed_image_b64,
                'original_histogram': result.get('original_histogram', []),
                'processed_histogram': result.get('processed_histogram', []),
                'statistics': result.get('statistics', {}),
                'transformation': result.get('transformation', ''),
                'formula': result.get('formula', '')
            }
            
            return jsonify(response_data)
        else:
            return jsonify({'error': result.get('error', 'Processing failed')}), 500
            
    except Exception as e:
        logger.error(f"Module2 processing error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/process/module3', methods=['POST'])
def process_module3():
    """Process images using Module 3: Frequency Domain Filtering"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        operation = data.get('operation')
        parameters = data.get('parameters', {})
        
        if not file_id or not operation:
            return jsonify({'error': 'file_id and operation required'}), 400
        
        if file_id not in file_registry:
            return jsonify({'error': 'File not found'}), 404
        
        # Load image
        filepath = file_registry[file_id]['filepath']
        image = cv2.imread(filepath)
        
        if image is None:
            return jsonify({'error': 'Could not load image'}), 400
        
        result = None
        
        if operation == 'ideal_lp':
            cutoff = parameters.get('cutoff_frequency', 30)
            result = ideal_lowpass_filter(image, cutoff)
            
        elif operation == 'ideal_hp':
            cutoff = parameters.get('cutoff_frequency', 60)
            result = ideal_highpass_filter(image, cutoff)
            
        elif operation == 'butterworth_lp':
            cutoff = parameters.get('cutoff_frequency', 50)
            order = parameters.get('order', 1)
            result = butterworth_lowpass_filter(image, cutoff, order)
            
        elif operation == 'butterworth_hp':
            cutoff = parameters.get('cutoff_frequency', 50)
            order = parameters.get('order', 1)
            result = butterworth_highpass_filter(image, cutoff, order)
            
        elif operation == 'gaussian_lp':
            cutoff = parameters.get('cutoff_frequency', 30)
            result = gaussian_lowpass_filter(image, cutoff)
            
        elif operation == 'gaussian_hp':
            cutoff = parameters.get('cutoff_frequency', 20)
            result = gaussian_highpass_filter(image, cutoff)
            
        elif operation == 'compute_dft':
            result = compute_dft_2d(image)
            
        else:
            return jsonify({'error': f'Invalid operation: {operation}'}), 400
        
        if result and result.get('success'):
            # Convert processed image to base64
            # processed_image_b64 = image_to_base64(result['filtered_image'])######################
            if operation == 'compute_dft':
                # For DFT, return the magnitude spectrum as the processed image
                mag_normalized = cv2.normalize(result['magnitude_spectrum'], None, 0, 255, cv2.NORM_MINMAX)
                processed_image_b64 = image_to_base64(mag_normalized.astype(np.uint8))
            else:
                # For filtering operations, return the filtered image
                processed_image_b64 = image_to_base64(result['filtered_image'])
            
            # Create frequency domain visualization
            visualization_path = None
            if 'F_shifted' in result:
                viz_result = visualize_frequency_domain(
                    result['F_shifted'], 
                    result.get('filter_mask'),
                    f"Frequency Analysis - {operation}"
                )
                if viz_result.get('success'):
                    visualization_path = viz_result['visualization_path']
            
            response_data = {
                'success': True,
                'operation': operation,
                'parameters': parameters,
                'processed_image': processed_image_b64,
                'visualization_path': visualization_path,
                'statistics': result.get('statistics', {})
            }
            
            return jsonify(response_data)
        else:











            
            return jsonify({'error': result.get('error', 'Processing failed')}), 500
            
    except Exception as e:
        logger.error(f"Module3 processing error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/process/module4', methods=['POST'])
def process_module4():
    """Process images using Module 4: Image Restoration"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        operation = data.get('operation')
        parameters = data.get('parameters', {})
        
        if not file_id or not operation:
            return jsonify({'error': 'file_id and operation required'}), 400
        
        if file_id not in file_registry:
            return jsonify({'error': 'File not found'}), 404
        
        # Load image
        filepath = file_registry[file_id]['filepath']
        image = cv2.imread(filepath)
        
        if image is None:
            return jsonify({'error': 'Could not load image'}), 400
        
        result = None
        
        if operation == 'add_noise':
            noise_type = parameters.get('noise_type', 'gaussian')
            noise_params = parameters.get('noise_params', {})
            result = add_noise(image, noise_type, noise_params)
            
        # elif operation == 'inverse_filter':
        #     kernel_size = parameters.get('kernel_size', 5)
        #     epsilon = parameters.get('epsilon', 1e-10)
        #     kernel = motion_blur_kernel(kernel_size, 0)
        #     result = inverse_filtering(image, kernel, epsilon)
            
        # elif operation == 'wiener_filter':
        #     kernel_size = parameters.get('kernel_size', 5)
        #     noise_variance = parameters.get('noise_variance', 0.01)
        #     kernel = motion_blur_kernel(kernel_size, 0)
        #     result = wiener_filtering(image, kernel, noise_variance)
        
        elif operation == 'inverse_filter':
            psf_size = parameters.get('psf_size', 5)
            epsilon = parameters.get('epsilon', 0.001)
            kernel = motion_blur_kernel(psf_size, 0)
            result = inverse_filtering(image, kernel, epsilon)
            
        elif operation == 'wiener_filter':
            psf_size = parameters.get('psf_size', 5)
            K = parameters.get('K', 0.01)
            kernel = motion_blur_kernel(psf_size, 0)
            result = wiener_filtering(image, kernel, K)
            
        elif operation == 'cls_filter':
            kernel_size = parameters.get('kernel_size', 5)
            gamma = parameters.get('gamma', 0.1)
            kernel = motion_blur_kernel(kernel_size, 0)
            result = constrained_least_squares_filtering(image, kernel, gamma)
            
        elif operation == 'periodic_noise_removal':
            frequencies = parameters.get('frequencies', [(10, 10)])
            result = periodic_noise_removal(image, frequencies)
            
        else:
            return jsonify({'error': f'Invalid operation: {operation}'}), 400
        
        if result and result.get('success'):
            # Convert images to base64
            degraded_image_b64 = None
            restored_image_b64 = None
            
            if 'noisy_image' in result:
                degraded_image_b64 = image_to_base64(result['noisy_image'])
            if 'restored_image' in result:
                restored_image_b64 = image_to_base64(result['restored_image'])
            
            # Calculate metrics
            metrics = {}
            if 'noisy_image' in result and 'original_image' in result:
                metrics['snr'] = calculate_snr(result['original_image'], 
                                            result['noisy_image'] - result['original_image'])
            
            if 'restored_image' in result and 'original_image' in result:
                metrics['psnr'] = calculate_psnr(result['original_image'], result['restored_image'])
                metrics['mse'] = calculate_mse(result['original_image'], result['restored_image'])
                metrics['ssim'] = calculate_ssim(result['original_image'], result['restored_image'])
            
            # Use restored_image or noisy_image as processed_image
            processed_image_b64 = restored_image_b64 or degraded_image_b64
            
            response_data = {
                'success': True,
                'operation': operation,
                'parameters': parameters,
                'processed_image': processed_image_b64,
                'statistics': metrics
            }
            
            return jsonify(response_data)
        else:
            return jsonify({'error': result.get('error', 'Processing failed')}), 500
        
    except Exception as e:
        logger.error(f"Module4 processing error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/process/module5', methods=['POST'])
def process_module5():
    """Process images using Module 5: Color Image Processing"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        operation = data.get('operation')
        parameters = data.get('parameters', {})
        
        if not file_id or not operation:
            return jsonify({'error': 'file_id and operation required'}), 400
        
        if file_id not in file_registry:
            return jsonify({'error': 'File not found'}), 404
        
        # Load image
        filepath = file_registry[file_id]['filepath']
        image = cv2.imread(filepath)
        
        if image is None:
            return jsonify({'error': 'Could not load image'}), 400
        
        result = None
        
        if operation == 'false_color':
            colormap = parameters.get('colormap', 'jet')
            result = false_color_composite(image, colormap)
            
        elif operation == 'rgb_enhance':
            enhance_op = parameters.get('enhance_operation', 'equalize')
            params = parameters.get('params', {})
            result = process_rgb_channels(image, enhance_op, **params)
            
        elif operation == 'hsi_process':
            process_type = parameters.get('process_type', 'smooth')
            if process_type == 'smooth':
                method = parameters.get('method', 'hsi')
                result = color_image_smoothing(image, method)
            elif process_type == 'sharpen':
                method = parameters.get('method', 'hsi')
                result = color_image_sharpening(image, method)
            elif process_type == 'convert':
                result = rgb_to_hsi(image)
            
        elif operation == 'pseudocolor':
            scheme = parameters.get('scheme', 'density')
            result = pseudocolor_processing(image, scheme)
            
        elif operation == 'intensity_slicing':
            levels = parameters.get('levels', 8)
            result = intensity_slicing(image, levels)
            
        # elif operation == 'ndvi':
        #     nir_band = parameters.get('nir_band')
        #     red_band = parameters.get('red_band')
        #     if nir_band is None or red_band is None:
        #         return jsonify({'error': 'NIR and Red bands required for NDVI'}), 400
        #     result = calculate_ndvi(nir_band, red_band)
            
        else:
            return jsonify({'error': f'Invalid operation: {operation}'}), 400
        
        if result and result.get('success'):
            # Convert processed image to base64
            processed_image_b64 = image_to_base64(result['processed_image'])
            if isinstance(result['processed_image'], np.ndarray):
                result['processed_image'] = image_to_base64(result['processed_image'])

            # #DEBUG
            # print("✅ Base64 conversion done. Length:", len(processed_image_b64) if processed_image_b64 else "None")

            # Extract channel information
            channel_info = {}
            if 'channels' in result:
                channel_info = result['channels']
            
            response_data = {
                'success': True,
                'operation': operation,
                'parameters': parameters,
                'processed_image': processed_image_b64,
                'statistics': result.get('statistics', {})
            }
            
            return jsonify(response_data)
        else:
            return jsonify({'error': result.get('error', 'Processing failed')}), 500
            
    except Exception as e:
        logger.error(f"Module5 processing error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics/<file_id>')
def get_metrics(file_id):
    """Calculate all quality metrics for an image"""
    try:
        if file_id not in file_registry:
            return jsonify({'error': 'File not found'}), 404
        
        # Load image
        filepath = file_registry[file_id]['filepath']
        image = cv2.imread(filepath)
        
        if image is None:
            return jsonify({'error': 'Could not load image'}), 400
        
        # Calculate comprehensive metrics
        metrics_data = calculate_image_metrics(image)
        histogram_features = calculate_histogram_features(image)
        texture_features = calculate_texture_features(image)
        
        # Calculate additional metrics
        sharpness = sharpness_index(image)
        contrast = contrast_measure(image)
        entropy = entropy_measure(image)
        edge_strength_val = edge_strength(image)
        
        response_data = {
            'success': True,
            'file_id': file_id,
            'metrics': {
                'psnr': None,  # Requires comparison image
                'mse': None,   # Requires comparison image
                'ssim': None,  # Requires comparison image
                'snr': None,   # Requires noise component
                'sharpness': sharpness,
                'contrast': contrast,
                'entropy': entropy,
                'edge_strength': edge_strength_val
            },
            'image_statistics': metrics_data,
            'histogram_features': histogram_features,
            'texture_features': texture_features
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Metrics calculation error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare', methods=['POST'])
def compare_images():
    """Compare two images and calculate comparative metrics"""
    try:
        data = request.get_json()
        original_id = data.get('original_id')
        processed_id = data.get('processed_id')
        
        if not original_id or not processed_id:
            return jsonify({'error': 'original_id and processed_id required'}), 400
        
        if original_id not in file_registry or processed_id not in file_registry:
            return jsonify({'error': 'One or both files not found'}), 404
        
        # Load images
        original_path = file_registry[original_id]['filepath']
        processed_path = file_registry[processed_id]['filepath']
        
        original_image = cv2.imread(original_path)
        processed_image = cv2.imread(processed_path)
        
        if original_image is None or processed_image is None:
            return jsonify({'error': 'Could not load images'}), 400
        
        # Calculate comparative metrics
        psnr = calculate_psnr(original_image, processed_image)
        mse = calculate_mse(original_image, processed_image)
        ssim = calculate_ssim(original_image, processed_image)
        
        # Calculate individual metrics
        original_metrics = calculate_image_metrics(original_image)
        processed_metrics = calculate_image_metrics(processed_image)
        
        # Calculate histograms
        original_hist = create_histogram(original_image)
        processed_hist = create_histogram(processed_image)
        
        # Generate comparison visualization
        comparison_path = plot_comparison_grid(
            [original_image, processed_image],
            ['Original Image', 'Processed Image'],
            rows=1, cols=2
        )
        
        response_data = {
            'success': True,
            'original_id': original_id,
            'processed_id': processed_id,
            'comparative_metrics': {
                'psnr': psnr,
                'mse': mse,
                'ssim': ssim
            },
            'original_metrics': original_metrics,
            'processed_metrics': processed_metrics,
            'original_histogram': original_hist,
            'processed_histogram': processed_hist,
            'comparison_visualization': comparison_path
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Image comparison error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/visualizations/<filename>')
def serve_visualization(filename):
    """Serve visualization images"""
    try:
        return send_from_directory(app.config['VISUALIZATIONS_FOLDER'], filename)
    except Exception as e:
        logger.error(f"Visualization serving error: {str(e)}")
        return jsonify({'error': 'Visualization not found'}), 404


@app.route('/api/files/<file_id>')
def get_file_info(file_id):
    """Get file information and metadata"""
    try:
        if file_id not in file_registry:
            return jsonify({'error': 'File not found'}), 404
        
        metadata = file_registry[file_id]
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': metadata['filename'],
            'upload_time': metadata['upload_time'],
            'properties': metadata['properties']
        })
        
    except Exception as e:
        logger.error(f"File info error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cleanup', methods=['POST'])
def manual_cleanup():
    """Manually trigger file cleanup"""
    try:
        cleanup_old_files()
        return jsonify({
            'success': True,
            'message': 'Cleanup completed',
            'remaining_files': len(file_registry)
        })
    except Exception as e:
        logger.error(f"Manual cleanup error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("Starting Satellite Image Processing Server...")
    print("Server will be available at: http://localhost:5000")
    print("API Documentation:")
    print("  POST /api/upload - Upload image file")
    print("  POST /api/process/module1 - Image fundamentals processing")
    print("  POST /api/process/module2 - Intensity transformations")
    print("  POST /api/process/module3 - Frequency domain filtering")
    print("  POST /api/process/module4 - Image restoration")
    print("  POST /api/process/module5 - Color image processing")
    print("  GET  /api/metrics/<file_id> - Get image metrics")
    print("  POST /api/compare - Compare two images")
    print("  GET  /api/visualizations/<filename> - Serve visualization images")
    
    app.run(debug=True, host='0.0.0.0', port=5000)