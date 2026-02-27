"""
Visualization utilities for image processing
Functions for creating histograms, spectrums, and other visualizations

Enhanced with comprehensive plotting functions for faculty presentation.
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from matplotlib import cm
from io import BytesIO
import base64
import os
from typing import Dict, List, Tuple, Union


def plot_histogram(image: np.ndarray, title: str = "Histogram") -> str:
    """
    Create 256-bin histogram plot and save as PNG.
    
    Args:
        image: Input image
        title: Title for the plot
        
    Returns:
        filepath to saved histogram
    """
    try:
        # Convert to grayscale if necessary
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Calculate 256-bin histogram
        histogram = cv2.calcHist([gray], [0], None, [256], [0, 256])
        histogram = histogram.flatten()
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        bins = np.arange(256)
        ax.bar(bins, histogram, alpha=0.7, color='blue', width=1)
        ax.set_xlabel('Intensity Value')
        ax.set_ylabel('Frequency')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 255)
        
        # Add statistics text
        mean_val = np.mean(gray)
        std_val = np.std(gray)
        ax.text(0.02, 0.98, f'Mean: {mean_val:.2f}\nStd: {std_val:.2f}', 
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        # Save plot
        output_dir = "satellite-image-processor/backend/uploads"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"histogram_{np.random.randint(1000, 9999)}.png"
        filepath = os.path.join(output_dir, filename)
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
        
    except Exception as e:
        return None


def plot_frequency_spectrum(fft_result: Dict, title: str = "Frequency Spectrum") -> str:
    """
    Create magnitude and phase plots for FFT result.
    
    Args:
        fft_result: Dictionary containing FFT results
        title: Title for the plot
        
    Returns:
        filepath to saved spectrum plot
    """
    try:
        # Extract data from FFT result
        if 'magnitude_spectrum' in fft_result:
            magnitude = fft_result['magnitude_spectrum']
        else:
            return None
        
        phase = fft_result.get('phase_spectrum', None)
        
        # Create subplots
        if phase is not None:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        else:
            fig, ax1 = plt.subplots(1, 1, figsize=(10, 8))
            ax2 = None
        
        # Plot magnitude spectrum (log scale)
        if isinstance(magnitude, list):
            magnitude = np.array(magnitude)
        
        # Apply log scale
        magnitude_log = np.log(1 + np.abs(magnitude))
        
        im1 = ax1.imshow(magnitude_log, cmap='hot', aspect='auto')
        ax1.set_title('Magnitude Spectrum (Log Scale)')
        ax1.set_xlabel('Frequency (v)')
        ax1.set_ylabel('Frequency (u)')
        plt.colorbar(im1, ax=ax1, label='Log Magnitude')
        
        # Plot phase spectrum if available
        if ax2 is not None and phase is not None:
            if isinstance(phase, list):
                phase = np.array(phase)
            
            im2 = ax2.imshow(phase, cmap='hsv', aspect='auto')
            ax2.set_title('Phase Spectrum')
            ax2.set_xlabel('Frequency (v)')
            ax2.set_ylabel('Frequency (u)')
            plt.colorbar(im2, ax=ax2, label='Phase (radians)')
        
        plt.suptitle(title)
        plt.tight_layout()
        
        # Save plot
        output_dir = "satellite-image-processor/backend/uploads"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"frequency_spectrum_{np.random.randint(1000, 9999)}.png"
        filepath = os.path.join(output_dir, filename)
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
        
    except Exception as e:
        return None


def plot_comparison_grid(images: List[np.ndarray], titles: List[str], 
                        rows: int = 2, cols: int = 2) -> str:
    """
    Create side-by-side comparison grid of images.
    
    Args:
        images: List of images to compare
        titles: List of titles for each image
        rows: Number of rows in grid
        cols: Number of columns in grid
        
    Returns:
        filepath to saved comparison plot
    """
    try:
        # Validate inputs
        if len(images) != len(titles):
            raise ValueError("Number of images must match number of titles")
        
        if len(images) > rows * cols:
            raise ValueError("Too many images for grid size")
        
        # Create subplots
        fig, axes = plt.subplots(rows, cols, figsize=(15, 12))
        
        # Handle single subplot case
        if rows == 1 and cols == 1:
            axes = [axes]
        elif rows == 1 or cols == 1:
            axes = axes.flatten()
        else:
            axes = axes.flatten()
        
        # Plot each image
        for i, (image, title) in enumerate(zip(images, titles)):
            if i >= len(axes):
                break
                
            ax = axes[i]
            
            # Determine colormap based on image type
            if len(image.shape) == 3:
                # Color image
                if image.shape[2] == 3:
                    # RGB image
                    ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                else:
                    # Multi-channel image
                    ax.imshow(image[:, :, 0], cmap='gray')
            else:
                # Grayscale image
                ax.imshow(image, cmap='gray')
            
            ax.set_title(title)
            ax.axis('off')
        
        # Hide unused subplots
        for i in range(len(images), len(axes)):
            axes[i].axis('off')
        
        plt.tight_layout()
        
        # Save plot
        output_dir = "satellite-image-processor/backend/uploads"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"comparison_grid_{np.random.randint(1000, 9999)}.png"
        filepath = os.path.join(output_dir, filename)
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
        
    except Exception as e:
        return None


def create_metrics_report(metrics_dict: Dict) -> str:
    """
    Generate formatted report with all metrics.
    
    Args:
        metrics_dict: Dictionary containing various metrics
        
    Returns:
        Formatted report string
    """
    try:
        report = []
        report.append("=" * 60)
        report.append("IMAGE PROCESSING METRICS REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Image dimensions
        if 'dimensions' in metrics_dict:
            dims = metrics_dict['dimensions']
            report.append("IMAGE DIMENSIONS:")
            report.append(f"  Width: {dims.get('width', 'N/A')} pixels")
            report.append(f"  Height: {dims.get('height', 'N/A')} pixels")
            report.append(f"  Total Pixels: {dims.get('total_pixels', 'N/A'):,}")
            report.append("")
        
        # Intensity statistics
        if 'intensity_statistics' in metrics_dict:
            stats = metrics_dict['intensity_statistics']
            report.append("INTENSITY STATISTICS:")
            report.append(f"  Mean: {stats.get('mean', 'N/A'):.2f}")
            report.append(f"  Standard Deviation: {stats.get('std', 'N/A'):.2f}")
            report.append(f"  Minimum: {stats.get('min', 'N/A'):.2f}")
            report.append(f"  Maximum: {stats.get('max', 'N/A'):.2f}")
            report.append(f"  Range: {stats.get('range', 'N/A'):.2f}")
            report.append("")
        
        # Image quality metrics
        if 'image_quality' in metrics_dict:
            quality = metrics_dict['image_quality']
            report.append("IMAGE QUALITY METRICS:")
            report.append(f"  Entropy: {quality.get('entropy', 'N/A'):.4f} bits")
            report.append(f"  Contrast (RMS): {quality.get('contrast', 'N/A'):.2f}")
            report.append(f"  Sharpness Index: {quality.get('sharpness', 'N/A'):.2f}")
            report.append(f"  Edge Strength: {quality.get('edge_strength', 'N/A'):.2f}")
            report.append(f"  Dynamic Range: {quality.get('dynamic_range', 'N/A'):.2f}")
            report.append("")
        
        # Comparison metrics
        if 'comparison_metrics' in metrics_dict:
            comp = metrics_dict['comparison_metrics']
            report.append("COMPARISON METRICS:")
            report.append(f"  PSNR: {comp.get('psnr', 'N/A'):.2f} dB")
            report.append(f"  MSE: {comp.get('mse', 'N/A'):.2f}")
            report.append(f"  SSIM: {comp.get('ssim', 'N/A'):.4f}")
            report.append(f"  SNR: {comp.get('snr', 'N/A'):.2f} dB")
            report.append("")
        
        # Processing information
        if 'processing_info' in metrics_dict:
            info = metrics_dict['processing_info']
            report.append("PROCESSING INFORMATION:")
            report.append(f"  Method: {info.get('method', 'N/A')}")
            report.append(f"  Parameters: {info.get('parameters', 'N/A')}")
            report.append(f"  Processing Time: {info.get('processing_time', 'N/A')} seconds")
            report.append("")
        
        # Histogram features
        if 'histogram_features' in metrics_dict:
            hist = metrics_dict['histogram_features']
            report.append("HISTOGRAM FEATURES:")
            report.append(f"  Mean Intensity: {hist.get('mean_intensity', 'N/A'):.2f}")
            report.append(f"  Variance: {hist.get('variance', 'N/A'):.2f}")
            report.append(f"  Skewness: {hist.get('skewness', 'N/A'):.4f}")
            report.append(f"  Kurtosis: {hist.get('kurtosis', 'N/A'):.4f}")
            report.append("")
        
        # Texture features
        if 'texture_features' in metrics_dict:
            texture = metrics_dict['texture_features']
            report.append("TEXTURE FEATURES:")
            report.append(f"  Texture Mean: {texture.get('texture_mean', 'N/A'):.2f}")
            report.append(f"  Texture Std: {texture.get('texture_std', 'N/A'):.2f}")
            report.append(f"  Texture Variance: {texture.get('texture_variance', 'N/A'):.2f}")
            report.append(f"  Edge Density: {texture.get('edge_density', 'N/A'):.4f}")
            report.append("")
        
        report.append("=" * 60)
        report.append("End of Report")
        report.append("=" * 60)
        
        return "\n".join(report)
        
    except Exception as e:
        return f"Error generating report: {str(e)}"


def create_histogram(image: np.ndarray, bins: int = 256) -> Dict:
    """
    Create histogram data for visualization.
    
    Args:
        image: numpy array representing the image
        bins: number of bins for histogram
        
    Returns:
        dict: Dictionary containing histogram data
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
        histogram = cv2.calcHist([gray_image], [0], None, [bins], [0, 256])
        histogram = histogram.flatten()
        
        # Normalize histogram
        histogram_normalized = histogram / np.sum(histogram)
        
        return {
            'bins': list(range(bins)),
            'values': histogram.tolist(),
            'normalized_values': histogram_normalized.tolist(),
            'total_pixels': int(np.sum(histogram))
        }
        
    except Exception as e:
        return {'error': f'Failed to create histogram: {str(e)}'}


