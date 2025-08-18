from PIL import Image, ImageEnhance, ImageOps
import numpy as np

class EnhancedAdjustments:
    @staticmethod
    def apply(image, adjustment_name, value):
        """Apply adjustment to image"""
        adjustment_map = {
            'brightness': EnhancedAdjustments.brightness,
            'contrast': EnhancedAdjustments.contrast,
            'saturation': EnhancedAdjustments.saturation,
            'sharpness': EnhancedAdjustments.sharpness,
            'hue': EnhancedAdjustments.hue,
            'gamma': EnhancedAdjustments.gamma,
            'exposure': EnhancedAdjustments.exposure,
            'temperature': EnhancedAdjustments.temperature,
            'levels': EnhancedAdjustments.levels,
            'auto_levels': EnhancedAdjustments.auto_levels,
            'auto_color': EnhancedAdjustments.auto_color,
        }
        
        if adjustment_name in adjustment_map:
            return adjustment_map[adjustment_name](image, value)
        return None
    
    @staticmethod
    def brightness(image, factor):
        """Điều chỉnh độ sáng
        factor: 0.0 - 2.0 (1.0 = không thay đổi)
        """
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def contrast(image, factor):
        """Điều chỉnh độ tương phản
        factor: 0.0 - 2.0 (1.0 = không thay đổi)
        """
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def saturation(image, factor):
        """Điều chỉnh độ bão hòa màu
        factor: 0.0 - 2.0 (1.0 = không thay đổi, 0.0 = grayscale)
        """
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def sharpness(image, factor):
        """Điều chỉnh độ sắc nét
        factor: 0.0 - 2.0 (1.0 = không thay đổi)
        """
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def gamma(image, gamma):
        """Điều chỉnh gamma
        gamma: 0.1 - 3.0 (1.0 = không thay đổi)
        """
        # Convert PIL image to numpy array
        array = np.array(image, dtype=np.float32)
        
        # Normalize to 0-1 range
        array = array / 255.0
        
        # Apply gamma correction
        array = np.power(array, 1.0 / gamma)
        
        # Convert back to 0-255 range and clip to valid range
        array = (array * 255)
        array = np.clip(array, 0, 255).astype(np.uint8)
        
        return Image.fromarray(array)
    
    @staticmethod
    def exposure(image, stops):
        """Điều chỉnh exposure (theo stops)
        stops: -3.0 đến 3.0 (0 = không thay đổi)
        """
        # Convert stops to multiplier
        factor = 2 ** stops
        return EnhancedAdjustments.brightness(image, factor)
    
    @staticmethod
    def hue(image, shift):
        """Điều chỉnh hue (độ màu)
        shift: -180 đến 180 (0 = không thay đổi)
        """
        # Convert to HSV
        hsv = image.convert('HSV')
        array = np.array(hsv, dtype=np.uint8)
        
        # Adjust hue channel and clip to valid range
        array[:, :, 0] = np.clip((array[:, :, 0] + shift) % 256, 0, 255)
        
        # Convert back to RGB
        hsv_adjusted = Image.fromarray(array, 'HSV')
        return hsv_adjusted.convert('RGB')
    
    @staticmethod
    def temperature(image, temp):
        """Điều chỉnh color temperature
        temp: -100 đến 100 (0 = không thay đổi)
        """
        array = np.array(image, dtype=np.float32)
        
        if temp > 0:  # Warmer (more red/yellow)
            array[:, :, 0] *= (1 + temp / 100 * 0.3)  # Red
            array[:, :, 1] *= (1 + temp / 100 * 0.1)  # Green
        else:  # Cooler (more blue)
            array[:, :, 2] *= (1 + abs(temp) / 100 * 0.3)  # Blue
        
        # Clip values to valid range
        array = np.clip(array, 0, 255)
        
        return Image.fromarray(array.astype(np.uint8))
    
    @staticmethod
    def levels(image, shadows=0, midtones=1, highlights=255):
        """Điều chỉnh levels (shadows, midtones, highlights)"""
        # Convert to numpy array
        array = np.array(image, dtype=np.float32)
        
        # Normalize input range
        array = (array - shadows) / (highlights - shadows) * 255
        
        # Apply gamma for midtones
        if midtones != 1:
            array = array / 255.0
            array = np.power(array, 1.0 / midtones)
            array = array * 255.0
        
        # Clip values to valid range
        array = np.clip(array, 0, 255)
        
        return Image.fromarray(array.astype(np.uint8))
    
    @staticmethod
    def auto_levels(image, value=None):
        """Tự động điều chỉnh levels"""
        return ImageOps.autocontrast(image)
    
    @staticmethod
    def auto_color(image, value=None):
        """Tự động cân bằng màu"""
        return ImageOps.equalize(image)
