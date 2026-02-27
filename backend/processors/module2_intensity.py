"""
Module 2: Intensity Transformations and Spatial Filtering
Based on Chapter 3-4 of "Digital Image Processing" by Gonzalez & Woods

This module implements exact transformations from the textbook:
- Point processing operations (negative, log, power-law, piecewise linear)
- Histogram processing (equalization, specification)
- Spatial filtering (smoothing, sharpening)

All functions return processed images with histograms and statistics for visualization.
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Union
import math


def _prepare_image(image: np.ndarray) -> np.ndarray:
    """
    Convert image to grayscale and ensure proper format.
    
    Args:
        image: Input image (color or grayscale)
        
    Returns:
        Grayscale image as uint8
    """
    if len(image.shape) == 3:
        # Convert color image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Ensure uint8 format
    if gray.dtype != np.uint8:
        gray = gray.astype(np.uint8)
    
    return gray


def _calculate_histogram(image: np.ndarray) -> List[int]:
    """
    Calculate 256-bin histogram for the image.
    
    Args:
        image: Input grayscale image
        
    Returns:
        List of histogram counts (256 bins)
    """
    hist = cv2.calcHist([image], [0], None, [256], [0, 256])
    return hist.flatten().astype(int).tolist()


def _calculate_statistics(image: np.ndarray) -> Dict:
    """
    Calculate image statistics.
    
    Args:
        image: Input image
        
    Returns:
        Dictionary with mean, std, min, max
    """
    return {
        'mean': float(np.mean(image)),
        'std': float(np.std(image)),
        'min': int(np.min(image)),
        'max': int(np.max(image))
    }


def image_negative(image: np.ndarray) -> Dict:
    """
    Apply image negative transformation.
    
    Mathematical formula: s = L - 1 - r
    Where L = 256 for 8-bit images, r is input pixel value, s is output pixel value
    
    Args:
        image: Input image as numpy array
        
    Returns:
        dict with processed_image, histograms, and statistics
    """
    try:
        # Prepare image
        gray = _prepare_image(image)
        
        # Apply negative transformation: s = L - 1 - r
        L = 256
        negative_image = L - 1 - gray
        
        # Calculate histograms
        original_hist = _calculate_histogram(gray)
        processed_hist = _calculate_histogram(negative_image)
        
        # Calculate statistics
        original_stats = _calculate_statistics(gray)
        processed_stats = _calculate_statistics(negative_image)
        
        return {
            'success': True,
            'processed_image': negative_image,
            'original_histogram': original_hist,
            'processed_histogram': processed_hist,
            'statistics': {
                'original': original_stats,
                'processed': processed_stats
            },
            'transformation': 'Image Negative',
            'formula': 's = L - 1 - r (L=256)'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def log_transform(image: np.ndarray, c: float = 1.0) -> Dict:
    """
    Apply logarithmic transformation.
    
    Mathematical formula: s = c * log(1 + r)
    Where c is scaling constant, r is input pixel value, s is output pixel value
    
    Args:
        image: Input image as numpy array
        c: Scaling constant (default: 1.0)
        
    Returns:
        dict with processed_image, histograms, and statistics
    """
    try:
        # Validate inputs
        if c <= 0:
            raise ValueError("Scaling constant c must be positive")
        
        # Prepare image
        gray = _prepare_image(image)
        
        # Convert to float for calculations
        gray_float = gray.astype(np.float32)
        
        # Apply logarithmic transformation: s = c * log(1 + r)
        log_image = c * np.log(1 + gray_float)
        
        # Normalize to [0, 255] range
        log_image = (log_image / log_image.max()) * 255
        
        # Convert back to uint8
        log_image = log_image.astype(np.uint8)
        
        # Calculate histograms
        original_hist = _calculate_histogram(gray)
        processed_hist = _calculate_histogram(log_image)
        
        # Calculate statistics
        original_stats = _calculate_statistics(gray)
        processed_stats = _calculate_statistics(log_image)
        
        return {
            'success': True,
            'processed_image': log_image,
            'original_histogram': original_hist,
            'processed_histogram': processed_hist,
            'statistics': {
                'original': original_stats,
                'processed': processed_stats
            },
            'transformation': 'Logarithmic Transform',
            'formula': f's = {c} * log(1 + r)',
            'parameters': {'c': c}
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def power_law_transform(image: np.ndarray, gamma: float, c: float = 1.0) -> Dict:
    """
    Apply power-law (gamma) transformation.
    
    Mathematical formula: s = c * r^gamma
    Where c is scaling constant, gamma is power value, r is input pixel value
    
    Args:
        image: Input image as numpy array
        gamma: Power value (gamma < 1 brightens dark regions, gamma > 1 darkens bright regions)
        c: Scaling constant (default: 1.0)
        
    Returns:
        dict with processed_image, histograms, and statistics
    """
    # try:
    #     # Validate inputs
    #     if c <= 0:
    #         raise ValueError("Scaling constant c must be positive")
    #     if gamma <= 0:
    #         raise ValueError("Gamma value must be positive")
        
        # Prepare image
    gray = _prepare_image(image)
        
        # Convert to float and normalize to [0, 1]
    gray_normalized = gray.astype(np.float32) / 255.0
        
        # Apply power-law transformation: s = c * r^gamma
    power_image = c * np.power(gray_normalized, gamma)
        
        # Normalize to [0, 255] range
    power_image = (power_image / power_image.max()) * 255
        
        # Convert back to uint8
    power_image = power_image.astype(np.uint8)
        
        # Calculate histograms
    original_hist = _calculate_histogram(gray)
    processed_hist = _calculate_histogram(power_image)
        
        # Calculate statistics
    original_stats = _calculate_statistics(gray)
    processed_stats = _calculate_statistics(power_image)
        
    return {
            'success': True,
            'processed_image': power_image,
            'original_histogram': original_hist,
            'processed_histogram': processed_hist,
            'statistics': {
                'original': original_stats,
                'processed': processed_stats
            },
            'transformation': 'Power-Law Transform',
            'formula': f's = {c} * r^{gamma}',
            'parameters': {'gamma': gamma, 'c': c},
            'effect': 'Brightens dark regions' if gamma < 1 else 'Darkens bright regions' if gamma > 1 else 'No change'
        }
        
# except Exception as e:
#     return {
#             'success': False,
#             'error': str(e)
#         }


def piecewise_linear_transform(image: np.ndarray, points: List[Tuple[int, int]]) -> Dict:
    """
    Apply piecewise linear transformation.
    
    Uses linear interpolation between breakpoints defined by (r, s) tuples.
    Example: contrast stretching with (r1, s1), (r2, s2)
    
    Args:
        image: Input image as numpy array
        points: List of (r, s) tuples for breakpoints
        
    Returns:
        dict with processed_image, histograms, and statistics
    """
    try:
        # Validate inputs
        if len(points) < 2:
            raise ValueError("At least 2 breakpoints required")
        
        # Sort points by r value
        points = sorted(points, key=lambda x: x[0])
        
        # Validate point ranges
        for r, s in points:
            if not (0 <= r <= 255 and 0 <= s <= 255):
                raise ValueError("All point coordinates must be in range [0, 255]")
        
        # Prepare image
        gray = _prepare_image(image)
        
        # Create lookup table
        lookup_table = np.zeros(256, dtype=np.uint8)
        
        # Fill lookup table using linear interpolation
        for i in range(len(points) - 1):
            r1, s1 = points[i]
            r2, s2 = points[i + 1]
            
            # Linear interpolation: s = s1 + (s2 - s1) * (r - r1) / (r2 - r1)
            for r in range(r1, r2 + 1):
                if r2 != r1:  # Avoid division by zero
                    s = s1 + (s2 - s1) * (r - r1) / (r2 - r1)
                    lookup_table[r] = int(np.clip(s, 0, 255))
                else:
                    lookup_table[r] = s1
        
        # Apply transformation using lookup table
        transformed_image = lookup_table[gray]
        
        # Calculate histograms
        original_hist = _calculate_histogram(gray)
        processed_hist = _calculate_histogram(transformed_image)
        
        # Calculate statistics
        original_stats = _calculate_statistics(gray)
        processed_stats = _calculate_statistics(transformed_image)
        
        return {
            'success': True,
            'processed_image': transformed_image,
            'original_histogram': original_hist,
            'processed_histogram': processed_hist,
            'statistics': {
                'original': original_stats,
                'processed': processed_stats
            },
            'transformation': 'Piecewise Linear Transform',
            'breakpoints': points,
            'lookup_table': lookup_table.tolist()
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def histogram_equalization(image: np.ndarray) -> Dict:
    """
    Perform histogram equalization using CDF-based method.
    
    Steps:
    1. Calculate histogram
    2. Calculate CDF: cdf[i] = sum(hist[0:i+1])
    3. Normalize CDF: cdf_normalized = (cdf - cdf_min) / (total_pixels - cdf_min) * 255
    4. Map pixels using lookup table
    
    Args:
        image: Input image as numpy array
        
    Returns:
        dict with equalized image, histograms, and statistics
    """
    try:
        # Prepare image
        gray = _prepare_image(image)
        
        # Step 1: Calculate histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
        
        # Step 2: Calculate CDF
        cdf = np.cumsum(hist)
        
        # Step 3: Normalize CDF
        cdf_min = cdf[cdf > 0].min()  # First non-zero value
        total_pixels = gray.shape[0] * gray.shape[1]
        cdf_normalized = ((cdf - cdf_min) / (total_pixels - cdf_min)) * 255
        
        # Step 4: Create lookup table and apply transformation
        lookup_table = cdf_normalized.astype(np.uint8)
        equalized_image = lookup_table[gray]
        
        # Calculate histograms
        original_hist = hist.astype(int).tolist()
        processed_hist = _calculate_histogram(equalized_image)
        
        # Calculate statistics
        original_stats = _calculate_statistics(gray)
        processed_stats = _calculate_statistics(equalized_image)
        
        return {
            'success': True,
            'processed_image': equalized_image,
            'original_histogram': original_hist,
            'processed_histogram': processed_hist,
            'statistics': {
                'original': original_stats,
                'processed': processed_stats
            },
            'transformation': 'Histogram Equalization',
            'cdf': cdf.tolist(),
            'cdf_normalized': cdf_normalized.tolist(),
            'lookup_table': lookup_table.tolist()
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def histogram_specification(image: np.ndarray, target_histogram: List[int]) -> Dict:
    """
    Match image histogram to target distribution using inverse CDF method.
    
    Args:
        image: Input image as numpy array
        target_histogram: Target histogram (256 bins)
        
    Returns:
        dict with matched image, histograms, and statistics
    """
    try:
        # Validate inputs
        if len(target_histogram) != 256:
            raise ValueError("Target histogram must have 256 bins")
        
        # Prepare image
        gray = _prepare_image(image)
        
        # Calculate original histogram and CDF
        original_hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
        original_cdf = np.cumsum(original_hist)
        
        # Normalize original CDF
        original_cdf_min = original_cdf[original_cdf > 0].min()
        total_pixels = gray.shape[0] * gray.shape[1]
        original_cdf_norm = ((original_cdf - original_cdf_min) / (total_pixels - original_cdf_min)) * 255
        
        # Calculate target CDF
        target_hist_array = np.array(target_histogram, dtype=np.float32)
        target_cdf = np.cumsum(target_hist_array)
        
        # Normalize target CDF
        target_cdf_min = target_cdf[target_cdf > 0].min()
        target_total = np.sum(target_hist_array)
        target_cdf_norm = ((target_cdf - target_cdf_min) / (target_total - target_cdf_min)) * 255
        
        # Create inverse mapping using interpolation
        lookup_table = np.zeros(256, dtype=np.uint8)
        
        for i in range(256):
            # Find closest value in target CDF
            diff = np.abs(target_cdf_norm - original_cdf_norm[i])
            closest_idx = np.argmin(diff)
            lookup_table[i] = closest_idx
        
        # Apply transformation
        matched_image = lookup_table[gray]
        
        # Calculate histograms
        original_hist_list = original_hist.astype(int).tolist()
        processed_hist = _calculate_histogram(matched_image)
        
        # Calculate statistics
        original_stats = _calculate_statistics(gray)
        processed_stats = _calculate_statistics(matched_image)
        
        return {
            'success': True,
            'processed_image': matched_image,
            'original_histogram': original_hist_list,
            'processed_histogram': processed_hist,
            'target_histogram': target_histogram,
            'statistics': {
                'original': original_stats,
                'processed': processed_stats
            },
            'transformation': 'Histogram Specification',
            'lookup_table': lookup_table.tolist()
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def spatial_smoothing(image: np.ndarray, kernel_size: int, method: str) -> Dict:
    """
    Apply spatial smoothing filters.
    
    Args:
        image: Input image as numpy array
        kernel_size: Size of the kernel (must be odd)
        method: 'average', 'gaussian', or 'median'
        
    Returns:
        dict with smoothed image, histograms, and statistics
    """
    try:
        # Validate inputs
        if kernel_size % 2 == 0:
            raise ValueError("Kernel size must be odd")
        if kernel_size < 3:
            raise ValueError("Kernel size must be at least 3")
        if method not in ['average', 'gaussian', 'median']:
            raise ValueError("Method must be 'average', 'gaussian', or 'median'")
        
        # Prepare image
        gray = _prepare_image(image)
        
        # Apply smoothing based on method
        if method == 'average':
            kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)
            smoothed_image = cv2.filter2D(gray, -1, kernel)
        elif method == 'gaussian':
            smoothed_image = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
        elif method == 'median':
            smoothed_image = cv2.medianBlur(gray, kernel_size)
        
        # Calculate histograms
        original_hist = _calculate_histogram(gray)
        processed_hist = _calculate_histogram(smoothed_image)
        
        # Calculate statistics
        original_stats = _calculate_statistics(gray)
        processed_stats = _calculate_statistics(smoothed_image)
        
        return {
            'success': True,
            'processed_image': smoothed_image,
            'original_histogram': original_hist,
            'processed_histogram': processed_hist,
            'statistics': {
                'original': original_stats,
                'processed': processed_stats
            },
            'transformation': f'Spatial Smoothing ({method})',
            'parameters': {'kernel_size': kernel_size, 'method': method}
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def spatial_sharpening(image: np.ndarray, method: str, k: float = 1.0) -> Dict:
    """
    Apply spatial sharpening filters.
    
    Args:
        image: Input image as numpy array
        method: 'laplacian', 'unsharp_masking', or 'high_boost'
        k: Enhancement factor for unsharp masking (default: 1.0)
        
    Returns:
        dict with sharpened image, histograms, and statistics
    """
    try:
        # Validate inputs
        if method not in ['laplacian', 'unsharp_masking', 'high_boost']:
            raise ValueError("Method must be 'laplacian', 'unsharp_masking', or 'high_boost'")
        
        # Prepare image
        gray = _prepare_image(image)
        
        # Apply sharpening based on method
        if method == 'laplacian':
            # Laplacian kernel: [0, 1, 0], [1, -4, 1], [0, 1, 0]
            laplacian_kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
            laplacian = cv2.filter2D(gray.astype(np.float32), -1, laplacian_kernel)
            sharpened_image = gray.astype(np.float32) - laplacian
            sharpened_image = np.clip(sharpened_image, 0, 255).astype(np.uint8)
            
        elif method == 'unsharp_masking':
            # Unsharp masking: sharpened = original + k * (original - blurred)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            mask = gray.astype(np.float32) - blurred.astype(np.float32)
            sharpened_image = gray.astype(np.float32) + k * mask
            sharpened_image = np.clip(sharpened_image, 0, 255).astype(np.uint8)
            
        elif method == 'high_boost':
            # High-boost filtering: enhanced = A * original + k * (original - blurred)
            A = 1.0  # Amplification factor
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            mask = gray.astype(np.float32) - blurred.astype(np.float32)
            sharpened_image = A * gray.astype(np.float32) + k * mask
            sharpened_image = np.clip(sharpened_image, 0, 255).astype(np.uint8)
        
        # Calculate histograms
        original_hist = _calculate_histogram(gray)
        processed_hist = _calculate_histogram(sharpened_image)
        
        # Calculate statistics
        original_stats = _calculate_statistics(gray)
        processed_stats = _calculate_statistics(sharpened_image)
        
        return {
            'success': True,
            'processed_image': sharpened_image,
            'original_histogram': original_hist,
            'processed_histogram': processed_hist,
            'statistics': {
                'original': original_stats,
                'processed': processed_stats
            },
            'transformation': f'Spatial Sharpening ({method})',
            'parameters': {'method': method, 'k': k}
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Legacy class-based interface for backward compatibility
class IntensityProcessor:
    """Legacy class-based interface for backward compatibility"""
    
    def __init__(self):
        self.supported_operations = [
            'image_negative',
            'log_transform',
            'power_law_transform',
            'piecewise_linear_transform',
            'histogram_equalization',
            'histogram_specification',
            'spatial_smoothing',
            'spatial_sharpening'
        ]
    
    def process(self, data):
        """Main processing function for legacy interface"""
        operation = data.get('operation')
        
        if operation not in self.supported_operations:
            return {'error': f'Unsupported operation: {operation}'}
        
        try:
            image = data.get('image')
            if image is None:
                return {'error': 'No image provided'}
            
            if operation == 'image_negative':
                return image_negative(image)
            
            elif operation == 'log_transform':
                c = data.get('c', 1.0)
                return log_transform(image, c)
            
            elif operation == 'power_law_transform':
                gamma = data.get('gamma', 1.0)
                c = data.get('c', 1.0)
                return power_law_transform(image, gamma, c)
            
            elif operation == 'piecewise_linear_transform':
                points = data.get('points', [(0, 0), (255, 255)])
                return piecewise_linear_transform(image, points)
            
            elif operation == 'histogram_equalization':
                return histogram_equalization(image)
            
            elif operation == 'histogram_specification':
                target_hist = data.get('target_histogram', [1] * 256)
                return histogram_specification(image, target_hist)
            
            elif operation == 'spatial_smoothing':
                kernel_size = data.get('kernel_size', 3)
                method = data.get('method', 'average')
                return spatial_smoothing(image, kernel_size, method)
            
            elif operation == 'spatial_sharpening':
                method = data.get('method', 'laplacian')
                k = data.get('k', 1.0)
                return spatial_sharpening(image, method, k)
            
            else:
                return {'error': 'Operation not implemented'}
                
        except Exception as e:
            return {'error': f'Processing failed: {str(e)}'}