def create_color_histogram(image: np.ndarray) -> Dict:
    """
    Create color histogram data for RGB images.
    
    Args:
        image: numpy array representing the color image
        
    Returns:
        dict: Dictionary containing color histogram data
    """
    try:
        if image is None:
            return {'error': 'Invalid image'}
        
        if len(image.shape) != 3:
            return {'error': 'Image must be color (3 channels)'}
        
        # Split into color channels
        b_channel, g_channel, r_channel = cv2.split(image)
        
        # Calculate histograms for each channel
        b_hist = cv2.calcHist([b_channel], [0], None, [256], [0, 256])
        g_hist = cv2.calcHist([g_channel], [0], None, [256], [0, 256])
        r_hist = cv2.calcHist([r_channel], [0], None, [256], [0, 256])
        
        return {
            'blue': {
                'bins': list(range(256)),
                'values': b_hist.flatten().tolist()
            },
            'green': {
                'bins': list(range(256)),
                'values': g_hist.flatten().tolist()
            },
            'red': {
                'bins': list(range(256)),
                'values': r_hist.flatten().tolist()
            }
        }
        
    except Exception as e:
        return {'error': f'Failed to create color histogram: {str(e)}'}


def create_spectrum_visualization(image: np.ndarray) -> Dict:
    """
    Create frequency spectrum visualization data.
    
    Args:
        image: numpy array representing the image
        
    Returns:
        dict: Dictionary containing spectrum data
    """
    try:
        if image is None:
            return {'error': 'Invalid image'}
        
        # Convert to grayscale if color image
        if len(image.shape) == 3:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = image
        
        # Apply 2D FFT
        f_transform = np.fft.fft2(gray_image)
        f_shift = np.fft.fftshift(f_transform)
        
        # Calculate magnitude spectrum
        magnitude_spectrum = np.log(np.abs(f_shift) + 1)
        
        # Calculate phase spectrum
        phase_spectrum = np.angle(f_shift)
        
        # Normalize for visualization
        magnitude_spectrum = (magnitude_spectrum - magnitude_spectrum.min()) / (magnitude_spectrum.max() - magnitude_spectrum.min())
        
        return {
            'magnitude_spectrum': magnitude_spectrum.tolist(),
            'phase_spectrum': phase_spectrum.tolist(),
            'shape': magnitude_spectrum.shape,
            'min_value': float(magnitude_spectrum.min()),
            'max_value': float(magnitude_spectrum.max())
        }
        
    except Exception as e:
        return {'error': f'Failed to create spectrum visualization: {str(e)}'}


