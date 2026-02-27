"""
Module 4: Image Restoration
Based on Chapter 5-6 of "Digital Image Processing" by Gonzalez & Woods

This module implements degradation modeling and restoration techniques:
- Noise modeling and addition
- Periodic noise removal with notch filtering
- Inverse filtering and Wiener filtering
- Constrained least squares restoration
- Motion blur and atmospheric turbulence modeling

Critical for faculty presentation: Shows degradation model g = h * f + n
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import os
from typing import Dict, List, Tuple, Union
import math
from scipy import ndimage
from scipy.signal import convolve2d


def _prepare_image(image: np.ndarray) -> np.ndarray:
    """
    Convert image to grayscale and ensure proper format.
    
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
    
    # Convert to float32 for processing
    gray_float = gray.astype(np.float32)
    
    return gray_float


def _normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normalize image to [0, 255] range and convert to uint8.
    
    Args:
        image: Input image
        
    Returns:
        Normalized image as uint8
    """
    # Normalize to [0, 255]
    normalized = np.clip(image, 0, 255)
    return normalized.astype(np.uint8)


def add_noise(image: np.ndarray, noise_type: str, params: Dict) -> Dict:
    """
    Add various types of noise to image.
    
    Args:
        image: Input image as numpy array
        noise_type: 'gaussian', 'salt_pepper', 'uniform', or 'periodic'
        params: Dictionary containing noise parameters
        
    Returns:
        dict with noisy image and noise parameters
    """
    try:
        # Prepare image
        gray = _prepare_image(image)
        rows, cols = gray.shape
        
        if noise_type == 'gaussian':
            # Gaussian noise: mean, variance
            mean = params.get('mean', 0)
            variance = params.get('variance', 0.01)
            std = np.sqrt(variance)
            
            noise = np.random.normal(mean, std, gray.shape)
            noisy_image = gray + noise * 255  # Scale to image range
            
        elif noise_type == 'salt_pepper':
            # Salt and pepper noise: probability
            prob = params.get('probability', 0.05)
            
            noisy_image = gray.copy()
            # Salt noise (white pixels)
            salt_mask = np.random.random(gray.shape) < prob / 2
            noisy_image[salt_mask] = 255
            
            # Pepper noise (black pixels)
            pepper_mask = np.random.random(gray.shape) < prob / 2
            noisy_image[pepper_mask] = 0
            
        elif noise_type == 'uniform':
            # Uniform noise: low, high
            low = params.get('low', -0.1)
            high = params.get('high', 0.1)
            
            noise = np.random.uniform(low, high, gray.shape)
            noisy_image = gray + noise * 255
            
        elif noise_type == 'periodic':
            # Periodic noise: frequency components
            frequencies = params.get('frequencies', [(10, 10), (20, 20)])
            amplitudes = params.get('amplitudes', [0.1, 0.05])
            
            noisy_image = gray.copy()
            u = np.arange(rows)
            v = np.arange(cols)
            U, V = np.meshgrid(v, u)
            
            for freq, amp in zip(frequencies, amplitudes):
                fu, fv = freq
                periodic_noise = amp * np.sin(2 * np.pi * (fu * U / rows + fv * V / cols))
                noisy_image += periodic_noise * 255
                
        else:
            raise ValueError(f"Unsupported noise type: {noise_type}")
        
        # Normalize output
        noisy_image = _normalize_image(noisy_image)
        
        # Calculate noise statistics
        noise_actual = noisy_image.astype(np.float32) - gray
        noise_stats = {
            'mean': float(np.mean(noise_actual)),
            'std': float(np.std(noise_actual)),
            'min': float(np.min(noise_actual)),
            'max': float(np.max(noise_actual))
        }
        
        return {
            'success': True,
            'noisy_image': noisy_image,
            'original_image': gray,
            'noise_type': noise_type,
            'noise_parameters': params,
            'noise_statistics': noise_stats,
            'snr_db': 20 * np.log10(np.std(gray) / np.std(noise_actual)) if np.std(noise_actual) > 0 else float('inf')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# def periodic_noise_removal(image: np.ndarray, frequencies: List[Tuple[int, int]]) -> Dict:
#     """
#     Remove periodic noise using notch filtering.
    
#     Steps:
#     1. Compute FFT of noisy image
#     2. Identify periodic noise frequencies (peaks in spectrum)
#     3. Create notch filter to remove specific frequencies
#     4. Apply filter and inverse FFT
    
#     Args:
#         image: Input noisy image
#         frequencies: List of (u, v) frequency pairs to remove
        
