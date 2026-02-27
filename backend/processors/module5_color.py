"""
Module 5: Color Image Processing
Based on Chapter 6 of "Digital Image Processing" by Gonzalez & Woods

This module implements color space conversions and false-color processing:
- RGB to HSI conversion with exact textbook formulas
- Color image enhancement and processing
- False-color composites for satellite imagery
- NDVI calculation and multispectral processing

Critical for satellite image analysis and visualization.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import cm
import os
from typing import Dict, List, Tuple, Union
import math


def _prepare_color_image(image: np.ndarray) -> np.ndarray:
    """
    Ensure image is in proper format for color processing.
    
    Args:
        image: Input image (BGR, RGB, or grayscale)
        
    Returns:
        RGB image as float32 in range [0, 1]
    """
    if len(image.shape) == 2:
        # Convert grayscale to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif len(image.shape) == 3:
        if image.shape[2] == 3:
            # Assume BGR and convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            # Remove alpha channel if present
            rgb_image = image[:, :, :3]
    else:
        raise ValueError("Unsupported image format")
    
    # Convert to float32 and normalize to [0, 1]
    rgb_image = rgb_image.astype(np.float32) / 255.0
    
    return rgb_image


def _normalize_to_uint8(image: np.ndarray) -> np.ndarray:
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


def rgb_to_hsi(image: np.ndarray) -> Dict:
    """
    Convert RGB to HSI color space using exact textbook formulas.
    
    Formulas from textbook:
    I = (R + G + B) / 3
    S = 1 - 3/(R+G+B) * min(R,G,B)
    H = arccos( [(R-G)+(R-B)] / [2*sqrt((R-G)^2 + (R-B)(G-B))] )
    
    Args:
        image: Input RGB image
        
    Returns:
        dict with H, S, I channels separately
    """
    try:
        # Prepare image
        rgb = _prepare_color_image(image)
        rows, cols, channels = rgb.shape
        
        # Extract R, G, B channels
        R = rgb[:, :, 0]
        G = rgb[:, :, 1]
        B = rgb[:, :, 2]
        
        # Calculate Intensity: I = (R + G + B) / 3
        I = (R + G + B) / 3.0
        
        # Calculate Saturation: S = 1 - 3/(R+G+B) * min(R,G,B)
        # Handle division by zero
        sum_rgb = R + G + B
        sum_rgb = np.where(sum_rgb == 0, 1e-10, sum_rgb)  # Avoid division by zero
        min_rgb = np.minimum(np.minimum(R, G), B)
        S = 1 - (3.0 / sum_rgb) * min_rgb
        
        # Calculate Hue: H = arccos( [(R-G)+(R-B)] / [2*sqrt((R-G)^2 + (R-B)(G-B))] )
        numerator = (R - G) + (R - B)
        denominator = 2 * np.sqrt((R - G)**2 + (R - B) * (G - B))
        
        # Handle division by zero
        denominator = np.where(denominator == 0, 1e-10, denominator)
        
        # Calculate arccos, handling values outside [-1, 1] range
        cos_h = numerator / denominator
        cos_h = np.clip(cos_h, -1, 1)  # Ensure valid range for arccos
        H = np.arccos(cos_h)
        
        # Adjust H based on B > G condition
        H = np.where(B > G, 2 * np.pi - H, H)
        
        # Convert H to degrees for easier interpretation
        H_degrees = H * 180 / np.pi
        
        # Normalize HSI values
        H_normalized = H_degrees / 360.0  # Normalize to [0, 1]
        S_normalized = np.clip(S, 0, 1)
        I_normalized = np.clip(I, 0, 1)
        
        # Convert to uint8 for visualization
        H_uint8 = (H_normalized * 255).astype(np.uint8)
        S_uint8 = (S_normalized * 255).astype(np.uint8)
        I_uint8 = (I_normalized * 255).astype(np.uint8)
        
        return {
            'success': True,
            'processed_image': rgb,
            'color_space': 'HSI',
            'channels': {
                'h': H_uint8,
                's': S_uint8,
                'i': I_uint8
            },
            'hsi_normalized': {
                'h': H_normalized,
                's': S_normalized,
                'i': I_normalized
            },
            'formulas_used': {
                'intensity': 'I = (R + G + B) / 3',
                'saturation': 'S = 1 - 3/(R+G+B) * min(R,G,B)',
                'hue': 'H = arccos( [(R-G)+(R-B)] / [2*sqrt((R-G)^2 + (R-B)(G-B))] )'
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def hsi_to_rgb(h: np.ndarray, s: np.ndarray, i: np.ndarray) -> Dict:
    """
    Convert HSI back to RGB handling 3 sectors (RG, GB, BR).
    
    Args:
        h: Hue channel (0-255 or 0-1)
        s: Saturation channel (0-255 or 0-1)
        i: Intensity channel (0-255 or 0-1)
        
    Returns:
        dict with RGB image
    """
    try:
        # Normalize inputs to [0, 1]
        if h.max() > 1:
            H = h.astype(np.float32) / 255.0
        else:
            H = h.astype(np.float32)
            
        if s.max() > 1:
            S = s.astype(np.float32) / 255.0
        else:
            S = s.astype(np.float32)
            
        if i.max() > 1:
            I = i.astype(np.float32) / 255.0
        else:
            I = i.astype(np.float32)
        
        # Convert H from [0, 1] to [0, 2π]
        H = H * 2 * np.pi
        
        # Initialize RGB channels
        R = np.zeros_like(H)
        G = np.zeros_like(H)
        B = np.zeros_like(H)
        
        # Handle 3 sectors: RG (0 ≤ H < 2π/3), GB (2π/3 ≤ H < 4π/3), BR (4π/3 ≤ H < 2π)
        
        # Sector 1: RG (0 ≤ H < 2π/3)
        mask1 = (H >= 0) & (H < 2 * np.pi / 3)
        R[mask1] = I[mask1] * (1 + S[mask1] * np.cos(H[mask1]) / np.cos(np.pi / 3 - H[mask1]))
        B[mask1] = I[mask1] * (1 - S[mask1])
        G[mask1] = 3 * I[mask1] - (R[mask1] + B[mask1])
        
        # Sector 2: GB (2π/3 ≤ H < 4π/3)
        mask2 = (H >= 2 * np.pi / 3) & (H < 4 * np.pi / 3)
        H2 = H[mask2] - 2 * np.pi / 3
        G[mask2] = I[mask2] * (1 + S[mask2] * np.cos(H2) / np.cos(np.pi / 3 - H2))
        R[mask2] = I[mask2] * (1 - S[mask2])
        B[mask2] = 3 * I[mask2] - (R[mask2] + G[mask2])
        
        # Sector 3: BR (4π/3 ≤ H < 2π)
        mask3 = (H >= 4 * np.pi / 3) & (H < 2 * np.pi)
        H3 = H[mask3] - 4 * np.pi / 3
        B[mask3] = I[mask3] * (1 + S[mask3] * np.cos(H3) / np.cos(np.pi / 3 - H3))
        G[mask3] = I[mask3] * (1 - S[mask3])
        R[mask3] = 3 * I[mask3] - (G[mask3] + B[mask3])
        
        # Clip values to [0, 1]
        R = np.clip(R, 0, 1)
        G = np.clip(G, 0, 1)
        B = np.clip(B, 0, 1)
        
        # Combine into RGB image
        rgb_image = np.stack([R, G, B], axis=2)
        
        # Convert to uint8
        rgb_uint8 = (rgb_image * 255).astype(np.uint8)
        
        return {
            'success': True,
            'processed_image': rgb_uint8,
            'color_space': 'RGB',
            'channels': {
                'r': (R * 255).astype(np.uint8),
                'g': (G * 255).astype(np.uint8),
                'b': (B * 255).astype(np.uint8)
            },
            'conversion_method': 'HSI_to_RGB_3_sector'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def intensity_slicing(image: np.ndarray, levels: int) -> Dict:
    """
    Divide intensity into discrete levels and map each level to different color.
    
    Args:
        image: Input grayscale image
        levels: Number of intensity levels
        
    Returns:
        dict with color-mapped image and legend
    """
    try:
        # Prepare image
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Normalize to [0, 1]
        gray_normalized = gray.astype(np.float32) / 255.0
        
        # Create intensity levels
        level_boundaries = np.linspace(0, 1, levels + 1)
        
        # Create color map
        colors = plt.cm.jet(np.linspace(0, 1, levels))
        
        # Initialize color image
        color_image = np.zeros((gray.shape[0], gray.shape[1], 3), dtype=np.float32)
        
        # Map each intensity level to color
        for i in range(levels):
            mask = (gray_normalized >= level_boundaries[i]) & (gray_normalized < level_boundaries[i + 1])
            if i == levels - 1:  # Include maximum value in last level
                mask = (gray_normalized >= level_boundaries[i]) & (gray_normalized <= level_boundaries[i + 1])
            
            color_image[mask, 0] = colors[i, 0]  # R
            color_image[mask, 1] = colors[i, 1]  # G
            color_image[mask, 2] = colors[i, 2]  # B
        
        # Convert to uint8
        color_image_uint8 = (color_image * 255).astype(np.uint8)
        
        # Create legend
        legend_colors = (colors * 255).astype(np.uint8)
        
        return {
            'success': True,
            'processed_image': color_image_uint8,
            'original_image': gray,
            'levels': levels,
            'level_boundaries': level_boundaries.tolist(),
            'legend_colors': legend_colors.tolist(),
            'method': 'intensity_slicing'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def false_color_composite(image: np.ndarray, colormap: str = 'jet') -> Dict:
    """
    Convert grayscale to false color using various colormaps.
    
    Useful for satellite imagery analysis.
    
    Args:
        image: Input grayscale image
        colormap: 'jet', 'rainbow', 'hot', 'cool', 'terrain'
        
    Returns:
        dict with false color image
    """
    try:
        # Prepare image
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Normalize to [0, 1]
        gray_normalized = gray.astype(np.float32) / 255.0
        
        # Apply colormap
        colormap_map = {
            'jet': plt.cm.jet,
            'rainbow': plt.cm.rainbow,
            'hot': plt.cm.hot,
            'cool': plt.cm.cool,
            'terrain': plt.cm.terrain,
            'viridis': plt.cm.viridis,
            'plasma': plt.cm.plasma,
            'inferno': plt.cm.inferno
        }
        
        if colormap not in colormap_map:
            raise ValueError(f"Unsupported colormap: {colormap}")
        
        cmap = colormap_map[colormap]
        false_color = cmap(gray_normalized)
        
        # Extract RGB channels (remove alpha if present)
        if false_color.shape[2] == 4:
            false_color_rgb = false_color[:, :, :3]
        else:
            false_color_rgb = false_color
        
        # Convert to uint8
        false_color_uint8 = (false_color_rgb * 255).astype(np.uint8)
        
        return {
            'success': True,
            'processed_image': false_color_uint8,
            'original_image': gray,
            'colormap_used': colormap,
            'method': 'false_color_composite'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def process_rgb_channels(image: np.ndarray, operation: str, **params) -> Dict:
    """
    Apply operation to each RGB channel independently.
    
    Args:
        image: Input RGB image
        operation: 'equalize', 'sharpen', 'smooth', 'edge_detect'
        **params: Additional parameters for the operation
        
    Returns:
        dict with processed RGB image and individual channel results
    """
    try:
        # Prepare image
        rgb = _prepare_color_image(image)
        
        # Extract channels
        R = rgb[:, :, 0]
        G = rgb[:, :, 1]
        B = rgb[:, :, 2]
        
        # Process each channel
        processed_channels = {}
        
        if operation == 'equalize':
            # Histogram equalization
            R_eq = cv2.equalizeHist((R * 255).astype(np.uint8)).astype(np.float32) / 255.0
            G_eq = cv2.equalizeHist((G * 255).astype(np.uint8)).astype(np.float32) / 255.0
            B_eq = cv2.equalizeHist((B * 255).astype(np.uint8)).astype(np.float32) / 255.0
            
            processed_channels = {'r': R_eq, 'g': G_eq, 'b': B_eq}
            
        elif operation == 'sharpen':
            # Sharpening kernel
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]], dtype=np.float32)
            
            R_sharp = cv2.filter2D(R, -1, kernel)
            G_sharp = cv2.filter2D(G, -1, kernel)
            B_sharp = cv2.filter2D(B, -1, kernel)
            
            # Clip to [0, 1]
            R_sharp = np.clip(R_sharp, 0, 1)
            G_sharp = np.clip(G_sharp, 0, 1)
            B_sharp = np.clip(B_sharp, 0, 1)
            
            processed_channels = {'r': R_sharp, 'g': G_sharp, 'b': B_sharp}
            
        elif operation == 'smooth':
            # Gaussian smoothing
            kernel_size = params.get('kernel_size', 5)
            sigma = params.get('sigma', 1.0)
            
            R_smooth = cv2.GaussianBlur(R, (kernel_size, kernel_size), sigma)
            G_smooth = cv2.GaussianBlur(G, (kernel_size, kernel_size), sigma)
            B_smooth = cv2.GaussianBlur(B, (kernel_size, kernel_size), sigma)
            
            processed_channels = {'r': R_smooth, 'g': G_smooth, 'b': B_smooth}
            
        elif operation == 'edge_detect':
            # Edge detection using Sobel
            R_edge = cv2.Sobel(R, cv2.CV_64F, 1, 1, ksize=3)
            G_edge = cv2.Sobel(G, cv2.CV_64F, 1, 1, ksize=3)
            B_edge = cv2.Sobel(B, cv2.CV_64F, 1, 1, ksize=3)
            
            # Normalize to [0, 1]
            R_edge = np.abs(R_edge) / np.max(np.abs(R_edge))
            G_edge = np.abs(G_edge) / np.max(np.abs(G_edge))
            B_edge = np.abs(B_edge) / np.max(np.abs(B_edge))
            
            processed_channels = {'r': R_edge, 'g': G_edge, 'b': B_edge}
            
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        
        # Combine processed channels
        processed_rgb = np.stack([processed_channels['r'], processed_channels['g'], processed_channels['b']], axis=2)
        processed_rgb_uint8 = (processed_rgb * 255).astype(np.uint8)
        
        return {
            'success': True,
            'processed_image': processed_rgb_uint8,
            'original_image': (rgb * 255).astype(np.uint8),
            'operation': operation,
            'parameters': params,
            'channels': {
                'r': (processed_channels['r'] * 255).astype(np.uint8),
                'g': (processed_channels['g'] * 255).astype(np.uint8),
                'b': (processed_channels['b'] * 255).astype(np.uint8)
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def color_image_smoothing(image: np.ndarray, method: str) -> Dict:
    """
    Apply smoothing to color images.
    
    Args:
        image: Input color image
        method: 'rgb' (smooth each channel separately) or 'hsi' (smooth only intensity)
        
    Returns:
        dict with smoothed color image
    """
    try:
        # Prepare image
        rgb = _prepare_color_image(image)
        
        if method == 'rgb':
            # Smooth each RGB channel separately
            kernel_size = 5
            sigma = 1.0
            
            R_smooth = cv2.GaussianBlur(rgb[:, :, 0], (kernel_size, kernel_size), sigma)
            G_smooth = cv2.GaussianBlur(rgb[:, :, 1], (kernel_size, kernel_size), sigma)
            B_smooth = cv2.GaussianBlur(rgb[:, :, 2], (kernel_size, kernel_size), sigma)
            
            smoothed_rgb = np.stack([R_smooth, G_smooth, B_smooth], axis=2)
            
        elif method == 'hsi':
            # Convert to HSI, smooth only intensity, convert back
            hsi_result = rgb_to_hsi((rgb * 255).astype(np.uint8))
            
            if not hsi_result['success']:
                return hsi_result
            
            H = hsi_result['channels']['h']
            S = hsi_result['channels']['s']
            I = hsi_result['channels']['i']
            
            # Smooth only intensity channel
            kernel_size = 5
            sigma = 1.0
            I_smooth = cv2.GaussianBlur(I, (kernel_size, kernel_size), sigma)
            
            # Convert back to RGB
            rgb_result = hsi_to_rgb(H, S, I_smooth)
            
            if not rgb_result['success']:
                return rgb_result
            
            smoothed_rgb = rgb_result['processed_image'].astype(np.float32) / 255.0
            
        else:
            raise ValueError("Method must be 'rgb' or 'hsi'")
        
        # Convert to uint8
        smoothed_rgb_uint8 = (smoothed_rgb * 255).astype(np.uint8)
        
        return {
            'success': True,
            'processed_image': smoothed_rgb_uint8,
            'original_image': (rgb * 255).astype(np.uint8),
            'method': f'color_smoothing_{method}',
            'smoothing_technique': 'gaussian_blur'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def color_image_sharpening(image: np.ndarray, method: str) -> Dict:
    """
    Apply sharpening to color images while preserving color.
    
    Args:
        image: Input color image
        method: 'rgb' (sharpen each channel) or 'hsi' (sharpen intensity only)
        
    Returns:
        dict with sharpened color image
    """
    try:
        # Prepare image
        rgb = _prepare_color_image(image)
        
        if method == 'rgb':
            # Sharpen each RGB channel separately
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]], dtype=np.float32)
            
            R_sharp = cv2.filter2D(rgb[:, :, 0], -1, kernel)
            G_sharp = cv2.filter2D(rgb[:, :, 1], -1, kernel)
            B_sharp = cv2.filter2D(rgb[:, :, 2], -1, kernel)
            
            # Clip to [0, 1]
            R_sharp = np.clip(R_sharp, 0, 1)
            G_sharp = np.clip(G_sharp, 0, 1)
            B_sharp = np.clip(B_sharp, 0, 1)
            
            sharpened_rgb = np.stack([R_sharp, G_sharp, B_sharp], axis=2)
            
        elif method == 'hsi':
            # Convert to HSI, sharpen only intensity, convert back
            hsi_result = rgb_to_hsi((rgb * 255).astype(np.uint8))
            
            if not hsi_result['success']:
                return hsi_result
            
            H = hsi_result['channels']['h']
            S = hsi_result['channels']['s']
            I = hsi_result['channels']['i']
            
            # Sharpen only intensity channel
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]], dtype=np.float32)
            I_sharp = cv2.filter2D(I, -1, kernel)
            I_sharp = np.clip(I_sharp, 0, 255).astype(np.uint8)
            
            # Convert back to RGB
            rgb_result = hsi_to_rgb(H, S, I_sharp)
            
            if not rgb_result['success']:
                return rgb_result
            
            sharpened_rgb = rgb_result['processed_image'].astype(np.float32) / 255.0
            
        else:
            raise ValueError("Method must be 'rgb' or 'hsi'")
        
        # Convert to uint8
        sharpened_rgb_uint8 = (sharpened_rgb * 255).astype(np.uint8)
        
        return {
            'success': True,
            'processed_image': sharpened_rgb_uint8,
            'original_image': (rgb * 255).astype(np.uint8),
            'method': f'color_sharpening_{method}',
            'sharpening_technique': 'laplacian_kernel'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def pseudocolor_processing(gray_image: np.ndarray, scheme: str) -> Dict:
    """
    Apply pseudocolor processing with different schemes.
    
    Args:
        gray_image: Input grayscale image
        scheme: 'density', 'temperature', 'elevation'
        
    Returns:
        dict with pseudocolor image and colorbar
    """
    try:
        # Prepare image
        if len(gray_image.shape) == 3:
            gray = cv2.cvtColor(gray_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = gray_image.copy()
        
        # Normalize to [0, 1]
        gray_normalized = gray.astype(np.float32) / 255.0
        
        # Apply different pseudocolor schemes
        if scheme == 'density':
            # Density-like coloring (blue to red)
            pseudocolor = plt.cm.RdYlBu_r(gray_normalized)
            
        elif scheme == 'temperature':
            # Temperature-like coloring (black to white to red)
            pseudocolor = plt.cm.hot(gray_normalized)
            
        elif scheme == 'elevation':
            # Terrain-like coloring (green to brown to white)
            pseudocolor = plt.cm.terrain(gray_normalized)
            
        else:
            raise ValueError(f"Unsupported scheme: {scheme}")
        
        # Extract RGB channels
        if pseudocolor.shape[2] == 4:
            pseudocolor_rgb = pseudocolor[:, :, :3]
        else:
            pseudocolor_rgb = pseudocolor
        
        # Convert to uint8
        pseudocolor_uint8 = (pseudocolor_rgb * 255).astype(np.uint8)
        
        return {
            'success': True,
            'processed_image': pseudocolor_uint8,
            'original_image': gray,
            'scheme': scheme,
            'method': 'pseudocolor_processing'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# def calculate_ndvi(nir_band: np.ndarray, red_band: np.ndarray) -> Dict:
#     """
#     Calculate Normalized Difference Vegetation Index (NDVI).
    
