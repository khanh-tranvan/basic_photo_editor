from PIL import Image, ImageOps
import math

class EnhancedTransforms:
    @staticmethod
    def apply(image, transform_name, params):
        transform_map = {
            'rotate': EnhancedTransforms.rotate,
            'resize': EnhancedTransforms.resize,
            'crop': EnhancedTransforms.crop,
            'flip': EnhancedTransforms.flip,
            'scale': EnhancedTransforms.scale,
            'auto_orient': EnhancedTransforms.auto_orient,
        }
        
        if transform_name in transform_map:
            return transform_map[transform_name](image, **params)
        return None
    
    @staticmethod
    def rotate(image, angle):
        if angle % 360 == 0:
            return image
        
        # For 90, 180, 270 degree rotations, use transpose for better quality
        if angle == 90:
            return image.transpose(Image.ROTATE_90)
        elif angle == 180:
            return image.transpose(Image.ROTATE_180)
        elif angle == 270:
            return image.transpose(Image.ROTATE_270)
        else:
            # For arbitrary angles, use rotate with expand=True
            return image.rotate(angle, expand=True, fillcolor='white')
    
    @staticmethod
    def resize(image, size, resample=Image.Resampling.LANCZOS):
        if isinstance(size, (list, tuple)) and len(size) == 2:
            return image.resize(size, resample)
        return image
    
    @staticmethod
    def scale(image, factor):
        if factor <= 0:
            return image
        
        new_width = int(image.width * factor)
        new_height = int(image.height * factor)
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    @staticmethod
    def flip(image, direction):
        if direction.lower() == 'horizontal':
            return image.transpose(Image.FLIP_LEFT_RIGHT)
        elif direction.lower() == 'vertical':
            return image.transpose(Image.FLIP_TOP_BOTTOM)
        return image
    
    @staticmethod
    def crop(image, box):
        if isinstance(box, (list, tuple)) and len(box) == 4:
            left, top, right, bottom = box
            
            # Validate coordinates
            left = max(0, min(left, image.width))
            top = max(0, min(top, image.height))
            right = max(left + 1, min(right, image.width))
            bottom = max(top + 1, min(bottom, image.height))
            
            return image.crop((left, top, right, bottom))
        return image
    
    @staticmethod
    def auto_orient(image):
        try:
            return ImageOps.exif_transpose(image)
        except:
            return image