#     Returns:
#         dict with restored image and frequency spectrum before/after
#     """
#     try:
#         # Prepare image
#         gray = _prepare_image(image)
#         rows, cols = gray.shape
        
#         # Step 1: Compute FFT of noisy image
#         F = np.fft.fft2(gray)
#         F_shifted = np.fft.fftshift(F)
        
#         # Step 2: Create notch filter
#         notch_filter = np.ones((rows, cols), dtype=np.float32)
        
#         # Step 3: Create notch filter to remove specific frequencies
#         for fu, fv in frequencies:
#             # Convert to frequency domain coordinates
#             center_u, center_v = rows // 2, cols // 2
            
#             # Create notch around each frequency
#             notch_size = 3  # Size of notch filter
#             for du in range(-notch_size, notch_size + 1):
#                 for dv in range(-notch_size, notch_size + 1):
#                     u_idx = center_u + fu + du
#                     v_idx = center_v + fv + dv
                    
#                     # Handle wraparound
#                     u_idx = u_idx % rows
#                     v_idx = v_idx % cols
                    
#                     if 0 <= u_idx < rows and 0 <= v_idx < cols:
#                         notch_filter[u_idx, v_idx] = 0
            
#             # Also remove symmetric frequencies
#             for du in range(-notch_size, notch_size + 1):
#                 for dv in range(-notch_size, notch_size + 1):
#                     u_idx = center_u - fu + du
#                     v_idx = center_v - fv + dv
                    
#                     # Handle wraparound
#                     u_idx = u_idx % rows
#                     v_idx = v_idx % cols
                    
#                     if 0 <= u_idx < rows and 0 <= v_idx < cols:
#                         notch_filter[u_idx, v_idx] = 0
        
#         # Step 4: Apply notch filter
#         F_filtered = F_shifted * notch_filter
        
#         # Inverse FFT
#         F_unshifted = np.fft.ifftshift(F_filtered)
#         restored_image = np.fft.ifft2(F_unshifted)
#         restored_image = np.real(restored_image)
#         restored_image = _normalize_image(restored_image)
        
#         # Calculate spectrums for visualization
#         original_spectrum = np.log(1 + np.abs(F_shifted))
#         filtered_spectrum = np.log(1 + np.abs(F_filtered))
        
#         return {
#             'success': True,
#             'restored_image': restored_image,
#             'original_image': gray,
#             'notch_filter': notch_filter,
#             'original_spectrum': original_spectrum,
#             'filtered_spectrum': filtered_spectrum,
#             'frequencies_removed': frequencies,
#             'method': 'notch_filtering'
#         }
        
