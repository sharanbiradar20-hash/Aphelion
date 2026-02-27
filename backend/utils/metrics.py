"""
Image Quality Metrics and Analysis
Utility functions for calculating various image quality metrics

Enhanced with exact formulas and comprehensive metrics for faculty presentation.
"""

import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim
from scipy import ndimage
import math
from typing import Dict, Tuple, Union


def calculate_psnr(original: np.ndarray, processed: np.ndarray) -> float:
    """
    Calculate Peak Signal-to-Noise Ratio with exact formula.
    
    EXACT formula: PSNR = 10 * log10(MAX^2 / MSE)
    Where MAX = 255 for 8-bit images, MSE = mean((original - processed)^2)
    
    Args:
        original: Original image (reference)
        processed: Processed image (test)
        
    Returns:
        PSNR value in dB
    """
    try:
        if original is None or processed is None:
            return float('nan')
        
        # Ensure images have the same shape
        if original.shape != processed.shape:
            return float('nan')
        
        # Convert to float32 for calculations
        orig_float = original.astype(np.float32)
        proc_float = processed.astype(np.float32)
        
        # Calculate MSE: mean((original - processed)^2)
        mse = np.mean((orig_float - proc_float) ** 2)
        
        # Avoid division by zero
        if mse == 0:
            return float('inf')
        
        # Calculate PSNR: 10 * log10(MAX^2 / MSE)
        MAX = 255.0  # Maximum pixel value for 8-bit images
        psnr = 10 * np.log10((MAX ** 2) / mse)
        
        return float(psnr)
        
    except Exception as e:
        return float('nan')


def calculate_mse(original: np.ndarray, processed: np.ndarray) -> float:
    """
    Calculate Mean Squared Error between two images.
    
    Args:
        original: Original image (reference)
        processed: Processed image (test)
        
    Returns:
        MSE value
    """
    try:
        if original is None or processed is None:
            return float('nan')
        
        # Ensure images have the same shape
        if original.shape != processed.shape:
            return float('nan')
        
        # Convert to float32 for calculations
        orig_float = original.astype(np.float32)
        proc_float = processed.astype(np.float32)
        
        # Calculate MSE: mean((original - processed)^2)
        mse = np.mean((orig_float - proc_float) ** 2)
        
        return float(mse)
        
    except Exception as e:
        return float('nan')


def calculate_ssim(original: np.ndarray, processed: np.ndarray, window_size: int = 11) -> float:
    """
    Calculate Structural Similarity Index using sliding window approach.
    
    Uses formula from Wang et al. 2004 paper with sliding window.
    
    Args:
        original: Original image (reference)
        processed: Processed image (test)
        window_size: Size of sliding window (default: 11)
        
    Returns:
        SSIM value between 0 and 1
    """
    try:
        if original is None or processed is None:
            return float('nan')
        
        # Ensure images have the same shape
        if original.shape != processed.shape:
            return float('nan')
        
        # Convert to grayscale if necessary
        if len(original.shape) == 3:
            original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        if len(processed.shape) == 3:
            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
        
        # Calculate SSIM using sliding window approach
        ssim_value = ssim(original, processed, win_size=window_size)
        
        return float(ssim_value)
        
    except Exception as e:
        return float('nan')


def calculate_snr(image: np.ndarray, noise: np.ndarray) -> float:
    """
    Calculate Signal-to-Noise Ratio.
    
    Formula: SNR = 10 * log10(signal_power / noise_power)
    
    Args:
        image: Original signal image
        noise: Noise component
        
    Returns:
        SNR in dB
    """
    try:
        if image is None or noise is None:
            return float('nan')
        
        # Ensure images have the same shape
        if image.shape != noise.shape:
            return float('nan')
        
        # Convert to float32 for calculations
        signal = image.astype(np.float32)
        noise_comp = noise.astype(np.float32)
        
        # Calculate signal power
        signal_power = np.mean(signal ** 2)
        
        # Calculate noise power
        noise_power = np.mean(noise_comp ** 2)
        
        # Avoid division by zero
        if noise_power == 0:
            return float('inf')
        
        # Calculate SNR: 10 * log10(signal_power / noise_power)
        snr = 10 * np.log10(signal_power / noise_power)
        
        return float(snr)
        
    except Exception as e:
        return float('nan')