def create_histogram_plot(histogram_data: Dict, title: str = "Histogram") -> str:
    """
    Create a histogram plot and return as base64 encoded image.
    
    Args:
        histogram_data: Dictionary containing histogram data
        title: Title for the plot
        
    Returns:
        str: Base64 encoded image string
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bins = histogram_data['bins']
        values = histogram_data['values']
        
        ax.bar(bins, values, alpha=0.7, color='blue')
        ax.set_xlabel('Intensity Value')
        ax.set_ylabel('Frequency')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        
        # Convert plot to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
        
    except Exception as e:
        return None


def create_color_histogram_plot(color_histogram_data: Dict, title: str = "Color Histogram") -> str:
    """
    Create a color histogram plot and return as base64 encoded image.
    
    Args:
        color_histogram_data: Dictionary containing color histogram data
        title: Title for the plot
        
    Returns:
        str: Base64 encoded image string
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bins = list(range(256))
        
        ax.plot(bins, color_histogram_data['red']['values'], color='red', alpha=0.7, label='Red')
        ax.plot(bins, color_histogram_data['green']['values'], color='green', alpha=0.7, label='Green')
        ax.plot(bins, color_histogram_data['blue']['values'], color='blue', alpha=0.7, label='Blue')
        
        ax.set_xlabel('Intensity Value')
        ax.set_ylabel('Frequency')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Convert plot to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
        
    except Exception as e:
        return None


