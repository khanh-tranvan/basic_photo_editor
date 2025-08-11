from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import random
import os

def rotate_90(img):
    return img.rotate(-90, expand=True)

def to_grayscale(img):
    return img.convert("L").convert("RGB")

def adjust_brightness(img, factor):
    return ImageEnhance.Brightness(img).enhance(factor)

def adjust_contrast(img, factor):
    return ImageEnhance.Contrast(img).enhance(factor)

def blur(img, radius):
    return img.filter(ImageFilter.GaussianBlur(radius))

def adjust_saturation(img, factor):
    return ImageEnhance.Color(img).enhance(factor)

def apply_random_filter(img):
    filters = [
        lambda x: ImageEnhance.Color(x).enhance(random.uniform(0.5, 1.5)),  # Tùy chỉnh bão hòa
        lambda x: ImageEnhance.Brightness(x).enhance(random.uniform(0.8, 1.2)),  # Tùy chỉnh sáng
        lambda x: ImageEnhance.Contrast(x).enhance(random.uniform(0.8, 1.2)),  # Tùy chỉnh tương phản
        lambda x: x.convert("L").convert("RGB"),  # Chuyển sang trắng đen rồi trở lại
        lambda x: x.filter(ImageFilter.SEPIA)  # Bộ lọc Sepia
    ]
    return random.choice(filters)(img)

def add_text_to_image(img, text, x, y, font_name, font_size, color="#FFFFFF"):
    # Tạo một bản sao của ảnh
    new_img = img.copy()
    draw = ImageDraw.Draw(new_img)
    
    try:
        # Sử dụng font hệ thống với kích thước được chỉ định
        # Ưu tiên font Arial, nếu không có thì dùng font mặc định với kích thước rõ ràng
        font = None
        if os.path.exists("arial.ttf"):
            font = ImageFont.truetype("arial.ttf", font_size)
        elif os.path.exists("times.ttf"):
            font = ImageFont.truetype("times.ttf", font_size)
        else:
            font = ImageFont.load_default(size=font_size)  # Đảm bảo kích thước được áp dụng
        
        print(f"Applying font with size: {font_size}, color: {color}")  # Debug để kiểm tra
        
        # Tính kích thước văn bản
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Điều chỉnh vị trí để văn bản không vượt ra ngoài
        img_width, img_height = img.size
        x = max(10, min(x, img_width - text_width - 10))
        y = max(10, min(y, img_height - text_height - 10))
        
        # Chèn văn bản với màu đã chọn và viền đen
        draw.text((x+1, y+1), text, fill="black", font=font)
        draw.text((x-1, y-1), text, fill="black", font=font)
        draw.text((x+1, y-1), text, fill="black", font=font)
        draw.text((x-1, y+1), text, fill="black", font=font)
        draw.text((x, y), text, fill=color, font=font)
        
        return new_img
    except Exception as e:
        print(f"Error adding text: {e}")
        return img  # Trả về ảnh gốc nếu lỗi