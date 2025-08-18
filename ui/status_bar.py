from PyQt6.QtWidgets import QStatusBar, QLabel, QProgressBar
from PyQt6.QtCore import Qt

class StatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize status bar components"""
        # Status label
        self.status_label = QLabel("Ready")
        self.addWidget(self.status_label)
        
        # Image info label
        self.image_info_label = QLabel("")
        self.addPermanentWidget(self.image_info_label)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.addPermanentWidget(self.progress_bar)
    
    def update_status(self, message):
        """Update status message"""
        self.status_label.setText(message)
    
    def update_image_info(self, info, zoom_percent=None):
        """Update image information display"""
        if info:
            size = info.get('size', (0, 0))
            mode = info.get('mode', 'Unknown')
            format_name = info.get('format', 'Unknown')
            
            info_text = f"Size: {size[0]}x{size[1]} | Mode: {mode} | Format: {format_name}"
            if zoom_percent is not None:
                info_text += f" | Zoom: {zoom_percent}%"
            self.image_info_label.setText(info_text)
        else:
            self.image_info_label.setText("")
    
    def show_progress(self, visible=True):
        """Show or hide progress bar"""
        self.progress_bar.setVisible(visible)
    
    def set_progress(self, value):
        """Set progress bar value (0-100)"""
        self.progress_bar.setValue(value)
    
    def clear_status(self):
        """Clear status message"""
        self.status_label.setText("Ready")
