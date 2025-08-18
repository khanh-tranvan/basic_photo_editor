import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QSlider, QGroupBox, QScrollArea,
                             QFileDialog, QInputDialog, QColorDialog, QMessageBox,
                             QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QImage
from PIL import Image, ImageDraw, ImageFont
from editor.image_state import ImageState
from editor.image_utils import *
import os

class ImageCanvas(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("QFrame { background-color: gray; border: 1px solid black; }")
        
        # Image display variables
        self.pixmap = None
        self.scaled_pixmap = None
        self.image_rect = None
        
        # Crop and text variables
        self.start_point = None
        self.current_rect = None
        self.text_mode = False
        self.text_start_point = None
        
        # Mouse tracking
        self.setMouseTracking(True)
        
    def set_image(self, pil_image):
        if pil_image:
            # Convert PIL image to QPixmap
            if pil_image.mode == "RGBA":
                pil_image = pil_image.convert("RGB")
            
            # Convert PIL image to QImage
            data = pil_image.convert("RGBA").tobytes("raw", "RGBA")
            qimage = QImage(data, pil_image.size[0], pil_image.size[1], QImage.Format.Format_RGBA8888)
            self.pixmap = QPixmap.fromImage(qimage)
            self.scale_image()
        else:
            self.pixmap = None
            self.scaled_pixmap = None
            self.image_rect = None
        self.update()
    
    def scale_image(self):
        if self.pixmap:
            # Scale image to fit in canvas while maintaining aspect ratio
            canvas_size = self.size()
            scaled_pixmap = self.pixmap.scaled(canvas_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.scaled_pixmap = scaled_pixmap
            
            # Calculate image position to center it
            x = (canvas_size.width() - scaled_pixmap.width()) // 2
            y = (canvas_size.height() - scaled_pixmap.height()) // 2
            self.image_rect = QRect(x, y, scaled_pixmap.width(), scaled_pixmap.height())
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scale_image()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        
        if self.scaled_pixmap:
            painter.drawPixmap(self.image_rect, self.scaled_pixmap)
        
        # Draw selection rectangle
        if self.current_rect:
            pen = QPen(QColor("red") if not self.text_mode else QColor("green"), 2)
            painter.setPen(pen)
            painter.drawRect(self.current_rect)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.image_rect:
            pos = event.pos()
            if self.image_rect.contains(pos):
                if self.text_mode:
                    self.text_start_point = pos
                else:
                    self.start_point = pos
                self.current_rect = None
                self.update()
    
    def mouseMoveEvent(self, event):
        if self.start_point and self.image_rect:
            pos = event.pos()
            if self.image_rect.contains(pos):
                self.current_rect = QRect(self.start_point, pos).normalized()
                self.update()
        elif self.text_start_point and self.image_rect:
            pos = event.pos()
            if self.image_rect.contains(pos):
                self.current_rect = QRect(self.text_start_point, pos).normalized()
                self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.image_rect:
            pos = event.pos()
            if self.image_rect.contains(pos):
                if self.text_mode and self.text_start_point:
                    # Find the main window
                    main_window = self.window()
                    if hasattr(main_window, 'handle_text_placement'):
                        main_window.handle_text_placement(self.text_start_point, pos)
                    self.text_start_point = None
                elif self.start_point:
                    # Find the main window
                    main_window = self.window()
                    if hasattr(main_window, 'handle_crop'):
                        main_window.handle_crop(self.start_point, pos)
                    self.start_point = None
                self.current_rect = None
                self.update()
    
    def get_image_coordinates(self, canvas_pos):
        """Convert canvas coordinates to image coordinates"""
        if not self.image_rect or not self.pixmap:
            return None
        
        # Calculate relative position within the displayed image
        rel_x = (canvas_pos.x() - self.image_rect.x()) / self.image_rect.width()
        rel_y = (canvas_pos.y() - self.image_rect.y()) / self.image_rect.height()
        
        # Convert to original image coordinates
        img_x = int(rel_x * self.pixmap.width())
        img_y = int(rel_y * self.pixmap.height())
        
        return QPoint(img_x, img_y)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_state = ImageState()
        self.selected_font = "arial"
        self.selected_text = "Text"
        self.selected_font_size = 40
        self.selected_color = "#FFFFFF"
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Photo Editor")
        self.setGeometry(100, 100, 1200, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Controls panel (left side)
        controls_widget = QWidget()
        controls_widget.setFixedWidth(250)
        controls_layout = QVBoxLayout(controls_widget)
        
        # Basic controls group
        basic_group = QGroupBox("Chức năng cơ bản")
        basic_layout = QVBoxLayout(basic_group)
        
        self.open_btn = QPushButton("Mở ảnh")
        self.open_btn.clicked.connect(self.open_image)
        basic_layout.addWidget(self.open_btn)
        
        self.rotate_btn = QPushButton("Xoay 90°")
        self.rotate_btn.clicked.connect(self.rotate_image)
        basic_layout.addWidget(self.rotate_btn)
        
        self.grayscale_btn = QPushButton("Trắng đen")
        self.grayscale_btn.clicked.connect(self.to_grayscale)
        basic_layout.addWidget(self.grayscale_btn)
        
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.undo)
        basic_layout.addWidget(self.undo_btn)
        
        self.save_btn = QPushButton("Lưu")
        self.save_btn.clicked.connect(self.save_image)
        basic_layout.addWidget(self.save_btn)
        
        controls_layout.addWidget(basic_group)
        
        # Adjustments group
        adjust_group = QGroupBox("Điều chỉnh")
        adjust_layout = QVBoxLayout(adjust_group)
        
        # Brightness slider
        brightness_label = QLabel("Độ sáng")
        adjust_layout.addWidget(brightness_label)
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(10, 200)
        self.brightness_slider.setValue(100)
        self.brightness_slider.valueChanged.connect(self.adjust_brightness)
        adjust_layout.addWidget(self.brightness_slider)
        
        # Contrast button and slider
        self.contrast_btn = QPushButton("Điều chỉnh tương phản")
        self.contrast_btn.clicked.connect(self.adjust_contrast)
        adjust_layout.addWidget(self.contrast_btn)
        
        contrast_label = QLabel("Độ tương phản")
        adjust_layout.addWidget(contrast_label)
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(10, 200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.valueChanged.connect(self.update_contrast)
        adjust_layout.addWidget(self.contrast_slider)
        
        # Blur button and slider
        self.blur_btn = QPushButton("Làm mờ")
        self.blur_btn.clicked.connect(self.blur)
        adjust_layout.addWidget(self.blur_btn)
        
        blur_label = QLabel("Mức độ làm mờ")
        adjust_layout.addWidget(blur_label)
        self.blur_slider = QSlider(Qt.Orientation.Horizontal)
        self.blur_slider.setRange(1, 10)
        self.blur_slider.setValue(1)
        self.blur_slider.valueChanged.connect(self.update_blur)
        adjust_layout.addWidget(self.blur_slider)
        
        # Saturation slider
        saturation_label = QLabel("Độ bão hòa")
        adjust_layout.addWidget(saturation_label)
        self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setRange(10, 200)
        self.saturation_slider.setValue(100)
        self.saturation_slider.valueChanged.connect(self.update_saturation)
        adjust_layout.addWidget(self.saturation_slider)
        
        # Crop and text buttons
        self.crop_btn = QPushButton("Cắt ảnh")
        self.crop_btn.clicked.connect(self.start_crop)
        adjust_layout.addWidget(self.crop_btn)
        
        self.random_filter_btn = QPushButton("Bộ lọc ngẫu nhiên")
        self.random_filter_btn.clicked.connect(self.apply_random_filter)
        adjust_layout.addWidget(self.random_filter_btn)
        
        self.text_btn = QPushButton("Chèn văn bản")
        self.text_btn.clicked.connect(self.start_add_text)
        adjust_layout.addWidget(self.text_btn)
        
        controls_layout.addWidget(adjust_group)
        controls_layout.addStretch()
        
        main_layout.addWidget(controls_widget)
        
        # Image display area (right side)
        self.image_canvas = ImageCanvas()
        main_layout.addWidget(self.image_canvas)
        
    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Mở ảnh", "", 
            "Image files (*.png *.jpg *.jpeg *.bmp *.gif);;All files (*.*)"
        )
        if file_path:
            try:
                pil_image = Image.open(file_path)
                self.image_state.set_image(pil_image)
                self.image_canvas.set_image(pil_image)
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể mở ảnh:\n{e}")
    
    def rotate_image(self):
        if self.image_state.image:
            self.image_state.apply(rotate_90)
            self.image_canvas.set_image(self.image_state.image)
    
    def to_grayscale(self):
        if self.image_state.image:
            self.image_state.apply(to_grayscale)
            self.image_canvas.set_image(self.image_state.image)
    
    def undo(self):
        self.image_state.undo()
        self.image_canvas.set_image(self.image_state.image)
    
    def save_image(self):
        if self.image_state.image:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Lưu ảnh", "", 
                "PNG files (*.png);;JPEG files (*.jpg);;BMP files (*.bmp);;All files (*.*)"
            )
            if file_path:
                try:
                    self.image_state.image.save(file_path)
                    QMessageBox.information(self, "Thành công", f"Ảnh đã được lưu tại:\n{file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Lỗi", f"Không thể lưu ảnh:\n{e}")
    
    def adjust_brightness(self, value):
        if self.image_state.history:
            factor = value / 100.0
            base = self.image_state.history[-1]
            brightened = adjust_brightness(base, factor)
            self.image_state.apply(lambda x: brightened)
            self.image_canvas.set_image(self.image_state.image)
    
    def adjust_contrast(self):
        if self.image_state.history:
            self.image_state.apply(lambda img: adjust_contrast(img, self.contrast_slider.value() / 100.0))
            self.image_canvas.set_image(self.image_state.image)
    
    def update_contrast(self, value):
        if self.image_state.history:
            factor = value / 100.0
            base = self.image_state.history[-1]
            contrasted = adjust_contrast(base, factor)
            self.image_state.image = contrasted
            self.image_canvas.set_image(self.image_state.image)
    
    def blur(self):
        if self.image_state.history:
            self.image_state.apply(lambda img: blur(img, self.blur_slider.value()))
            self.image_canvas.set_image(self.image_state.image)
    
    def update_blur(self, value):
        if self.image_state.history:
            radius = value
            base = self.image_state.history[-1]
            blurred = blur(base, radius)
            self.image_state.image = blurred
            self.image_canvas.set_image(self.image_state.image)
    
    def update_saturation(self, value):
        if self.image_state.history:
            factor = value / 100.0
            base = self.image_state.history[-1]
            saturated = adjust_saturation(base, factor)
            self.image_state.apply(lambda x: saturated)
            self.image_canvas.set_image(self.image_state.image)
    
    def start_crop(self):
        if self.image_state.image:
            self.image_canvas.text_mode = False
            self.image_canvas.start_point = None
            self.image_canvas.text_start_point = None
            self.image_canvas.current_rect = None
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            QMessageBox.warning(self, "Lỗi", "Vui lòng mở ảnh trước khi cắt!")
    
    def start_add_text(self):
        if self.image_state.image:
            self.image_canvas.text_mode = True
            self.image_canvas.start_point = None
            self.image_canvas.text_start_point = None
            self.image_canvas.current_rect = None
            self.setCursor(Qt.CursorShape.CrossCursor)
            self.show_text_dialog()
        else:
            QMessageBox.warning(self, "Lỗi", "Vui lòng mở ảnh trước khi chèn văn bản!")
    
    def show_text_dialog(self):
        # Get font name
        font_name, ok = QInputDialog.getText(self, "Chèn văn bản", "Font (ví dụ: arial):", text="arial")
        if not ok:
            return
        self.selected_font = font_name or "arial"
        
        # Get text content
        text, ok = QInputDialog.getText(self, "Chèn văn bản", "Văn bản:")
        if not ok:
            return
        self.selected_text = text or "Text"
        
        # Get font size
        font_size, ok = QInputDialog.getInt(self, "Chèn văn bản", "Kích thước font:", 
                                           value=40, min=10, max=200)
        if not ok:
            return
        self.selected_font_size = font_size
        
        # Get color
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()
    
    def handle_text_placement(self, start_point, end_point):
        if not self.image_state.image:
            return
        
        # Convert canvas coordinates to image coordinates
        img_start = self.image_canvas.get_image_coordinates(start_point)
        if img_start:
            self.image_state.apply(lambda img: add_text_to_image(
                img, self.selected_text, img_start.x(), img_start.y(), 
                self.selected_font, self.selected_font_size, self.selected_color
            ))
            self.image_canvas.set_image(self.image_state.image)
        
        self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def handle_crop(self, start_point, end_point):
        if not self.image_state.image:
            return
        
        # Convert canvas coordinates to image coordinates
        img_start = self.image_canvas.get_image_coordinates(start_point)
        img_end = self.image_canvas.get_image_coordinates(end_point)
        
        if img_start and img_end:
            # Calculate crop rectangle
            left = min(img_start.x(), img_end.x())
            top = min(img_start.y(), img_end.y())
            right = max(img_start.x(), img_end.x())
            bottom = max(img_start.y(), img_end.y())
            
            # Ensure coordinates are within image bounds
            img_width, img_height = self.image_state.image.size
            left = max(0, min(left, img_width))
            top = max(0, min(top, img_height))
            right = max(left, min(right, img_width))
            bottom = max(top, min(bottom, img_height))
            
            # Crop the image
            cropped = self.image_state.image.crop((left, top, right, bottom))
            self.image_state.set_image(cropped)
            self.image_canvas.set_image(cropped)
        
        self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def apply_random_filter(self):
        if self.image_state.history:
            self.image_state.apply(apply_random_filter)
            self.image_canvas.set_image(self.image_state.image)