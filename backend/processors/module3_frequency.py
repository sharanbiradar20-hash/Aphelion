"""
Module 3: Frequency Domain Filtering
Based on Chapter 4-5 of "Digital Image Processing" by Gonzalez & Woods

This module implements proper FFT-based filtering operations:
- 2D Discrete Fourier Transform (DFT) computation
- Ideal, Butterworth, and Gaussian filters
- Low-pass and high-pass filtering
- Frequency domain visualization

All operations use proper FFT with fftshift/ifftshift for correct centering.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import os
from typing import Dict, Tuple, Union
import math


def _prepare_image(image: np.ndarray) -> np.ndarray:
    """
    Convert image to grayscale and ensure proper format for FFT.
    
    Args:
        image: Input image (color or grayscale)
        
    Returns:
        Grayscale image as float32
    """
    if len(image.shape) == 3:
        # Convert color image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Convert to float32 for FFT operations
    gray_float = gray.astype(np.float32)
    
    return gray_float #/////////////////////// doubt hai, check karna hai baadme


def create_distance_matrix(rows: int, cols: int) -> np.ndarray:
    """
    Create meshgrid of distances from center for frequency domain operations.
    
    Mathematical formula: D[u,v] = sqrt((u-M/2)^2 + (v-N/2)^2)
    Where M, N are image dimensions and (M/2, N/2) is the center
    
    Args:
        rows: Number of rows (height)
        cols: Number of columns (width)
        
    Returns:
        Distance matrix D where D[u,v] = distance from center
    """
    # Create coordinate arrays
    u = np.arange(rows)
    v = np.arange(cols)
    
    # Create meshgrid
    U, V = np.meshgrid(v, u)  # Note: swapped for proper indexing
    
    # Calculate center coordinates
    center_u = rows // 2
    center_v = cols // 2
    
    # Calculate distance from center
    D = np.sqrt((U - center_v)**2 + (V - center_u)**2)
    
    return D


def compute_dft_2d(image: np.ndarray) -> Dict:
    """
    Compute 2D Discrete Fourier Transform with proper centering.
    
    Steps:
    1. Convert to grayscale if needed
    2. Apply 2D FFT: F = np.fft.fft2(image)
    3. Shift zero frequency to center: F_shifted = np.fft.fftshift(F)
    4. Calculate magnitude spectrum: magnitude = np.log(1 + np.abs(F_shifted))
    5. Calculate phase spectrum: phase = np.angle(F_shifted)
    
    Args:
        image: Input image as numpy array
        
    Returns:
        dict with F_shifted, magnitude_spectrum, phase_spectrum
    """
    try:
        # Prepare image
        gray = _prepare_image(image)
        
        # Step 1: Apply 2D FFT
        F = np.fft.fft2(gray)
        
        # Step 2: Shift zero frequency to center
        F_shifted = np.fft.fftshift(F)
        
        # Step 3: Calculate magnitude spectrum (log-scaled)
        magnitude = np.log(1 + np.abs(F_shifted))
        
        # Step 4: Calculate phase spectrum
        phase = np.angle(F_shifted)
        
        # Calculate additional metrics
        magnitude_db = 20 * np.log10(1 + np.abs(F_shifted))
        
        return {
            'success': True,
            'F_shifted': F_shifted,
            'magnitude_spectrum': magnitude,
            'magnitude_db': magnitude_db,
            'phase_spectrum': phase,
            'original_image': gray,
            'image_shape': gray.shape,
            'frequency_center': (gray.shape[0] // 2, gray.shape[1] // 2)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def ideal_lowpass_filter(image: np.ndarray, cutoff_frequency: float) -> Dict:
    """
    Apply ideal low-pass filter in frequency domain.
    
    Steps:
    1. Get DFT of image
    2. Create circular mask: D(u,v) = sqrt((u-M/2)^2 + (v-N/2)^2)
    3. H(u,v) = 1 if D(u,v) <= D0, else 0
    4. Multiply: G(u,v) = H(u,v) * F(u,v)
    5. Inverse FFT: g = ifft2(ifftshift(G))
    
    Args:
        image: Input image as numpy array
        cutoff_frequency: Cutoff frequency D0 in pixels (typical range: 10-100)
        
    Returns:
        dict with filtered image, filter mask, and spectrums
    """
    try:
        # Validate inputs
        if cutoff_frequency <= 0:
            raise ValueError("Cutoff frequency must be positive")
        
        # Prepare image and compute DFT
        gray = _prepare_image(image)
        dft_result = compute_dft_2d(gray)
        
        if not dft_result['success']:
            return dft_result
        
        F_shifted = dft_result['F_shifted']
        rows, cols = gray.shape
        
        # Create distance matrix
        D = create_distance_matrix(rows, cols)
        
        # Create ideal low-pass filter mask
        # H(u,v) = 1 if D(u,v) <= D0, else 0
        H = (D <= cutoff_frequency).astype(np.float32)
        
        # Apply filter in frequency domain
        G_shifted = H * F_shifted
        
        # Inverse FFT to get filtered image
        G = np.fft.ifftshift(G_shifted)
        g = np.fft.ifft2(G)
        
        # Take real part and normalize to [0, 255]
        filtered_image = np.real(g)
        filtered_image = np.clip(filtered_image, 0, 255).astype(np.uint8)
        
        # Calculate spectrums for visualization
        original_magnitude = np.log(1 + np.abs(F_shifted))
        filtered_magnitude = np.log(1 + np.abs(G_shifted))
        
        return {
            'success': True,
            'filtered_image': filtered_image,
            'original_spectrum': original_magnitude,
            'filtered_spectrum': filtered_magnitude,
            'filter_mask': H,
            'parameters': {'cutoff': cutoff_frequency, 'type': 'ideal_lowpass'},
            'distance_matrix': D,
            'filter_response': H
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def ideal_highpass_filter(image: np.ndarray, cutoff_frequency: float) -> Dict:
    """
    Apply ideal high-pass filter in frequency domain.
    
    Same as lowpass but: H(u,v) = 0 if D(u,v) <= D0, else 1
    
    Args:
        image: Input image as numpy array
        cutoff_frequency: Cutoff frequency D0 in pixels
        
    Returns:
        dict with filtered image, filter mask, and spectrums
    """
    try:
        # Validate inputs
        if cutoff_frequency <= 0:
            raise ValueError("Cutoff frequency must be positive")
        
        # Prepare image and compute DFT
        gray = _prepare_image(image)
        dft_result = compute_dft_2d(gray)
        
        if not dft_result['success']:
            return dft_result
        
        F_shifted = dft_result['F_shifted']
        rows, cols = gray.shape
        
        # Create distance matrix
        D = create_distance_matrix(rows, cols)
        
        # Create ideal high-pass filter mask
        # H(u,v) = 0 if D(u,v) <= D0, else 1
        H = (D > cutoff_frequency).astype(np.float32)
        
        # Apply filter in frequency domain
        G_shifted = H * F_shifted
        
        # Inverse FFT to get filtered image
        G = np.fft.ifftshift(G_shifted)
        g = np.fft.ifft2(G)
        
        # Take real part and normalize to [0, 255]
        filtered_image = np.real(g)
        filtered_image = np.clip(filtered_image, 0, 255).astype(np.uint8)
        
        # Calculate spectrums for visualization
        original_magnitude = np.log(1 + np.abs(F_shifted))
        filtered_magnitude = np.log(1 + np.abs(G_shifted))
        
        return {
            'success': True,
            'filtered_image': filtered_image,
            'original_spectrum': original_magnitude,
            'filtered_spectrum': filtered_magnitude,
            'filter_mask': H,
            'parameters': {'cutoff': cutoff_frequency, 'type': 'ideal_highpass'},
            'distance_matrix': D,
            'filter_response': H
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def butterworth_lowpass_filter(image: np.ndarray, cutoff_frequency: float, order: int = 2) -> Dict:
    """
    Apply Butterworth low-pass filter in frequency domain.
    
    Formula: H(u,v) = 1 / (1 + (D(u,v)/D0)^(2*n))
    Where n is the order (typically 2 or 3)
    
    Args:
        image: Input image as numpy array
        cutoff_frequency: Cutoff frequency D0 in pixels
        order: Filter order n (typically 2 or 3)
        
    Returns:
        dict with filtered image, filter mask, and spectrums
    """
    try:
        # Validate inputs
        if cutoff_frequency <= 0:
            raise ValueError("Cutoff frequency must be positive")
        if order <= 0:
            raise ValueError("Filter order must be positive")
        
        # Prepare image and compute DFT
        gray = _prepare_image(image)
        dft_result = compute_dft_2d(gray)
        
        if not dft_result['success']:
            return dft_result
        
        F_shifted = dft_result['F_shifted']
        rows, cols = gray.shape
        
        # Create distance matrix
        D = create_distance_matrix(rows, cols)
        
        # Create Butterworth low-pass filter mask
        # H(u,v) = 1 / (1 + (D(u,v)/D0)^(2*n))
        H = 1 / (1 + (D / cutoff_frequency)**(2 * order))
        
        # Apply filter in frequency domain
        G_shifted = H * F_shifted
        
        # Inverse FFT to get filtered image
        G = np.fft.ifftshift(G_shifted)
        g = np.fft.ifft2(G)
        
        # Take real part and normalize to [0, 255]
        filtered_image = np.real(g)
        filtered_image = np.clip(filtered_image, 0, 255).astype(np.uint8)
        
        # Calculate spectrums for visualization
        original_magnitude = np.log(1 + np.abs(F_shifted))
        filtered_magnitude = np.log(1 + np.abs(G_shifted))
        
        return {
            'success': True,
            'filtered_image': filtered_image,
            'original_spectrum': original_magnitude,
            'filtered_spectrum': filtered_magnitude,
            'filter_mask': H,
            'parameters': {'cutoff': cutoff_frequency, 'order': order, 'type': 'butterworth_lowpass'},
            'distance_matrix': D,
            'filter_response': H
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def butterworth_highpass_filter(image: np.ndarray, cutoff_frequency: float, order: int = 2) -> Dict:
    """
    Apply Butterworth high-pass filter in frequency domain.
    
    Formula: H(u,v) = 1 / (1 + (D0/D(u,v))^(2*n))
    
    Args:
        image: Input image as numpy array
        cutoff_frequency: Cutoff frequency D0 in pixels
        order: Filter order n (typically 2 or 3)
        
    Returns:
        dict with filtered image, filter mask, and spectrums
    """
    try:
        # Validate inputs
        if cutoff_frequency <= 0:
            raise ValueError("Cutoff frequency must be positive")
        if order <= 0:
            raise ValueError("Filter order must be positive")
        
        # Prepare image and compute DFT
        gray = _prepare_image(image)
        dft_result = compute_dft_2d(gray)
        
        if not dft_result['success']:
            return dft_result
        
        F_shifted = dft_result['F_shifted']
        rows, cols = gray.shape
        
        # Create distance matrix
        D = create_distance_matrix(rows, cols)
        
        # Avoid division by zero for D = 0
        D_safe = np.where(D == 0, 1e-10, D)
        
        # Create Butterworth high-pass filter mask
        # H(u,v) = 1 / (1 + (D0/D(u,v))^(2*n))
        H = 1 / (1 + (cutoff_frequency / D_safe)**(2 * order))
        
        # Handle center point (D = 0) separately
        center_mask = (D == 0)
        H[center_mask] = 0  # High-pass filter blocks DC component
        
        # Apply filter in frequency domain
        G_shifted = H * F_shifted
        
        # Inverse FFT to get filtered image
        G = np.fft.ifftshift(G_shifted)
        g = np.fft.ifft2(G)
        
        # Take real part and normalize to [0, 255]
        filtered_image = np.real(g)
        filtered_image = np.clip(filtered_image, 0, 255).astype(np.uint8)
        
        # Calculate spectrums for visualization
        original_magnitude = np.log(1 + np.abs(F_shifted))
        filtered_magnitude = np.log(1 + np.abs(G_shifted))
        
        return {
            'success': True,
            'filtered_image': filtered_image,
            'original_spectrum': original_magnitude,
            'filtered_spectrum': filtered_magnitude,
            'filter_mask': H,
            'parameters': {'cutoff': cutoff_frequency, 'order': order, 'type': 'butterworth_highpass'},
            'distance_matrix': D,
            'filter_response': H
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def gaussian_lowpass_filter(image: np.ndarray, cutoff_frequency: float) -> Dict:
    """
    Apply Gaussian low-pass filter in frequency domain.
    
    Formula: H(u,v) = exp(-D^2(u,v) / (2*D0^2))
    No ringing artifacts compared to ideal filter
    
    Args:
        image: Input image as numpy array
        cutoff_frequency: Cutoff frequency D0 in pixels
        
    Returns:
        dict with filtered image, filter mask, and spectrums
    """
    try:
        # Validate inputs
        if cutoff_frequency <= 0:
            raise ValueError("Cutoff frequency must be positive")
        
        # Prepare image and compute DFT
        gray = _prepare_image(image)
        dft_result = compute_dft_2d(gray)
        
        if not dft_result['success']:
            return dft_result
        
        F_shifted = dft_result['F_shifted']
        rows, cols = gray.shape
        
        # Create distance matrix
        D = create_distance_matrix(rows, cols)
        
        # Create Gaussian low-pass filter mask
        # H(u,v) = exp(-D^2(u,v) / (2*D0^2))
        H = np.exp(-(D**2) / (2 * cutoff_frequency**2))
        
        # Apply filter in frequency domain
        G_shifted = H * F_shifted
        
        # Inverse FFT to get filtered image
        G = np.fft.ifftshift(G_shifted)
        g = np.fft.ifft2(G)
        
        # Take real part and normalize to [0, 255]
        filtered_image = np.real(g)
        filtered_image = np.clip(filtered_image, 0, 255).astype(np.uint8)
        
        # Calculate spectrums for visualization
        original_magnitude = np.log(1 + np.abs(F_shifted))
        filtered_magnitude = np.log(1 + np.abs(G_shifted))
        
        return {
            'success': True,
            'filtered_image': filtered_image,
            'original_spectrum': original_magnitude,
            'filtered_spectrum': filtered_magnitude,
            'filter_mask': H,
            'parameters': {'cutoff': cutoff_frequency, 'type': 'gaussian_lowpass'},
            'distance_matrix': D,
            'filter_response': H
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def gaussian_highpass_filter(image: np.ndarray, cutoff_frequency: float) -> Dict:
    """
    Apply Gaussian high-pass filter in frequency domain.
    
    Formula: H(u,v) = 1 - exp(-D^2(u,v) / (2*D0^2))
    
    Args:
        image: Input image as numpy array
        cutoff_frequency: Cutoff frequency D0 in pixels
        
    Returns:
        dict with filtered image, filter mask, and spectrums
    """
    try:
        # Validate inputs
        if cutoff_frequency <= 0:
            raise ValueError("Cutoff frequency must be positive")
        
        # Prepare image and compute DFT
        gray = _prepare_image(image)
        dft_result = compute_dft_2d(gray)
        
        if not dft_result['success']:
            return dft_result
        
        F_shifted = dft_result['F_shifted']
        rows, cols = gray.shape
        
        # Create distance matrix
        D = create_distance_matrix(rows, cols)
        
        # Create Gaussian high-pass filter mask
        # H(u,v) = 1 - exp(-D^2(u,v) / (2*D0^2))
        H = 1 - np.exp(-(D**2) / (2 * cutoff_frequency**2))
        
        # Apply filter in frequency domain
        G_shifted = H * F_shifted
        
        # Inverse FFT to get filtered image
        G = np.fft.ifftshift(G_shifted)
        g = np.fft.ifft2(G)
        
        # Take real part and normalize to [0, 255]
        filtered_image = np.real(g)
        filtered_image = np.clip(filtered_image, 0, 255).astype(np.uint8)
        
        # Calculate spectrums for visualization
        original_magnitude = np.log(1 + np.abs(F_shifted))
        filtered_magnitude = np.log(1 + np.abs(G_shifted))
        
        return {
            'success': True,
            'filtered_image': filtered_image,
            'original_spectrum': original_magnitude,
            'filtered_spectrum': filtered_magnitude,
            'filter_mask': H,
            'parameters': {'cutoff': cutoff_frequency, 'type': 'gaussian_highpass'},
            'distance_matrix': D,
            'filter_response': H
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def visualize_frequency_domain(F_shifted: np.ndarray, filter_mask: np.ndarray = None, 
                             title: str = "Frequency Domain Analysis") -> Dict:
    """
    Create comprehensive frequency domain visualization.
    
    Creates 2x2 subplot:
    - Magnitude spectrum (log scale)
    - Phase spectrum
    - 3D surface plot of magnitude
    - Filter mask visualization (if provided)
    
    Args:
        F_shifted: Shifted frequency domain representation
        filter_mask: Optional filter mask for visualization
        title: Title for the visualization
        
    Returns:
        dict with filepath to saved visualization
    """
    try:
        # Calculate magnitude and phase
        magnitude = np.log(1 + np.abs(F_shifted))
        phase = np.angle(F_shifted)
        
        # Create figure with 2x2 subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(title, fontsize=16)
        
        # 1. Magnitude spectrum (log scale)
        im1 = axes[0, 0].imshow(magnitude, cmap='hot', aspect='auto')
        axes[0, 0].set_title('Magnitude Spectrum (Log Scale)')
        axes[0, 0].set_xlabel('Frequency (v)')
        axes[0, 0].set_ylabel('Frequency (u)')
        plt.colorbar(im1, ax=axes[0, 0])
        
        # 2. Phase spectrum
        im2 = axes[0, 1].imshow(phase, cmap='hsv', aspect='auto')
        axes[0, 1].set_title('Phase Spectrum')
        axes[0, 1].set_xlabel('Frequency (v)')
        axes[0, 1].set_ylabel('Frequency (u)')
        plt.colorbar(im2, ax=axes[0, 1])
        
        # 3. 3D surface plot of magnitude
        rows, cols = magnitude.shape
        u = np.arange(rows)
        v = np.arange(cols)
        U, V = np.meshgrid(v, u)
        
        # Downsample for better visualization
        step = max(1, min(rows, cols) // 50)
        U_sub = U[::step, ::step]
        V_sub = V[::step, ::step]
        magnitude_sub = magnitude[::step, ::step]
        
        surf = axes[1, 0].plot_surface(U_sub, V_sub, magnitude_sub, 
                                     cmap='hot', alpha=0.8)
        axes[1, 0].set_title('3D Magnitude Surface')
        axes[1, 0].set_xlabel('Frequency (v)')
        axes[1, 0].set_ylabel('Frequency (u)')
        axes[1, 0].set_zlabel('Magnitude')
        
        # 4. Filter mask visualization or frequency center
        if filter_mask is not None:
            im4 = axes[1, 1].imshow(filter_mask, cmap='gray', aspect='auto')
            axes[1, 1].set_title('Filter Mask')
            axes[1, 1].set_xlabel('Frequency (v)')
            axes[1, 1].set_ylabel('Frequency (u)')
            plt.colorbar(im4, ax=axes[1, 1])
        else:
            # Show frequency center
            center_u, center_v = rows // 2, cols // 2
            axes[1, 1].imshow(magnitude, cmap='hot', aspect='auto')
            axes[1, 1].plot(center_v, center_u, 'bo', markersize=10, label='DC Component')
            axes[1, 1].set_title('Frequency Center')
            axes[1, 1].set_xlabel('Frequency (v)')
            axes[1, 1].set_ylabel('Frequency (u)')
            axes[1, 1].legend()
        
        plt.tight_layout()
        
        # Save visualization
        output_dir = "satellite-image-processor/backend/uploads"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"frequency_analysis_{np.random.randint(1000, 9999)}.png"
        filepath = os.path.join(output_dir, filename)
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return {
            'success': True,
            'visualization_path': filepath,
            'magnitude_spectrum': magnitude.tolist(),
            'phase_spectrum': phase.tolist(),
            'frequency_center': (rows // 2, cols // 2)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Legacy class-based interface for backward compatibility
class FrequencyProcessor:
    """Legacy class-based interface for backward compatibility"""
    
    def __init__(self):
        self.supported_operations = [
            'compute_dft_2d',
            'ideal_lowpass_filter',
            'ideal_highpass_filter',
            'butterworth_lowpass_filter',
            'butterworth_highpass_filter',
            'gaussian_lowpass_filter',
            'gaussian_highpass_filter',
            'visualize_frequency_domain'
        ]
    
    def process(self, data):
        """Main processing function for legacy interface"""
        operation = data.get('operation')
        
        if operation not in self.supported_operations:
            return {'error': f'Unsupported operation: {operation}'}
        
        try:
            image = data.get('image')
            if image is None and operation != 'visualize_frequency_domain':
                return {'error': 'No image provided'}
            
            if operation == 'compute_dft_2d':
                return compute_dft_2d(image)
            
            elif operation == 'ideal_lowpass_filter':
                cutoff = data.get('cutoff_frequency', 30)
                return ideal_lowpass_filter(image, cutoff)
            
            elif operation == 'ideal_highpass_filter':
                cutoff = data.get('cutoff_frequency', 30)
                return ideal_highpass_filter(image, cutoff)
            
            elif operation == 'butterworth_lowpass_filter':
                cutoff = data.get('cutoff_frequency', 30)
                order = data.get('order', 2)
                return butterworth_lowpass_filter(image, cutoff, order)
            
            elif operation == 'butterworth_highpass_filter':
                cutoff = data.get('cutoff_frequency', 30)
                order = data.get('order', 2)
                return butterworth_highpass_filter(image, cutoff, order)
            
            elif operation == 'gaussian_lowpass_filter':
                cutoff = data.get('cutoff_frequency', 30)
                return gaussian_lowpass_filter(image, cutoff)
            
            elif operation == 'gaussian_highpass_filter':
                cutoff = data.get('cutoff_frequency', 30)
                return gaussian_highpass_filter(image, cutoff)
            
            elif operation == 'visualize_frequency_domain':
                F_shifted = data.get('F_shifted')
                filter_mask = data.get('filter_mask')
                title = data.get('title', 'Frequency Domain Analysis')
                if F_shifted is None:
                    return {'error': 'No F_shifted provided'}
                return visualize_frequency_domain(F_shifted, filter_mask, title)
            
            else:
                return {'error': 'Operation not implemented'}
                
        except Exception as e:
            return {'error': f'Processing failed: {str(e)}'}