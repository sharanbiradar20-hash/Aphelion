"""
Image Processing Modules
Based on "Digital Image Processing" by Gonzalez & Woods
"""

# from .module1_fundamentals import FundamentalsProcessor
from .module2_intensity import IntensityProcessor
from .module3_frequency import FrequencyProcessor
from .module4_restoration import RestorationProcessor
from .module5_color import ColorProcessor

__all__ = [
    'IntensityProcessor', 
    'FrequencyProcessor',
    'RestorationProcessor',
    'ColorProcessor'
]