def sharpness_index(image: np.ndarray) -> float:
    """
    Calculate sharpness index using Laplacian variance method.
    
    Higher value indicates sharper image.
    
    Args:
        image: Input image
        
    Returns:
        Sharpness score
    """
    try:
        if image is None:
            return float('nan')
        
        # Convert to grayscale if necessary
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply Laplacian operator
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        
        # Calculate variance of Laplacian
        sharpness = np.var(laplacian)
        
        return float(sharpness)
        
    except Exception as e:
        return float('nan')


def contrast_measure(image: np.ndarray) -> float:
    """
    Calculate RMS contrast measure.
    
    Formula: sqrt(mean((pixel - mean)^2))
    
    Args:
        image: Input image
        
    Returns:
        Contrast value
    """
    try:
        if image is None:
            return float('nan')
        
        # Convert to grayscale if necessary
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Convert to float32
        gray_float = gray.astype(np.float32)
        
        # Calculate mean
        mean_value = np.mean(gray_float)
        
        # Calculate RMS contrast: sqrt(mean((pixel - mean)^2))
        contrast = np.sqrt(np.mean((gray_float - mean_value) ** 2))
        
        return float(contrast)
        
    except Exception as e:
        return float('nan')


def entropy_measure(image: np.ndarray) -> float:
    """
    Calculate image entropy.
    
    Formula: -sum(p * log2(p)) where p = normalized histogram
    
    Args:
        image: Input image
        
    Returns:
        Entropy in bits
    """
    try:
        if image is None:
            return float('nan')
        
        # Convert to grayscale if necessary
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Calculate histogram
        histogram = cv2.calcHist([gray], [0], None, [256], [0, 256])
        histogram = histogram.flatten()
        
        # Normalize histogram to get probabilities
        total_pixels = np.sum(histogram)
        if total_pixels == 0:
            return float('nan')
        
        probabilities = histogram / total_pixels
        
        # Remove zero probabilities to avoid log(0)
        probabilities = probabilities[probabilities > 0]
        
        # Calculate entropy: -sum(p * log2(p))
        entropy = -np.sum(probabilities * np.log2(probabilities))
        
        return float(entropy)
        
    except Exception as e:
        return float('nan')


def edge_strength(image: np.ndarray) -> float:
    """
    Calculate mean gradient magnitude using Sobel operator.
    
    Args:
        image: Input image
        
    Returns:
        Average edge strength
    """
    try:
        if image is None:
            return float('nan')
        
        # Convert to grayscale if necessary
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Calculate gradients using Sobel operator
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Calculate gradient magnitude
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Calculate mean edge strength
        edge_strength = np.mean(gradient_magnitude)
        
        return float(edge_strength)
        
    except Exception as e:
        return float('nan')


def calculate_image_metrics(image: np.ndarray) -> Dict:
    """
    Calculate comprehensive image statistics and metrics.
    
    Args:
        image: numpy array representing the image
        
    Returns:
        dict: Dictionary containing various image metrics
    """
    try:
        if image is None:
            return {'error': 'Invalid image'}
        
        # Convert to grayscale if color image
        if len(image.shape) == 3:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = image
        
        # Basic statistics
        height, width = gray_image.shape
        total_pixels = height * width
        
        # Intensity statistics
        mean_intensity = np.mean(gray_image)
        std_intensity = np.std(gray_image)
        min_intensity = np.min(gray_image)
        max_intensity = np.max(gray_image)
        
        # Calculate additional metrics
        sharpness = sharpness_index(gray_image)
        contrast = contrast_measure(gray_image)
        entropy = entropy_measure(gray_image)
        edge_strength_val = edge_strength(gray_image)
        
        # Histogram statistics
        histogram = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
        
        # Calculate entropy (alternative method)
        histogram_normalized = histogram / total_pixels
        histogram_normalized = histogram_normalized[histogram_normalized > 0]
        entropy_alt = -np.sum(histogram_normalized * np.log2(histogram_normalized))
        
        # Calculate contrast (alternative method)
        contrast_alt = max_intensity - min_intensity
        
        # Calculate dynamic range
        dynamic_range = max_intensity - min_intensity
        
        return {
            'dimensions': {
                'height': int(height),
                'width': int(width),
                'total_pixels': int(total_pixels)
            },
            'intensity_statistics': {
                'mean': float(mean_intensity),
                'std': float(std_intensity),
                'min': float(min_intensity),
                'max': float(max_intensity),
                'range': float(contrast_alt)
            },
            'image_quality': {
                'entropy': float(entropy),
                'entropy_alt': float(entropy_alt),
                'dynamic_range': float(dynamic_range),
                'contrast': float(contrast),
                'contrast_alt': float(contrast_alt),
                'sharpness': float(sharpness),
                'edge_strength': float(edge_strength_val)
            }
        }
        
    except Exception as e:
        return {'error': f'Failed to calculate metrics: {str(e)}'}


