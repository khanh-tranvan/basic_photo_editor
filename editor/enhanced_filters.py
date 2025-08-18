from PIL import Image, ImageFilter, ImageEnhance
import numpy as np

class EnhancedFilters:
    @staticmethod
    def apply(image, filter_name, params=None):
        """Apply filter to image"""
        if params is None:
            params = {}
        
        filter_map = {
            'blur': EnhancedFilters.blur,
            'sharpen': EnhancedFilters.sharpen,
            'grayscale': EnhancedFilters.grayscale,
            'sepia': EnhancedFilters.sepia,
            'edge_enhance': EnhancedFilters.edge_enhance,
            'emboss': EnhancedFilters.emboss,
            'find_edges': EnhancedFilters.find_edges,
            'smooth': EnhancedFilters.smooth,
            'detail': EnhancedFilters.detail,
            'contour': EnhancedFilters.contour,
            'vintage': EnhancedFilters.vintage,
            'black_and_white': EnhancedFilters.black_and_white,
            'random_filter': EnhancedFilters.random_filter,
        }
        
        if filter_name in filter_map:
            return filter_map[filter_name](image, **params)
        return None
    
    @staticmethod
    def blur(image, radius=2):
        """Làm mờ ảnh"""
        return image.filter(ImageFilter.GaussianBlur(radius=radius))
    
    @staticmethod
    def sharpen(image):
        """Làm sắc nét ảnh"""
        return image.filter(ImageFilter.SHARPEN)
    
    @staticmethod
    def grayscale(image):
        """Chuyển ảnh sang đen trắng"""
        return image.convert('L').convert('RGB')
    
    @staticmethod
    def sepia(image):
        """Hiệu ứng sepia (nâu cổ điển)"""
        # Convert to grayscale first
        grayscale = image.convert('L')
        
        # Convert back to RGB
        sepia_image = Image.new('RGB', image.size)
        
        # Apply sepia tone
        for x in range(image.width):
            for y in range(image.height):
                gray_value = grayscale.getpixel((x, y))
                
                # Sepia formula
                r = min(255, int(gray_value * 1.35))
                g = min(255, int(gray_value * 1.20))
                b = min(255, int(gray_value * 0.87))
                
                sepia_image.putpixel((x, y), (r, g, b))
        
        return sepia_image
    
    @staticmethod
    def edge_enhance(image):
        """Tăng cường viền"""
        return image.filter(ImageFilter.EDGE_ENHANCE)
    
    @staticmethod
    def emboss(image):
        """Hiệu ứng nổi"""
        return image.filter(ImageFilter.EMBOSS)
    
    @staticmethod
    def find_edges(image):
        """Tìm viền"""
        return image.filter(ImageFilter.FIND_EDGES)
    
    @staticmethod
    def smooth(image):
        """Làm mịn ảnh"""
        return image.filter(ImageFilter.SMOOTH)
    
    @staticmethod
    def detail(image):
        """Tăng chi tiết"""
        return image.filter(ImageFilter.DETAIL)
    
    @staticmethod
    def contour(image):
        """Hiệu ứng đường viền"""
        return image.filter(ImageFilter.CONTOUR)
    
    @staticmethod
    def vintage(image):
        """Hiệu ứng vintage"""
        # Giảm độ bão hòa và thêm hiệu ứng sepia nhẹ
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(0.7)  # Giảm màu sắc
        
        # Thêm tông màu ấm
        array = np.array(image)
        array[:, :, 0] = np.clip(array[:, :, 0] * 1.1, 0, 255)  # Tăng đỏ
        array[:, :, 2] = np.clip(array[:, :, 2] * 0.9, 0, 255)  # Giảm xanh
        
        return Image.fromarray(array.astype('uint8'))
    
    @staticmethod
    def black_and_white(image, threshold=128):
        """Chuyển ảnh sang đen trắng thuần túy"""
        grayscale = image.convert('L')
        
        # Apply threshold
        def threshold_func(x):
            return 255 if x > threshold else 0
        
        bw_image = grayscale.point(threshold_func, mode='1')
        return bw_image.convert('RGB')
    
    @staticmethod
    def random_filter(image):
        """Apply random filter effect"""
        import random
        filters = [
            lambda x: ImageEnhance.Color(x).enhance(random.uniform(0.5, 1.5)),
            lambda x: ImageEnhance.Brightness(x).enhance(random.uniform(0.8, 1.2)),
            lambda x: ImageEnhance.Contrast(x).enhance(random.uniform(0.8, 1.2)),
            lambda x: x.convert("L").convert("RGB"),
            lambda x: EnhancedFilters.sepia(x)
        ]
        return random.choice(filters)(image)
