import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QStatusBar, QMessageBox, QFileDialog,
                             QPushButton, QSlider, QLabel)
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QImage

from .menu_bar import MenuBar
from .enhanced_tool_panel import EnhancedToolPanel
from .status_bar import StatusBar
from editor.enhanced_image_processor import EnhancedImageProcessor

class EnhancedImageViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("QWidget { background-color: #2b2b2b; border: 1px solid #555; }")
        
        # Image display variables
        self.pixmap = None
        self.scaled_pixmap = None
        self.image_rect = None
        # zoom_factor is relative to 'fit' (1.0 = fit to canvas)
        self.zoom_factor = 1.0
        self.fit_scale = 1.0
        self.min_zoom = 0.1  # 10% of fit
        self.max_zoom = 10.0 # 1000% of fit
        
        # Crop and text variables
        self.start_point = None
        self.current_rect = None
        self.text_mode = False
        self.crop_mode = False
        self.text_start_point = None
        self.pending_text = None
        
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
            # Reset zoom to fit on new image
            self.zoom_factor = 1.0
            self.scale_image()
        else:
            self.pixmap = None
            self.scaled_pixmap = None
            self.image_rect = None
        self.update()
    
    def set_preview_image(self, pil_image):
        """Set preview image without affecting zoom"""
        if pil_image:
            if pil_image.mode == "RGBA":
                pil_image = pil_image.convert("RGB")
            
            data = pil_image.convert("RGBA").tobytes("raw", "RGBA")
            qimage = QImage(data, pil_image.size[0], pil_image.size[1], QImage.Format.Format_RGBA8888)
            self.pixmap = QPixmap.fromImage(qimage)
            self.scale_image()
            self.update()
    
    def scale_image(self):
        if self.pixmap:
            # Calculate scaled size based on zoom relative to fit
            canvas_size = self.size()
            img_w = max(1, self.pixmap.width())
            img_h = max(1, self.pixmap.height())

            # Compute fit scale to keep entire image visible
            self.fit_scale = min(canvas_size.width() / img_w, canvas_size.height() / img_h)
            if self.fit_scale <= 0:
                self.fit_scale = 1.0

            # Composite scale
            composite_scale = self.fit_scale * max(self.min_zoom, min(self.zoom_factor, self.max_zoom))

            scaled_width = max(1, int(img_w * composite_scale))
            scaled_height = max(1, int(img_h * composite_scale))

            scaled_pixmap = self.pixmap.scaled(
                scaled_width, scaled_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            self.scaled_pixmap = scaled_pixmap

            # Center the image
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
                if self.text_mode and self.pending_text:
                    # Add text at clicked position
                    img_pos = self.get_image_coordinates(pos)
                    if img_pos:
                        # Find the main window
                        main_window = self.window()
                        if hasattr(main_window, 'add_text_at_position'):
                            main_window.add_text_at_position(
                                self.pending_text[0], img_pos.x(), img_pos.y(),
                                self.pending_text[1], self.pending_text[2], self.pending_text[3]
                            )
                    self.text_mode = False
                    self.pending_text = None
                    self.setCursor(Qt.CursorShape.ArrowCursor)
                elif self.crop_mode:
                    # Only start crop selection if crop mode is active
                    self.start_point = pos
                self.current_rect = None
                self.update()
    
    def mouseMoveEvent(self, event):
        if self.start_point and self.image_rect and self.crop_mode:
            pos = event.pos()
            if self.image_rect.contains(pos):
                self.current_rect = QRect(self.start_point, pos).normalized()
                self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.image_rect and self.start_point and self.crop_mode:
            pos = event.pos()
            if self.image_rect.contains(pos):
                # Handle crop
                img_start = self.get_image_coordinates(self.start_point)
                img_end = self.get_image_coordinates(pos)
                if img_start and img_end:
                    # Find the main window
                    main_window = self.window()
                    if hasattr(main_window, 'crop_image'):
                        main_window.crop_image(img_start, img_end)
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
    
    def set_text_mode(self, text_info):
        """Set text mode with pending text information"""
        self.text_mode = True
        self.crop_mode = False
        self.pending_text = text_info
        self.setCursor(Qt.CursorShape.CrossCursor)
    
    def set_crop_mode(self, enabled):
        """Enable or disable crop mode"""
        self.crop_mode = enabled
        self.text_mode = False
        if enabled:
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.start_point = None
            self.current_rect = None
            self.update()
    
    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Ctrl + Mouse wheel for zoom
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
    
    def zoom_in(self):
        """Zoom in by 25%"""
        if self.pixmap:
            self.zoom_factor = min(self.zoom_factor * 1.25, self.max_zoom)
            self.scale_image()
            self.update()
    
    def zoom_out(self):
        """Zoom out by 25%"""
        if self.pixmap:
            self.zoom_factor = max(self.zoom_factor / 1.25, self.min_zoom)
            self.scale_image()
            self.update()
    
    def zoom_to_fit(self):
        """Reset zoom to fit image in canvas"""
        if self.pixmap:
            self.zoom_factor = 1.0  # 100% of fit
            self.scale_image()
            self.update()
    
    def zoom_to_100(self):
        """Zoom to 100% (actual pixel size)"""
        if self.pixmap:
            # 100% actual pixels relative to fit
            # If fit_scale < 1, need to increase zoom to 1/fit_scale
            self.zoom_factor = max(self.min_zoom, min(self.max_zoom, 1.0 / max(self.fit_scale, 1e-6)))
            self.scale_image()
            self.update()
    
    def get_zoom_percentage(self):
        """Get current zoom (relative to fit) as percentage"""
        return int(round(self.zoom_factor * 100))

class EnhancedMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_processor = EnhancedImageProcessor()
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Enhanced Photo Editor v2.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # Menu bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Tool panel (left)
        self.tool_panel = EnhancedToolPanel(self)
        self.tool_panel.setMaximumWidth(300)
        self.tool_panel.setMinimumWidth(250)
        
        # Right side container for image viewer and zoom controls
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Zoom controls at the top
        self.zoom_controls = self.create_zoom_controls()
        right_layout.addWidget(self.zoom_controls)
        
        # Image viewer (center)
        self.image_viewer = EnhancedImageViewer(self)
        right_layout.addWidget(self.image_viewer)
        
        # Add to splitter
        splitter.addWidget(self.tool_panel)
        splitter.addWidget(right_container)
        splitter.setStretchFactor(0, 0)  # Tool panel fixed
        splitter.setStretchFactor(1, 1)  # Image viewer expandable
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)
    
    def create_zoom_controls(self):
        """Create zoom controls widget for the top of the canvas"""
        zoom_widget = QWidget()
        zoom_widget.setMaximumHeight(44)
        # Dark theme styling for the zoom bar
        zoom_widget.setStyleSheet(
            """
            QWidget { background-color: #1f1f1f; border-bottom: 1px solid #3a3a3a; }
            QPushButton { background: #2b2b2b; color: #ddd; border: 1px solid #3a3a3a; padding: 4px 8px; border-radius: 4px; }
            QPushButton:hover { background: #383838; }
            QLabel { color: #ddd; }
            QSlider::groove:horizontal { background: #3a3a3a; height: 6px; border-radius: 3px; }
            QSlider::handle:horizontal { background: #5a5a5a; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }
            QSlider::sub-page:horizontal { background: #6a6a6a; }
            """
        )
        
        layout = QHBoxLayout(zoom_widget)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Zoom out button
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setToolTip("Zoom Out (Ctrl + Mouse Wheel Down)")
        zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_out_btn.setMaximumWidth(30)
        zoom_out_btn.setMaximumHeight(30)
        layout.addWidget(zoom_out_btn)
        
        # Zoom slider
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 1000)  # 10% to 1000% (relative to fit)
        self.zoom_slider.setValue(100)  # 100% of fit
        self.zoom_slider.setToolTip("Drag to zoom")
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_changed)
        layout.addWidget(self.zoom_slider)
        
        # Zoom in button
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setToolTip("Zoom In (Ctrl + Mouse Wheel Up)")
        zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_in_btn.setMaximumWidth(30)
        zoom_in_btn.setMaximumHeight(30)
        layout.addWidget(zoom_in_btn)
        
        # Zoom percentage label
        self.zoom_percentage_label = QLabel("100%")
        self.zoom_percentage_label.setMinimumWidth(50)
        self.zoom_percentage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_percentage_label.setStyleSheet("QLabel { font-weight: bold; }")
        layout.addWidget(self.zoom_percentage_label)
        
        # Fit button
        fit_btn = QPushButton("Fit")
        fit_btn.setToolTip("Fit to Canvas")
        fit_btn.clicked.connect(self.zoom_to_fit)
        fit_btn.setMaximumHeight(30)
        layout.addWidget(fit_btn)
        
        # Center the zoom controls
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        return zoom_widget
    
    def on_zoom_slider_changed(self, value):
        """Handle zoom slider changes"""
        self.zoom_percentage_label.setText(f"{value}%")
        self.zoom_to_percentage(value)
        
    def connect_signals(self):
        """Connect signals between components"""
        # Menu bar signals
        self.menu_bar.open_image.connect(self.open_image)
        self.menu_bar.save_image.connect(self.save_image)
        self.menu_bar.reset_image.connect(self.reset_image)
        
        # Tool panel signals
        self.tool_panel.filter_applied.connect(self.apply_filter)
        self.tool_panel.adjustment_applied.connect(self.apply_adjustment)
        self.tool_panel.adjustment_preview.connect(self.preview_adjustments)
        self.tool_panel.transform_applied.connect(self.apply_transform)
        self.tool_panel.text_added.connect(self.start_add_text)
        self.tool_panel.file_open_requested.connect(lambda: self.open_image())
        self.tool_panel.file_save_requested.connect(lambda: self.save_image())
        self.tool_panel.file_reset_requested.connect(self.reset_image)
        self.tool_panel.crop_requested.connect(self.start_crop)
        # Zoom signals (now connected to the zoom controls at the top)
        # Note: Zoom controls are now in the main window, not tool panel
        
        # Remove legacy direct method assignments; signals are used instead
        
    def open_image(self, file_path=None):
        """Open image file"""
        if file_path is None:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Image", "", 
                "Image files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp);;All files (*.*)"
            )
        
        if file_path:
            try:
                if self.image_processor.load_image(file_path):
                    self.image_viewer.set_image(self.image_processor.get_current_image())
                    self.status_bar.update_status(f"Loaded: {file_path}")
                    
                    # Update image info in status bar
                    image_info = self.image_processor.get_image_info()
                    if image_info:
                        zoom_percent = self.image_viewer.get_zoom_percentage()
                        self.status_bar.update_image_info(image_info, zoom_percent)
                else:
                    QMessageBox.critical(self, "Error", "Could not load image file.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading image:\n{e}")
    
    def save_image(self, file_path=None):
        """Save current image"""
        if file_path is None:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Image", "", 
                "PNG files (*.png);;JPEG files (*.jpg);;BMP files (*.bmp);;All files (*.*)"
            )
        
        if file_path:
            try:
                if self.image_processor.save_image(file_path):
                    self.status_bar.update_status(f"Saved: {file_path}")
                else:
                    QMessageBox.critical(self, "Error", "Could not save image file.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving image:\n{e}")
    
    def reset_image(self):
        """Reset to original image"""
        if self.image_processor.reset_to_original():
            self.image_viewer.set_image(self.image_processor.get_current_image())
            self.status_bar.update_status("Reset to original image")
    
    def apply_filter(self, filter_name, params=None):
        """Apply filter to current image"""
        if self.image_processor.apply_filter(filter_name, params):
            self.image_viewer.set_image(self.image_processor.get_current_image())
            self.status_bar.update_status(f"Applied filter: {filter_name}")
    
    def apply_adjustment(self, adjustment_name, value):
        """Apply adjustment to current image"""
        if self.image_processor.apply_adjustment(adjustment_name, value):
            self.image_viewer.set_image(self.image_processor.get_current_image())
            self.status_bar.update_status(f"Applied adjustment: {adjustment_name}")
    
    def preview_adjustments(self, adjustments):
        """Preview adjustments without modifying the actual image"""
        if self.image_processor.get_current_image():
            preview_image = self.image_processor.get_preview_with_adjustments(adjustments)
            if preview_image:
                self.image_viewer.set_preview_image(preview_image)
    
    def apply_transform(self, transform_name, params):
        """Apply transform to current image"""
        if self.image_processor.apply_transform(transform_name, params):
            self.image_viewer.set_image(self.image_processor.get_current_image())
            self.status_bar.update_status(f"Applied transform: {transform_name}")
    
    def start_crop(self):
        """Start crop tool"""
        if self.image_processor.get_current_image():
            self.image_viewer.set_crop_mode(True)
            self.status_bar.update_status("Crop tool activated - click and drag to select area")
        else:
            QMessageBox.warning(self, "Warning", "Please open an image first!")
    
    def crop_image(self, start_point, end_point):
        """Crop image based on selected area"""
        left = min(start_point.x(), end_point.x())
        top = min(start_point.y(), end_point.y())
        right = max(start_point.x(), end_point.x())
        bottom = max(start_point.y(), end_point.y())
        
        if self.image_processor.apply_transform('crop', {'box': [left, top, right, bottom]}):
            self.image_viewer.set_image(self.image_processor.get_current_image())
            self.image_viewer.set_crop_mode(False)  # Exit crop mode after cropping
            self.status_bar.update_status("Image cropped")
    
    def start_add_text(self, text, x, y, font_name, font_size, color):
        """Start text addition mode"""
        if self.image_processor.get_current_image():
            self.image_viewer.set_crop_mode(False)  # Exit crop mode when starting text tool
            self.image_viewer.set_text_mode((text, font_name, font_size, color))
            self.status_bar.update_status("Text tool activated - click where you want to place text")
        else:
            QMessageBox.warning(self, "Warning", "Please open an image first!")
    
    def add_text_at_position(self, text, x, y, font_name, font_size, color):
        """Add text at specific position"""
        if self.image_processor.add_text(text, x, y, font_name, font_size, color):
            self.image_viewer.set_image(self.image_processor.get_current_image())
            self.status_bar.update_status("Text added to image")
    
    def undo(self):
        """Undo last operation"""
        if self.image_processor.undo():
            self.image_viewer.set_image(self.image_processor.get_current_image())
            self.status_bar.update_status("Undo completed")
    
    def redo(self):
        """Redo last undone operation"""
        if self.image_processor.redo():
            self.image_viewer.set_image(self.image_processor.get_current_image())
            self.status_bar.update_status("Redo completed")
    
    def zoom_in(self):
        """Zoom in the image viewer"""
        self.image_viewer.zoom_in()
        zoom_percent = self.image_viewer.get_zoom_percentage()
        self.status_bar.update_status(f"Zoomed in to {zoom_percent}%")
        # Update image info with new zoom
        image_info = self.image_processor.get_image_info()
        if image_info:
            self.status_bar.update_image_info(image_info, zoom_percent)
        # Update zoom slider
        self.update_zoom_slider(zoom_percent)
    
    def zoom_out(self):
        """Zoom out the image viewer"""
        self.image_viewer.zoom_out()
        zoom_percent = self.image_viewer.get_zoom_percentage()
        self.status_bar.update_status(f"Zoomed out to {zoom_percent}%")
        # Update image info with new zoom
        image_info = self.image_processor.get_image_info()
        if image_info:
            self.status_bar.update_image_info(image_info, zoom_percent)
        # Update zoom slider
        self.update_zoom_slider(zoom_percent)
    
    def zoom_to_fit(self):
        """Zoom to fit image in canvas"""
        self.image_viewer.zoom_to_fit()
        self.status_bar.update_status("Zoomed to fit canvas")
        # Update image info with new zoom
        image_info = self.image_processor.get_image_info()
        if image_info:
            zoom_percent = self.image_viewer.get_zoom_percentage()
            self.status_bar.update_image_info(image_info, zoom_percent)
        # Update zoom slider
        self.update_zoom_slider(zoom_percent)
    
    def zoom_to_100(self):
        """Zoom to 100% (actual pixel size)"""
        self.image_viewer.zoom_to_100()
        self.status_bar.update_status("Zoomed to 100% (actual size)")
        # Update image info with new zoom
        image_info = self.image_processor.get_image_info()
        if image_info:
            zoom_percent = self.image_viewer.get_zoom_percentage()
            self.status_bar.update_image_info(image_info, zoom_percent)
        # Update zoom slider
        self.update_zoom_slider(100)
    
    def zoom_to_percentage(self, percentage):
        """Zoom to specific percentage"""
        if self.image_viewer.pixmap:
            # Convert percentage to zoom factor
            zoom_factor = percentage / 100.0
            self.image_viewer.zoom_factor = zoom_factor
            self.image_viewer.scale_image()
            self.image_viewer.update()
            
            self.status_bar.update_status(f"Zoomed to {percentage}%")
            # Update image info with new zoom
            image_info = self.image_processor.get_image_info()
            if image_info:
                self.status_bar.update_image_info(image_info, percentage)
    
    def update_zoom_slider(self, percentage):
        """Update zoom slider without triggering zoom change"""
        if hasattr(self, 'zoom_slider'):
            # Temporarily disconnect to avoid feedback loop
            self.zoom_slider.valueChanged.disconnect()
            self.zoom_slider.setValue(percentage)
            self.zoom_percentage_label.setText(f"{percentage}%")
            # Reconnect
            self.zoom_slider.valueChanged.connect(self.on_zoom_slider_changed)