def calculate_histogram_features(image: np.ndarray) -> Dict:
    """
    Calculate histogram-based features.
    
    Args:
        image: numpy array representing the image
        
    Returns:
        dict: Dictionary containing histogram features
    """
    try:
        if image is None:
            return {'error': 'Invalid image'}
        
        # Convert to grayscale if color image
        if len(image.shape) == 3:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = image
        
        # Calculate histogram
        histogram = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
        histogram = histogram.flatten()
        
        # Normalize histogram
        histogram_normalized = histogram / np.sum(histogram)
        
        # Calculate features
        mean_intensity = np.sum(np.arange(256) * histogram_normalized)
        variance = np.sum(((np.arange(256) - mean_intensity) ** 2) * histogram_normalized)
        
        # Calculate skewness and kurtosis
        if variance > 0:
            skewness = np.sum(((np.arange(256) - mean_intensity) ** 3) * histogram_normalized) / (variance ** 1.5)
            kurtosis = np.sum(((np.arange(256) - mean_intensity) ** 4) * histogram_normalized) / (variance ** 2) - 3
        else:
            skewness = 0
            kurtosis = 0
        
        return {
            'mean_intensity': float(mean_intensity),
            'variance': float(variance),
            'skewness': float(skewness),
            'kurtosis': float(kurtosis),
            'histogram': histogram.tolist()
        }
        
    except Exception as e:
        return {'error': f'Failed to calculate histogram features: {str(e)}'}


def calculate_edge_density(image: np.ndarray) -> float:
    """
    Calculate edge density in the image.
    
    Args:
        image: numpy array representing the image
        
    Returns:
        Edge density (ratio of edge pixels to total pixels)
    """
    try:
        if image is None:
            return float('nan')
        
        # Convert to grayscale if color image
        if len(image.shape) == 3:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = image
        
        # Apply Canny edge detection
        edges = cv2.Canny(gray_image, 50, 150)
        
        # Calculate edge density
        total_pixels = gray_image.shape[0] * gray_image.shape[1]
        edge_pixels = np.sum(edges > 0)
        edge_density = edge_pixels / total_pixels
        
        return float(edge_density)
        
    except Exception as e:
        return float('nan')


def calculate_texture_features(image: np.ndarray) -> Dict:
    """
    Calculate basic texture features.
    
    Args:
        image: numpy array representing the image
        
    Returns:
        dict: Dictionary containing texture features
    """
    try:
        if image is None:
            return {'error': 'Invalid image'}
        
        # Convert to grayscale if color image
        if len(image.shape) == 3:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = image
        
        # Calculate gradient magnitude
        grad_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Calculate texture features
        texture_mean = np.mean(gradient_magnitude)
        texture_std = np.std(gradient_magnitude)
        texture_variance = np.var(gradient_magnitude)
        
        return {
            'texture_mean': float(texture_mean),
            'texture_std': float(texture_std),
            'texture_variance': float(texture_variance),
            'edge_density': calculate_edge_density(gray_image)
        }
        
    except Exception as e:
        return {'error': f'Failed to calculate texture features: {str(e)}'}