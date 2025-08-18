from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QSlider, QGroupBox, QScrollArea, QFrame,
                             QSpinBox, QComboBox, QColorDialog, QInputDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

class EnhancedToolPanel(QWidget):
    # Signals
    filter_applied = pyqtSignal(str, dict)  # filter_name, params
    adjustment_applied = pyqtSignal(str, float)  # adjustment_name, value
    adjustment_preview = pyqtSignal(dict)  # adjustments dict
    transform_applied = pyqtSignal(str, dict)  # transform_name, params
    text_added = pyqtSignal(str, int, int, str, int, str)  # text, x, y, font, size, color
    # File/tool requests
    file_open_requested = pyqtSignal()
    file_save_requested = pyqtSignal()
    file_reset_requested = pyqtSignal()
    crop_requested = pyqtSignal()

    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.connect_signals()
        
        # Store current adjustment values for preview
        self.current_adjustments = {}
    
    def init_ui(self):
        """Initialize user interface"""
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create scroll area for tool panel
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create widget to hold all controls
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # File operations group
        file_group = self.create_file_group()
        content_layout.addWidget(file_group)
        
        # Basic adjustments group
        basic_group = self.create_basic_adjustments_group()
        content_layout.addWidget(basic_group)
        
        # Advanced adjustments group
        advanced_group = self.create_advanced_adjustments_group()
        content_layout.addWidget(advanced_group)
        
        # Filters group
        filters_group = self.create_filters_group()
        content_layout.addWidget(filters_group)
        
        # Transforms group
        transforms_group = self.create_transforms_group()
        content_layout.addWidget(transforms_group)
        
        # Tools group
        tools_group = self.create_tools_group()
        content_layout.addWidget(tools_group)
        
        # Add stretch to push everything to the top
        content_layout.addStretch()
        
        # Set the content widget
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
    
    def create_file_group(self):
        """Create file operations group"""
        group = QGroupBox("File Operations")
        layout = QVBoxLayout(group)
        
        # Open button
        open_btn = QPushButton("Open Image")
        open_btn.clicked.connect(self.file_open_requested.emit)
        layout.addWidget(open_btn)
        
        # Save button
        save_btn = QPushButton("Save Image")
        save_btn.clicked.connect(self.file_save_requested.emit)
        layout.addWidget(save_btn)
        
        # Reset button
        reset_btn = QPushButton("Reset to Original")
        reset_btn.clicked.connect(self.file_reset_requested.emit)
        layout.addWidget(reset_btn)
        
        return group
    
    def create_basic_adjustments_group(self):
        """Create basic adjustments group"""
        group = QGroupBox("Basic Adjustments")
        layout = QVBoxLayout(group)
        
        # Brightness
        brightness_label = QLabel("Brightness")
        layout.addWidget(brightness_label)
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 200)
        self.brightness_slider.setValue(100)
        self.brightness_slider.setToolTip("0-200% (100 = normal)")
        layout.addWidget(self.brightness_slider)
        
        # Contrast
        contrast_label = QLabel("Contrast")
        layout.addWidget(contrast_label)
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(0, 200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.setToolTip("0-200% (100 = normal)")
        layout.addWidget(self.contrast_slider)
        
        # Saturation
        saturation_label = QLabel("Saturation")
        layout.addWidget(saturation_label)
        self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setRange(0, 200)
        self.saturation_slider.setValue(100)
        self.saturation_slider.setToolTip("0-200% (100 = normal)")
        layout.addWidget(self.saturation_slider)
        
        # Sharpness
        sharpness_label = QLabel("Sharpness")
        layout.addWidget(sharpness_label)
        self.sharpness_slider = QSlider(Qt.Orientation.Horizontal)
        self.sharpness_slider.setRange(0, 200)
        self.sharpness_slider.setValue(100)
        self.sharpness_slider.setToolTip("0-200% (100 = normal)")
        layout.addWidget(self.sharpness_slider)
        
        return group
    
    def create_advanced_adjustments_group(self):
        """Create advanced adjustments group"""
        group = QGroupBox("Advanced Adjustments")
        layout = QVBoxLayout(group)
        
        # Gamma
        gamma_label = QLabel("Gamma")
        layout.addWidget(gamma_label)
        self.gamma_slider = QSlider(Qt.Orientation.Horizontal)
        self.gamma_slider.setRange(10, 300)
        self.gamma_slider.setValue(100)
        self.gamma_slider.setToolTip("0.1-3.0 (1.0 = normal)")
        layout.addWidget(self.gamma_slider)
        
        # Exposure
        exposure_label = QLabel("Exposure")
        layout.addWidget(exposure_label)
        self.exposure_slider = QSlider(Qt.Orientation.Horizontal)
        self.exposure_slider.setRange(-30, 30)
        self.exposure_slider.setValue(0)
        self.exposure_slider.setToolTip("-3.0 to +3.0 stops")
        layout.addWidget(self.exposure_slider)
        
        # Hue
        hue_label = QLabel("Hue")
        layout.addWidget(hue_label)
        self.hue_slider = QSlider(Qt.Orientation.Horizontal)
        self.hue_slider.setRange(-180, 180)
        self.hue_slider.setValue(0)
        self.hue_slider.setToolTip("-180 to +180 degrees")
        layout.addWidget(self.hue_slider)
        
        # Temperature
        temp_label = QLabel("Color Temperature")
        layout.addWidget(temp_label)
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(-100, 100)
        self.temp_slider.setValue(0)
        self.temp_slider.setToolTip("-100 (cool) to +100 (warm)")
        layout.addWidget(self.temp_slider)
        
        # Auto adjustments
        auto_layout = QHBoxLayout()
        auto_levels_btn = QPushButton("Auto Levels")
        auto_levels_btn.clicked.connect(lambda: self.apply_auto_adjustment('auto_levels'))
        auto_layout.addWidget(auto_levels_btn)
        
        auto_color_btn = QPushButton("Auto Color")
        auto_color_btn.clicked.connect(lambda: self.apply_auto_adjustment('auto_color'))
        auto_layout.addWidget(auto_color_btn)
        
        layout.addLayout(auto_layout)
        
        return group
    
    def create_filters_group(self):
        """Create filters group"""
        group = QGroupBox("Filters")
        layout = QVBoxLayout(group)
        
        # Basic filters
        basic_filters_layout = QHBoxLayout()
        
        grayscale_btn = QPushButton("Grayscale")
        grayscale_btn.clicked.connect(lambda: self.apply_filter('grayscale'))
        basic_filters_layout.addWidget(grayscale_btn)
        
        sepia_btn = QPushButton("Sepia")
        sepia_btn.clicked.connect(lambda: self.apply_filter('sepia'))
        basic_filters_layout.addWidget(sepia_btn)
        
        layout.addLayout(basic_filters_layout)
        
        # Blur with radius
        blur_layout = QHBoxLayout()
        blur_btn = QPushButton("Blur")
        blur_btn.clicked.connect(self.apply_blur)
        blur_layout.addWidget(blur_btn)
        
        self.blur_radius_spin = QSpinBox()
        self.blur_radius_spin.setRange(1, 10)
        self.blur_radius_spin.setValue(2)
        blur_layout.addWidget(self.blur_radius_spin)
        
        layout.addLayout(blur_layout)
        
        # Advanced filters
        advanced_filters_layout = QHBoxLayout()
        
        sharpen_btn = QPushButton("Sharpen")
        sharpen_btn.clicked.connect(lambda: self.apply_filter('sharpen'))
        advanced_filters_layout.addWidget(sharpen_btn)
        
        edge_btn = QPushButton("Edge Enhance")
        edge_btn.clicked.connect(lambda: self.apply_filter('edge_enhance'))
        advanced_filters_layout.addWidget(edge_btn)
        
        layout.addLayout(advanced_filters_layout)
        
        # More filters
        more_filters_layout = QHBoxLayout()
        
        emboss_btn = QPushButton("Emboss")
        emboss_btn.clicked.connect(lambda: self.apply_filter('emboss'))
        more_filters_layout.addWidget(emboss_btn)
        
        find_edges_btn = QPushButton("Find Edges")
        find_edges_btn.clicked.connect(lambda: self.apply_filter('find_edges'))
        more_filters_layout.addWidget(find_edges_btn)
        
        layout.addLayout(more_filters_layout)
        
        # Special effects
        effects_layout = QHBoxLayout()
        
        vintage_btn = QPushButton("Vintage")
        vintage_btn.clicked.connect(lambda: self.apply_filter('vintage'))
        effects_layout.addWidget(vintage_btn)
        
        random_btn = QPushButton("Random")
        random_btn.clicked.connect(lambda: self.apply_filter('random_filter'))
        effects_layout.addWidget(random_btn)
        
        layout.addLayout(effects_layout)
        
        return group
    
    def create_transforms_group(self):
        """Create transforms group"""
        group = QGroupBox("Transforms")
        layout = QVBoxLayout(group)
        
        # Rotation
        rotation_layout = QHBoxLayout()
        rotate_90_btn = QPushButton("Rotate 90°")
        rotate_90_btn.clicked.connect(lambda: self.apply_transform('rotate', {'angle': 90}))
        rotation_layout.addWidget(rotate_90_btn)
        
        rotate_180_btn = QPushButton("Rotate 180°")
        rotate_180_btn.clicked.connect(lambda: self.apply_transform('rotate', {'angle': 180}))
        rotation_layout.addWidget(rotate_180_btn)
        
        layout.addLayout(rotation_layout)
        
        # Flip
        flip_layout = QHBoxLayout()
        flip_h_btn = QPushButton("Flip H")
        flip_h_btn.clicked.connect(lambda: self.apply_transform('flip', {'direction': 'horizontal'}))
        flip_layout.addWidget(flip_h_btn)
        
        flip_v_btn = QPushButton("Flip V")
        flip_v_btn.clicked.connect(lambda: self.apply_transform('flip', {'direction': 'vertical'}))
        flip_layout.addWidget(flip_v_btn)
        
        layout.addLayout(flip_layout)
        
        # Scale
        scale_layout = QHBoxLayout()
        scale_label = QLabel("Scale:")
        scale_layout.addWidget(scale_label)
        
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(['50%', '75%', '100%', '125%', '150%', '200%'])
        self.scale_combo.setCurrentText('100%')
        scale_layout.addWidget(self.scale_combo)
        
        scale_btn = QPushButton("Apply")
        scale_btn.clicked.connect(self.apply_scale)
        scale_layout.addWidget(scale_btn)
        
        layout.addLayout(scale_layout)
        
        return group
    
    def create_tools_group(self):
        """Create tools group"""
        group = QGroupBox("Tools")
        layout = QVBoxLayout(group)
        
        # Crop tool
        crop_btn = QPushButton("Crop Tool")
        crop_btn.clicked.connect(self.crop_requested.emit)
        layout.addWidget(crop_btn)
        
        # Text tool
        text_btn = QPushButton("Add Text")
        text_btn.clicked.connect(self.add_text)
        layout.addWidget(text_btn)
        
        return group
    
    def connect_signals(self):
        """Connect slider signals for real-time preview"""
        # Connect basic adjustment sliders
        self.brightness_slider.valueChanged.connect(
            lambda v: self.on_adjustment_changed('brightness', v / 100.0))
        self.contrast_slider.valueChanged.connect(
            lambda v: self.on_adjustment_changed('contrast', v / 100.0))
        self.saturation_slider.valueChanged.connect(
            lambda v: self.on_adjustment_changed('saturation', v / 100.0))
        self.sharpness_slider.valueChanged.connect(
            lambda v: self.on_adjustment_changed('sharpness', v / 100.0))
        
        # Connect advanced adjustment sliders
        self.gamma_slider.valueChanged.connect(
            lambda v: self.on_adjustment_changed('gamma', v / 100.0))
        self.exposure_slider.valueChanged.connect(
            lambda v: self.on_adjustment_changed('exposure', v / 10.0))
        self.hue_slider.valueChanged.connect(
            lambda v: self.on_adjustment_changed('hue', v))
        self.temp_slider.valueChanged.connect(
            lambda v: self.on_adjustment_changed('temperature', v))
    
    def on_adjustment_changed(self, adjustment_name, value):
        """Handle adjustment slider changes"""
        self.current_adjustments[adjustment_name] = value
        self.adjustment_preview.emit(self.current_adjustments.copy())
    
    def apply_filter(self, filter_name, params=None):
        """Apply filter"""
        if params is None:
            params = {}
        self.filter_applied.emit(filter_name, params)
    
    def apply_blur(self):
        """Apply blur with radius"""
        radius = self.blur_radius_spin.value()
        self.apply_filter('blur', {'radius': radius})
    
    def apply_scale(self):
        """Apply scale transform"""
        scale_text = self.scale_combo.currentText()
        scale_factor = float(scale_text.replace('%', '')) / 100.0
        self.apply_transform('scale', {'factor': scale_factor})
    
    def apply_transform(self, transform_name, params):
        """Apply transform"""
        self.transform_applied.emit(transform_name, params)
    
    def apply_auto_adjustment(self, adjustment_name):
        """Apply auto adjustment"""
        self.adjustment_applied.emit(adjustment_name, 0.0)
    
    def open_image(self):
        """Open image (will be connected to main window)"""
        pass
    
    def save_image(self):
        """Save image (will be connected to main window)"""
        pass
    
    def reset_image(self):
        """Reset image (will be connected to main window)"""
        pass
    
    def start_crop(self):
        """Start crop tool (will be connected to main window)"""
        pass
    
    def add_text(self):
        """Add text dialog"""
        text, ok = QInputDialog.getText(self, "Add Text", "Enter text:")
        if ok and text:
            # Get font size
            font_size, ok = QInputDialog.getInt(self, "Font Size", "Font size:", 40, 10, 200)
            if ok:
                # Get color
                color = QColorDialog.getColor()
                if color.isValid():
                    # Emit signal with default position (will be set by click)
                    self.text_added.emit(text, 0, 0, "arial", font_size, color.name())