#     Formula: NDVI = (NIR - Red) / (NIR + Red)
    
#     Args:
#         nir_band: Near-infrared band
#         red_band: Red band
        
#     Returns:
#         dict with NDVI image and statistics
#     """
#     try:
#         # Ensure both bands have same shape
#         if nir_band.shape != red_band.shape:
#             raise ValueError("NIR and Red bands must have the same shape")
        
#         # Convert to float32 for calculations
#         nir = nir_band.astype(np.float32)
#         red = red_band.astype(np.float32)
        
#         # Calculate NDVI: (NIR - Red) / (NIR + Red)
#         numerator = nir - red
#         denominator = nir + red
        
#         # Handle division by zero
#         denominator = np.where(denominator == 0, 1e-10, denominator)
        
#         ndvi = numerator / denominator
        
#         # Clip NDVI to valid range [-1, 1]
#         ndvi = np.clip(ndvi, -1, 1)
        
#         # Create false color visualization
#         # Map NDVI [-1, 1] to [0, 1] for colormap
#         ndvi_normalized = (ndvi + 1) / 2
        
#         # Apply vegetation colormap (green for high NDVI, red for low NDVI)
#         ndvi_colormap = plt.cm.RdYlGn(ndvi_normalized)
        
#         # Extract RGB channels
#         if ndvi_colormap.shape[2] == 4:
#             ndvi_rgb = ndvi_colormap[:, :, :3]
#         else:
#             ndvi_rgb = ndvi_colormap
        