def create_spectrum_plot(spectrum_data: Dict, title: str = "Frequency Spectrum") -> str:
    """
    Create a frequency spectrum plot and return as base64 encoded image.
    
    Args:
        spectrum_data: Dictionary containing spectrum data
        title: Title for the plot
        
    Returns:
        str: Base64 encoded image string
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        magnitude_spectrum = np.array(spectrum_data['magnitude_spectrum'])
        
        im = ax.imshow(magnitude_spectrum, cmap='hot', interpolation='nearest')
        ax.set_title(title)
        ax.set_xlabel('Frequency X')
        ax.set_ylabel('Frequency Y')
        
        # Add colorbar
        plt.colorbar(im, ax=ax, label='Magnitude')
        
        # Convert plot to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
        
    except Exception as e:
        return None


def create_comparison_plot(original_data: np.ndarray, processed_data: np.ndarray, title: str = "Image Comparison") -> str:
    """
    Create a comparison plot showing original and processed images.
    
    Args:
        original_data: Original image data
        processed_data: Processed image data
        title: Title for the plot
        
    Returns:
        str: Base64 encoded image string
    """
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Original image
        ax1.imshow(original_data, cmap='gray')
        ax1.set_title('Original Image')
        ax1.axis('off')
        
        # Processed image
        ax2.imshow(processed_data, cmap='gray')
        ax2.set_title('Processed Image')
        ax2.axis('off')
        
        plt.suptitle(title)
        
        # Convert plot to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
        
    except Exception as e:
        return None