#     except Exception as e:
#         return {
#             'success': False,
#             'error': str(e)
#         }
def periodic_noise_removal(image: np.ndarray, frequencies: List[Tuple[int, int]]) -> Dict:
    """
    Remove periodic noise using notch filtering.
    
    Steps:
    1. Compute FFT of noisy image
    2. Identify periodic noise frequencies (peaks in spectrum)
    3. Create notch filter to remove specific frequencies
    4. Apply filter and inverse FFT
    
    Args:
        image: Input noisy image
        frequencies: List of (u, v) frequency pairs to remove
        
    Returns:
        dict with restored image and frequency spectrum before/after
    """
    try:
        # Prepare image
        gray = _prepare_image(image)
        rows, cols = gray.shape
        
        # Step 1: Compute FFT of noisy image
        F = np.fft.fft2(gray)
        F_shifted = np.fft.fftshift(F)
        
        # Step 2: Create notch filter
        notch_filter = np.ones((rows, cols), dtype=np.float32)
        
        # Step 3: Create notch filter to remove specific frequencies
        for fu, fv in frequencies:
            # Convert to frequency domain coordinates
            center_u, center_v = rows // 2, cols // 2
            
            # Create notch around each frequency
            notch_size = 3  # Size of notch filter
            for du in range(-notch_size, notch_size + 1):
                for dv in range(-notch_size, notch_size + 1):
                    u_idx = center_u + fu + du
                    v_idx = center_v + fv + dv
                    
                    # Handle wraparound
                    u_idx = u_idx % rows
                    v_idx = v_idx % cols
                    
                    if 0 <= u_idx < rows and 0 <= v_idx < cols:
                        notch_filter[u_idx, v_idx] = 0
            
            # Also remove symmetric frequencies
            for du in range(-notch_size, notch_size + 1):
                for dv in range(-notch_size, notch_size + 1):
                    u_idx = center_u - fu + du
                    v_idx = center_v - fv + dv
                    
                    # Handle wraparound
                    u_idx = u_idx % rows
                    v_idx = v_idx % cols
                    
                    if 0 <= u_idx < rows and 0 <= v_idx < cols:
                        notch_filter[u_idx, v_idx] = 0
        
        # Step 4: Apply notch filter
        F_filtered = F_shifted * notch_filter
        
        # Inverse FFT
        F_unshifted = np.fft.ifftshift(F_filtered)
        restored_image = np.fft.ifft2(F_unshifted)
        restored_image = np.real(restored_image)
        restored_image = _normalize_image(restored_image)
        
        # Calculate spectrums for visualization
        original_spectrum = np.log(1 + np.abs(F_shifted))
        filtered_spectrum = np.log(1 + np.abs(F_filtered))
        
        # Ensure original_image is also uint8
        original_uint8 = _normalize_image(gray)
        
        return {
            'success': True,
            'restored_image': restored_image,
            'original_image': original_uint8,
            'notch_filter': notch_filter,
            'original_spectrum': original_spectrum,
            'filtered_spectrum': filtered_spectrum,
            'frequencies_removed': frequencies,
            'method': 'notch_filtering'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# def inverse_filtering(image: np.ndarray, degradation_kernel: np.ndarray, epsilon: float = 1e-10) -> Dict:
#     """
#     Apply inverse filtering for image restoration.
    
#     Degradation model: g(x,y) = h(x,y) * f(x,y) + n(x,y)
#     In frequency domain: G(u,v) = H(u,v) * F(u,v) + N(u,v)
#     Restoration: F_hat(u,v) = G(u,v) / (H(u,v) + epsilon)
    
#     Args:
#         image: Degraded image
#         degradation_kernel: Point Spread Function (PSF)
#         epsilon: Small constant to prevent division by zero
        
#     Returns:
#         dict with restored image and degradation model visualization
#     """
#     try:
#         # Prepare image
#         gray = _prepare_image(image)
#         rows, cols = gray.shape
        
#         # Pad kernel to image size
#         kernel_padded = np.zeros((rows, cols), dtype=np.float32)
#         k_rows, k_cols = degradation_kernel.shape
        
#         # Center the kernel
#         start_row = (rows - k_rows) // 2
#         start_col = (cols - k_cols) // 2
#         kernel_padded[start_row:start_row + k_rows, start_col:start_col + k_cols] = degradation_kernel
        
#         # Compute FFTs
#         G = np.fft.fft2(gray)
#         H = np.fft.fft2(kernel_padded)
        
#         # Apply inverse filter
#         # F_hat(u,v) = G(u,v) / (H(u,v) + epsilon)
#         H_stable = H + epsilon
#         F_hat = G / H_stable
        
#         # Inverse FFT
#         restored_image = np.fft.ifft2(F_hat)
#         restored_image = np.real(restored_image)
#         restored_image = _normalize_image(restored_image)
        
#         # Calculate degradation model visualization
#         degradation_model = {
#             'equation': 'g(x,y) = h(x,y) * f(x,y) + n(x,y)',
#             'frequency_domain': 'G(u,v) = H(u,v) * F(u,v) + N(u,v)',
#             'restoration_formula': 'F_hat(u,v) = G(u,v) / (H(u,v) + epsilon)',
#             'epsilon_used': epsilon
#         }
        
#         # Calculate restoration quality metrics
#         mse = np.mean((gray.astype(np.float32) - restored_image.astype(np.float32))**2)
#         psnr = 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')
        
#         return {
#             'success': True,
#             'restored_image': restored_image,
#             'degraded_image': gray,
#             'degradation_kernel': degradation_kernel,
#             'method': 'inverse_filtering',
#             'parameters': {'epsilon': epsilon},
#             'degradation_model': degradation_model,
#             'restoration_metrics': {
#                 'mse': float(mse),
#                 'psnr': float(psnr)
#             },
#             'frequency_response': np.abs(H)
#         }
        
#     except Exception as e:
#         return {
#             'success': False,
#             'error': str(e)
#         }


# def wiener_filtering(image: np.ndarray, degradation_kernel: np.ndarray, noise_variance: float) -> Dict:
#     """
#     Apply Wiener filter for optimal restoration.
    
#     EXACT formula from textbook:
#     F_hat(u,v) = [H*(u,v) / (|H(u,v)|^2 + K)] * G(u,v)
#     where K = S_n(u,v) / S_f(u,v) (noise-to-signal power ratio)
    
#     Args:
#         image: Degraded image
#         degradation_kernel: Point Spread Function (PSF)
#         noise_variance: Noise variance (S_n)
        
#     Returns:
#         dict with restored image, frequency domain visualization, and K value
#     """
#     try:
#         # Prepare image
#         gray = _prepare_image(image)
#         rows, cols = gray.shape
        
#         # Pad kernel to image size
#         kernel_padded = np.zeros((rows, cols), dtype=np.float32)
#         k_rows, k_cols = degradation_kernel.shape
        
#         # Center the kernel
#         start_row = (rows - k_rows) // 2
#         start_col = (cols - k_cols) // 2
#         kernel_padded[start_row:start_row + k_rows, start_col:start_col + k_cols] = degradation_kernel
        
#         # Compute FFTs
#         G = np.fft.fft2(gray)
#         H = np.fft.fft2(kernel_padded)
        
#         # Calculate power spectral densities
#         # Estimate signal power from image
#         signal_power = np.var(gray)
        
#         # Calculate K = S_n / S_f
#         K = noise_variance / signal_power
        
#         # Apply Wiener filter formula
#         # F_hat(u,v) = [H*(u,v) / (|H(u,v)|^2 + K)] * G(u,v)
#         H_conj = np.conj(H)
#         H_magnitude_sq = np.abs(H)**2
        
#         wiener_filter = H_conj / (H_magnitude_sq + K)
#         F_hat = wiener_filter * G
        
#         # Inverse FFT
#         restored_image = np.fft.ifft2(F_hat)
#         restored_image = np.real(restored_image)
#         restored_image = _normalize_image(restored_image)
        
#         # Calculate restoration quality metrics
#         mse = np.mean((gray.astype(np.float32) - restored_image.astype(np.float32))**2)
#         psnr = 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')
        
#         return {
#             'success': True,
#             'restored_image': restored_image,
#             'degraded_image': gray,
#             'degradation_kernel': degradation_kernel,
#             'method': 'wiener_filtering',
#             'parameters': {'noise_variance': noise_variance, 'K': K},
#             'wiener_formula': 'F_hat(u,v) = [H*(u,v) / (|H(u,v)|^2 + K)] * G(u,v)',
#             'K_value': K,
#             'restoration_metrics': {
#                 'mse': float(mse),
#                 'psnr': float(psnr),
#                 'signal_power': float(signal_power),
#                 'noise_power': float(noise_variance)
#             },
#             'frequency_response': np.abs(wiener_filter)
#         }
        
#     except Exception as e:
#         return {
#             'success': False,
#             'error': str(e)
#         }

def inverse_filtering(image: np.ndarray, degradation_kernel: np.ndarray, epsilon: float = 1e-10) -> Dict:
    """
    Apply inverse filtering for image restoration.
    
    Degradation model: g(x,y) = h(x,y) * f(x,y) + n(x,y)
    In frequency domain: G(u,v) = H(u,v) * F(u,v) + N(u,v)
    Restoration: F_hat(u,v) = G(u,v) / (H(u,v) + epsilon)
    
    Args:
        image: Degraded image
        degradation_kernel: Point Spread Function (PSF)
        epsilon: Small constant to prevent division by zero
        
    Returns:
        dict with restored image and degradation model visualization
    """
    try:
        # Added By Shree 25/25 - Start: Fix FFT shifting to prevent quadrant swapping
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Normalize to float
        img_float = gray.astype(np.float64) / 255.0
        rows, cols = img_float.shape
        
        # Create motion blur PSF if kernel not provided or use provided kernel
        if degradation_kernel is None or degradation_kernel.size == 0:
            psf = motion_blur_kernel(10, 0)  # Use motion_blur_kernel function
        else:
            psf = degradation_kernel.astype(np.float64)
            if psf.sum() > 0:
                psf = psf / psf.sum()
        
        # Pad the PSF to match image size at origin
        psf_padded = np.zeros((rows, cols), dtype=np.float64)
        k_rows, k_cols = psf.shape
        # Place kernel at origin (top-left) for proper FFT shifting
        psf_padded[:k_rows, :k_cols] = psf
        
        # Apply FFT to both image and PSF
        img_fft = np.fft.fft2(img_float)
        psf_fft = np.fft.fft2(psf_padded)
        
        # Apply fftshift to center zero-frequency component
        img_fft_shifted = np.fft.fftshift(img_fft)
        psf_fft_shifted = np.fft.fftshift(psf_fft)
        
        # Inverse filtering with regularization
        # Add epsilon to avoid division by zero
        psf_fft_reg = psf_fft_shifted + epsilon
        
        # Perform inverse filtering in frequency domain
        restored_fft_shifted = img_fft_shifted / psf_fft_reg
        
        # Apply ifftshift before inverse FFT
        restored_fft = np.fft.ifftshift(restored_fft_shifted)
        
        # Apply IFFT to get restored image
        restored = np.real(np.fft.ifft2(restored_fft))
        # Added By Shree 25/25 - End
        
        # Clip values and normalize
        restored = np.clip(restored, 0, 1)
        restored_gray = (restored * 255).astype(np.uint8)
        
        # Added by shree 24/10 - Start: Fix shape mismatch for color images
        # Calculate restoration quality metrics on grayscale before converting
        mse = np.mean((gray.astype(np.float32) - restored_gray.astype(np.float32))**2)
        psnr = 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')
        
        # Convert back to color if original was color
        if len(image.shape) == 3:
            restored_output = cv2.cvtColor(restored_gray, cv2.COLOR_GRAY2BGR)
            degraded_uint8 = cv2.cvtColor(gray.astype(np.uint8), cv2.COLOR_GRAY2BGR)
        else:
            restored_output = restored_gray
            degraded_uint8 = gray.astype(np.uint8)
        # Added by shree 24/10 - End
        
        # Calculate degradation model visualization
        degradation_model = {
            'equation': 'g(x,y) = h(x,y) * f(x,y) + n(x,y)',
            'frequency_domain': 'G(u,v) = H(u,v) * F(u,v) + N(u,v)',
            'restoration_formula': 'F_hat(u,v) = G(u,v) / (H(u,v) + epsilon)',
            'epsilon_used': epsilon
        }
        
        return {
            'success': True,
            'restored_image': restored_output,
            'degraded_image': degraded_uint8,
            'original_image': degraded_uint8,
            'degradation_kernel': psf,
            'method': 'inverse_filtering',
            'parameters': {'epsilon': epsilon},
            'degradation_model': degradation_model,
            'restoration_metrics': {
                'mse': float(mse),
                'psnr': float(psnr)
            },
            'frequency_response': np.abs(psf_fft_shifted)  # Added By Shree 25/25: Use shifted version
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
# Added by shree 24/10 - End


def wiener_filtering(image: np.ndarray, degradation_kernel: np.ndarray, noise_variance: float) -> Dict:
    """
    Apply Wiener filter for optimal restoration.
    
    EXACT formula from textbook:
    F_hat(u,v) = [H*(u,v) / (|H(u,v)|^2 + K)] * G(u,v)
    where K = S_n(u,v) / S_f(u,v) (noise-to-signal power ratio)
    
    Args:
        image: Degraded image
        degradation_kernel: Point Spread Function (PSF)
        noise_variance: Noise variance (S_n)
        
    Returns:
        dict with restored image, frequency domain visualization, and K value
    """
    try:
        # Prepare image
        gray = _prepare_image(image)
        rows, cols = gray.shape
        
        # Added By Shree 25/25 - Start: Pad kernel at origin for proper FFT shifting
        # Place kernel at top-left (origin) for proper FFT shifting workflow
        kernel_padded = np.zeros((rows, cols), dtype=np.float32)
        k_rows, k_cols = degradation_kernel.shape
        kernel_padded[:k_rows, :k_cols] = degradation_kernel
        # Added By Shree 25/25 - End
        
        # Added By Shree 25/25 - Start: Fix FFT shifting to prevent quadrant swapping
        # Compute FFTs
        G = np.fft.fft2(gray)
        H = np.fft.fft2(kernel_padded)
        
        # Apply fftshift to center zero-frequency component
        G_shifted = np.fft.fftshift(G)
        H_shifted = np.fft.fftshift(H)
        
        # Calculate power spectral densities
        # Estimate signal power from image
        signal_power = np.var(gray)
        
        # Calculate K = S_n / S_f
        K = noise_variance / signal_power
        
        # Apply Wiener filter formula
        # F_hat(u,v) = [H*(u,v) / (|H(u,v)|^2 + K)] * G(u,v)
        H_conj = np.conj(H_shifted)
        H_magnitude_sq = np.abs(H_shifted)**2
        
        wiener_filter = H_conj / (H_magnitude_sq + K)
        F_hat_shifted = wiener_filter * G_shifted
        
        # Apply ifftshift before inverse FFT
        F_hat = np.fft.ifftshift(F_hat_shifted)
        
        # Inverse FFT
        restored_image = np.fft.ifft2(F_hat)
        # Added By Shree 25/25 - End
        restored_image = np.real(restored_image)
        restored_image = _normalize_image(restored_image)
        
        # Calculate restoration quality metrics
        mse = np.mean((gray.astype(np.float32) - restored_image.astype(np.float32))**2)
        psnr = 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')
        
        # Ensure degraded_image is uint8
        degraded_uint8 = _normalize_image(gray)
        
        return {
            'success': True,
            'restored_image': restored_image,
            'degraded_image': degraded_uint8,
            'original_image': degraded_uint8,
            'degradation_kernel': degradation_kernel,
            'method': 'wiener_filtering',
            'parameters': {'noise_variance': noise_variance, 'K': K},
            'wiener_formula': 'F_hat(u,v) = [H*(u,v) / (|H(u,v)|^2 + K)] * G(u,v)',
            'K_value': K,
            'restoration_metrics': {
                'mse': float(mse),
                'psnr': float(psnr),
                'signal_power': float(signal_power),
                'noise_power': float(noise_variance)
            },
            'frequency_response': np.abs(wiener_filter)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def constrained_least_squares_filtering(image: np.ndarray, degradation_kernel: np.ndarray, gamma: float) -> Dict:
    """
    Apply constrained least squares restoration.
    
    Minimize: ||g - Hf||^2 + gamma * ||Cf||^2
    C is Laplacian operator
    In frequency domain: F_hat = [H* / (|H|^2 + gamma*|C|^2)] * G
    
    Args:
        image: Degraded image
        degradation_kernel: Point Spread Function (PSF)
        gamma: Regularization parameter
        
    Returns:
        dict with restored image and cost function value
    """
    try:
        # Prepare image
        gray = _prepare_image(image)
        rows, cols = gray.shape
        
        # Pad kernel to image size
        kernel_padded = np.zeros((rows, cols), dtype=np.float32)
        k_rows, k_cols = degradation_kernel.shape
        
        # Center the kernel
        start_row = (rows - k_rows) // 2
        start_col = (cols - k_cols) // 2
        kernel_padded[start_row:start_row + k_rows, start_col:start_col + k_cols] = degradation_kernel
        
        # Create Laplacian operator C
        laplacian_kernel = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]], dtype=np.float32)
        C_padded = np.zeros((rows, cols), dtype=np.float32)
        
        # Center the Laplacian kernel
        c_rows, c_cols = laplacian_kernel.shape
        start_row_c = (rows - c_rows) // 2
        start_col_c = (cols - c_cols) // 2
        C_padded[start_row_c:start_row_c + c_rows, start_col_c:start_col_c + c_cols] = laplacian_kernel
        
        # Compute FFTs
        G = np.fft.fft2(gray)
        H = np.fft.fft2(kernel_padded)
        C = np.fft.fft2(C_padded)
        
        # Apply constrained least squares formula
        # F_hat = [H* / (|H|^2 + gamma*|C|^2)] * G
        H_conj = np.conj(H)
        H_magnitude_sq = np.abs(H)**2
        C_magnitude_sq = np.abs(C)**2
        
        cls_filter = H_conj / (H_magnitude_sq + gamma * C_magnitude_sq)
        F_hat = cls_filter * G
        
        # Inverse FFT
        restored_image = np.fft.ifft2(F_hat)
        restored_image = np.real(restored_image)
        restored_image = _normalize_image(restored_image)
        
        # Calculate cost function value
        # Cost = ||g - Hf||^2 + gamma * ||Cf||^2
        Hf = np.fft.ifft2(H * np.fft.fft2(restored_image))
        Hf = np.real(Hf)
        Cf = np.fft.ifft2(C * np.fft.fft2(restored_image))
        Cf = np.real(Cf)
        
        data_fidelity = np.sum((gray - Hf)**2)
        regularization = np.sum(Cf**2)
        cost_function = data_fidelity + gamma * regularization
        
        # Calculate restoration quality metrics
        mse = np.mean((gray.astype(np.float32) - restored_image.astype(np.float32))**2)
        psnr = 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')
        
        return {
            'success': True,
            'restored_image': restored_image,
            'degraded_image': gray,
            'degradation_kernel': degradation_kernel,
            'method': 'constrained_least_squares',
            'parameters': {'gamma': gamma},
            'cost_function_value': float(cost_function),
            'cost_components': {
                'data_fidelity': float(data_fidelity),
                'regularization': float(regularization)
            },
            'restoration_metrics': {
                'mse': float(mse),
                'psnr': float(psnr)
            },
            'frequency_response': np.abs(cls_filter)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def motion_blur_kernel(length: int, angle: float) -> np.ndarray:
    """
    Create Point Spread Function (PSF) for motion blur.
    
    Args:
        length: Blur length in pixels
        angle: Direction of motion in degrees
        
    Returns:
        PSF kernel as numpy array
    """
    try:
        # Convert angle to radians
        angle_rad = np.radians(angle)
        
        # Calculate kernel dimensions
        kernel_size = max(length, 15)  # Minimum kernel size
        
        # Create motion blur kernel
        kernel = np.zeros((kernel_size, kernel_size), dtype=np.float32)
        
        # Calculate motion direction
        dx = length * np.cos(angle_rad)
        dy = length * np.sin(angle_rad)
        
        # Create line kernel
        center = kernel_size // 2
        steps = max(abs(int(dx)), abs(int(dy)), 1)
        
        for i in range(steps + 1):
            x = int(center + dx * i / steps)
            y = int(center + dy * i / steps)
            
            if 0 <= x < kernel_size and 0 <= y < kernel_size:
                kernel[y, x] = 1.0
        
        # Normalize kernel
        kernel = kernel / np.sum(kernel)
        
        return kernel
        
    except Exception as e:
        # Return default kernel on error
        kernel = np.zeros((15, 15), dtype=np.float32)
        kernel[7, :] = 1.0 / 15
        return kernel


def atmospheric_turbulence_degradation(image: np.ndarray, k: float = 0.001) -> Dict:
    """
    Model atmospheric turbulence degradation.
    
    H(u,v) = exp(-k * (u^2 + v^2)^(5/6))
    Apply degradation to image
    
    Args:
        image: Input image
        k: Turbulence parameter (default: 0.001)
        
    Returns:
        dict with degraded image and H kernel
    """
    try:
        # Prepare image
        gray = _prepare_image(image)
        rows, cols = gray.shape
        
        # Create frequency coordinates
        u = np.arange(rows)
        v = np.arange(cols)
        U, V = np.meshgrid(v, u)
        
        # Shift to center
        center_u, center_v = rows // 2, cols // 2
        U_shifted = U - center_v
        V_shifted = V - center_u
        
        # Calculate distance from center
        D = np.sqrt(U_shifted**2 + V_shifted**2)
        
        # Create atmospheric turbulence transfer function
        # H(u,v) = exp(-k * (u^2 + v^2)^(5/6))
        H = np.exp(-k * (D**2)**(5/6))
        
        # Apply degradation in frequency domain
        F = np.fft.fft2(gray)
        F_shifted = np.fft.fftshift(F)
        
        # Apply transfer function
        G_shifted = F_shifted * H
        
        # Inverse FFT
        G = np.fft.ifftshift(G_shifted)
        degraded_image = np.fft.ifft2(G)
        degraded_image = np.real(degraded_image)
        degraded_image = _normalize_image(degraded_image)
        
        # Calculate degradation metrics
        degradation_strength = 1 - np.mean(H)
        
        return {
            'success': True,
            'degraded_image': degraded_image,
            'original_image': gray,
            'transfer_function': H,
            'parameters': {'k': k},
            'degradation_strength': float(degradation_strength),
            'method': 'atmospheric_turbulence',
            'formula': 'H(u,v) = exp(-k * (u^2 + v^2)^(5/6))'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def visualize_degradation_model(original_image: np.ndarray, degraded_image: np.ndarray, 
                               degradation_kernel: np.ndarray, method: str) -> Dict:
    """
    Create visualization of degradation model for faculty presentation.
    
    Shows: g = h * f + n equation and frequency domain visualization
    
    Args:
        original_image: Original clean image
        degraded_image: Degraded image
        degradation_kernel: PSF kernel
        method: Restoration method used
        
    Returns:
        dict with filepath to visualization
    """
    try:
        # Create figure with subplots
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle(f'Image Restoration: {method}', fontsize=16)
        
        # 1. Original image
        axes[0, 0].imshow(original_image, cmap='gray')
        axes[0, 0].set_title('Original Image f(x,y)')
        axes[0, 0].axis('off')
        
        # 2. Degradation kernel
        axes[0, 1].imshow(degradation_kernel, cmap='hot')
        axes[0, 1].set_title('PSF h(x,y)')
        axes[0, 1].axis('off')
        
        # 3. Degraded image
        axes[0, 2].imshow(degraded_image, cmap='gray')
        axes[0, 2].set_title('Degraded Image g(x,y)')
        axes[0, 2].axis('off')
        
        # 4. Degradation model equation
        axes[1, 0].text(0.1, 0.5, 'Degradation Model:\n\ng(x,y) = h(x,y) * f(x,y) + n(x,y)\n\nFrequency Domain:\nG(u,v) = H(u,v) * F(u,v) + N(u,v)', 
                       fontsize=12, verticalalignment='center')
        axes[1, 0].set_title('Mathematical Model')
        axes[1, 0].axis('off')
        
        # 5. Frequency domain visualization
        rows, cols = original_image.shape
        kernel_padded = np.zeros((rows, cols), dtype=np.float32)
        k_rows, k_cols = degradation_kernel.shape
        
        # Center the kernel
        start_row = (rows - k_rows) // 2
        start_col = (cols - k_cols) // 2
        kernel_padded[start_row:start_row + k_rows, start_col:start_col + k_cols] = degradation_kernel
        
        H = np.fft.fft2(kernel_padded)
        H_shifted = np.fft.fftshift(H)
        H_magnitude = np.log(1 + np.abs(H_shifted))
        
        im = axes[1, 1].imshow(H_magnitude, cmap='hot')
        axes[1, 1].set_title('|H(u,v)| in Frequency Domain')
        axes[1, 1].axis('off')
        plt.colorbar(im, ax=axes[1, 1])
        
        # 6. Restoration quality metrics
        mse = np.mean((original_image.astype(np.float32) - degraded_image.astype(np.float32))**2)
        psnr = 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')
        
        axes[1, 2].text(0.1, 0.5, f'Quality Metrics:\n\nMSE: {mse:.2f}\nPSNR: {psnr:.2f} dB\n\nMethod: {method}', 
                      fontsize=12, verticalalignment='center')
        axes[1, 2].set_title('Restoration Quality')
        axes[1, 2].axis('off')
        
        plt.tight_layout()
        
        # Save visualization
        output_dir = "satellite-image-processor/backend/uploads"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"restoration_analysis_{method}_{np.random.randint(1000, 9999)}.png"
        filepath = os.path.join(output_dir, filename)
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return {
            'success': True,
            'visualization_path': filepath,
            'method': method,
            'quality_metrics': {
                'mse': float(mse),
                'psnr': float(psnr)
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Legacy class-based interface for backward compatibility
class RestorationProcessor:
    """Legacy class-based interface for backward compatibility"""
    
    def __init__(self):
        self.supported_operations = [
            'add_noise',
            'periodic_noise_removal',
            'inverse_filtering',
            'wiener_filtering',
            'constrained_least_squares_filtering',
            'motion_blur_kernel',
            'atmospheric_turbulence_degradation',
            'visualize_degradation_model'
        ]
    
    def process(self, data):
        """Main processing function for legacy interface"""
        operation = data.get('operation')
        
        if operation not in self.supported_operations:
            return {'error': f'Unsupported operation: {operation}'}
        
        try:
            if operation == 'add_noise':
                image = data.get('image')
                noise_type = data.get('noise_type', 'gaussian')
                params = data.get('params', {})
                if image is None:
                    return {'error': 'No image provided'}
                return add_noise(image, noise_type, params)
            
            elif operation == 'periodic_noise_removal':
                image = data.get('image')
                frequencies = data.get('frequencies', [(10, 10)])
                if image is None:
                    return {'error': 'No image provided'}
                return periodic_noise_removal(image, frequencies)
            
            elif operation == 'inverse_filtering':
                image = data.get('image')
                kernel = data.get('degradation_kernel')
                epsilon = data.get('epsilon', 1e-10)
                if image is None or kernel is None:
                    return {'error': 'Image and degradation kernel required'}
                return inverse_filtering(image, kernel, epsilon)
            
            elif operation == 'wiener_filtering':
                image = data.get('image')
                kernel = data.get('degradation_kernel')
                noise_var = data.get('noise_variance', 0.01)
                if image is None or kernel is None:
                    return {'error': 'Image and degradation kernel required'}
                return wiener_filtering(image, kernel, noise_var)
            
            elif operation == 'constrained_least_squares_filtering':
                image = data.get('image')
                kernel = data.get('degradation_kernel')
                gamma = data.get('gamma', 0.1)
                if image is None or kernel is None:
                    return {'error': 'Image and degradation kernel required'}
                return constrained_least_squares_filtering(image, kernel, gamma)
            
            elif operation == 'motion_blur_kernel':
                length = data.get('length', 10)
                angle = data.get('angle', 0)
                return {'kernel': motion_blur_kernel(length, angle)}
            
            elif operation == 'atmospheric_turbulence_degradation':
                image = data.get('image')
                k = data.get('k', 0.001)
                if image is None:
                    return {'error': 'No image provided'}
                return atmospheric_turbulence_degradation(image, k)
            
            elif operation == 'visualize_degradation_model':
                original = data.get('original_image')
                degraded = data.get('degraded_image')
                kernel = data.get('degradation_kernel')
                method = data.get('method', 'unknown')
                if original is None or degraded is None or kernel is None:
                    return {'error': 'Original image, degraded image, and kernel required'}
                return visualize_degradation_model(original, degraded, kernel, method)
            
            else:
                return {'error': 'Operation not implemented'}
                
        except Exception as e:
            return {'error': f'Processing failed: {str(e)}'}