#         # Convert to uint8
#         ndvi_uint8 = (ndvi_rgb * 255).astype(np.uint8)

#         # Convert RGB → BGR for OpenCV before returning
#         ndvi_bgr = cv2.cvtColor(ndvi_uint8, cv2.COLOR_RGB2BGR)
        
#         # Calculate statistics
#         ndvi_stats = {
#             'min': float(np.min(ndvi)),
#             'max': float(np.max(ndvi)),
#             'mean': float(np.mean(ndvi)),
#             'std': float(np.std(ndvi)),
#             'vegetation_pixels': int(np.sum(ndvi > 0.3)),  # Threshold for vegetation
#             'total_pixels': int(ndvi.size)
#         }
#         # # DEBUG/////////////////////////////////////////////////////////////////////////////////////////////////////////
#         # print("✅ NDVI image calculated successfully.")
#         # print("NDVI processed image shape:", ndvi_bgr.shape)
#         # print("NDVI processed image dtype:", ndvi_bgr.dtype)

        
#         return {
#             'success': True,
#             'ndvi_image': ndvi,
#             'ndvi_visualization': ndvi_uint8,
#             'processed_image':ndvi_bgr,
#             'nir_band': nir_band,
#             'red_band': red_band,
#             'statistics': ndvi_stats,
#             'formula': 'NDVI = (NIR - Red) / (NIR + Red)',
#             'method': 'ndvi_calculation'
#         }
        
#     except Exception as e:
#         return {
#             'success': False,
#             'error': str(e)
#         }


def multispectral_band_selection(image: np.ndarray, bands: List[int]) -> Dict:
    """
    Select and combine multispectral bands for visualization.
    
    Args:
        image: Multispectral image (multiple bands)
        bands: List of band indices to select
        
    Returns:
        dict with selected bands and RGB composite
    """
    try:
        if len(image.shape) != 3:
            raise ValueError("Input must be a multispectral image with multiple bands")
        
        total_bands = image.shape[2]
        
        # Validate band indices
        for band in bands:
            if band < 0 or band >= total_bands:
                raise ValueError(f"Band index {band} is out of range [0, {total_bands-1}]")
        
        # Select bands
        selected_bands = image[:, :, bands]
        
        # If 3 bands selected, create RGB composite
        if len(bands) == 3:
            # Normalize each band to [0, 255]
            rgb_composite = np.zeros_like(selected_bands, dtype=np.uint8)
            for i in range(3):
                band_data = selected_bands[:, :, i].astype(np.float32)
                band_normalized = ((band_data - band_data.min()) / (band_data.max() - band_data.min()) * 255).astype(np.uint8)
                rgb_composite[:, :, i] = band_normalized
            
            composite_type = 'RGB'
        else:
            # Create false color composite
            rgb_composite = false_color_composite(selected_bands[:, :, 0], 'jet')
            if rgb_composite['success']:
                rgb_composite = rgb_composite['processed_image']
            else:
                rgb_composite = selected_bands[:, :, 0]
            composite_type = 'False Color'
        
        return {
            'success': True,
            'selected_bands': selected_bands,
            'rgb_composite': rgb_composite,
            'band_indices': bands,
            'composite_type': composite_type,
            'total_bands': total_bands,
            'method': 'multispectral_selection'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Legacy class-based interface for backward compatibility
class ColorProcessor:
    """Legacy class-based interface for backward compatibility"""
    
    def __init__(self):
        self.supported_operations = [
            'rgb_to_hsi',
            'hsi_to_rgb',
            'intensity_slicing',
            'false_color_composite',
            'process_rgb_channels',
            'color_image_smoothing',
            'color_image_sharpening',
            'pseudocolor_processing',
            'calculate_ndvi',
            'multispectral_band_selection'
        ]
    
    def process(self, data):
        """Main processing function for legacy interface"""
        operation = data.get('operation')
        
        if operation not in self.supported_operations:
            return {'error': f'Unsupported operation: {operation}'}
        
        try:
            if operation == 'rgb_to_hsi':
                image = data.get('image')
                if image is None:
                    return {'error': 'No image provided'}
                return rgb_to_hsi(image)
            
            elif operation == 'hsi_to_rgb':
                h = data.get('h')
                s = data.get('s')
                i = data.get('i')
                if h is None or s is None or i is None:
                    return {'error': 'H, S, I channels required'}
                return hsi_to_rgb(h, s, i)
            
            elif operation == 'intensity_slicing':
                image = data.get('image')
                levels = data.get('levels', 8)
                if image is None:
                    return {'error': 'No image provided'}
                return intensity_slicing(image, levels)
            
            elif operation == 'false_color_composite':
                image = data.get('image')
                colormap = data.get('colormap', 'jet')
                if image is None:
                    return {'error': 'No image provided'}
                return false_color_composite(image, colormap)
            
            elif operation == 'process_rgb_channels':
                image = data.get('image')
                operation_type = data.get('operation_type', 'equalize')
                params = data.get('params', {})
                if image is None:
                    return {'error': 'No image provided'}
                return process_rgb_channels(image, operation_type, **params)
            
            elif operation == 'color_image_smoothing':
                image = data.get('image')
                method = data.get('method', 'rgb')
                if image is None:
                    return {'error': 'No image provided'}
                return color_image_smoothing(image, method)
            
            elif operation == 'color_image_sharpening':
                image = data.get('image')
                method = data.get('method', 'rgb')
                if image is None:
                    return {'error': 'No image provided'}
                return color_image_sharpening(image, method)
            
            elif operation == 'pseudocolor_processing':
                image = data.get('image')
                scheme = data.get('scheme', 'density')
                if image is None:
                    return {'error': 'No image provided'}
                return pseudocolor_processing(image, scheme)
            
            # elif operation == 'calculate_ndvi':
            #     nir_band = data.get('nir_band')
            #     red_band = data.get('red_band')
            #     if nir_band is None or red_band is None:
            #         return {'error': 'NIR and Red bands required'}
            #     return calculate_ndvi(nir_band, red_band)
            
            elif operation == 'multispectral_band_selection':
                image = data.get('image')
                bands = data.get('bands', [0, 1, 2])
                if image is None:
                    return {'error': 'No image provided'}
                return multispectral_band_selection(image, bands)
            
            else:
                return {'error': 'Operation not implemented'}
                
        except Exception as e:
            return {'error': f'Processing failed: {str(e)}'}