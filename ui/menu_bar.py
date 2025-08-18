from PyQt6.QtWidgets import QMenuBar, QMenu, QFileDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence

class MenuBar(QMenuBar):
    # Signals
    open_image = pyqtSignal(str)
    save_image = pyqtSignal(str)
    reset_image = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_menus()
    
    def init_menus(self):
        """Initialize menu items"""
        # File menu
        file_menu = self.addMenu("&File")
        
        # Open action
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Open an image file")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        # Save action
        save_action = QAction("&Save As...", self)
        save_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_action.setStatusTip("Save the current image")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Reset action
        reset_action = QAction("&Reset to Original", self)
        reset_action.setStatusTip("Reset image to original")
        reset_action.triggered.connect(self.reset_image.emit)
        file_menu.addAction(reset_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.parent().close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = self.addMenu("&Edit")
        
        # Undo action
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.setStatusTip("Undo last action")
        undo_action.triggered.connect(self.undo_action)
        edit_menu.addAction(undo_action)
        
        # Redo action
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.setStatusTip("Redo last undone action")
        redo_action.triggered.connect(self.redo_action)
        edit_menu.addAction(redo_action)
        
        # Help menu
        help_menu = self.addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About this application")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def open_file(self):
        """Open file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", 
            "Image files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp);;All files (*.*)"
        )
        if file_path:
            self.open_image.emit(file_path)
    
    def save_file(self):
        """Save file dialog"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "", 
            "PNG files (*.png);;JPEG files (*.jpg);;BMP files (*.bmp);;All files (*.*)"
        )
        if file_path:
            self.save_image.emit(file_path)
    
    def undo_action(self):
        """Undo action"""
        # This will be connected to the main window's undo method
        pass
    
    def redo_action(self):
        """Redo action"""
        # This will be connected to the main window's redo method
        pass
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About Photo Editor",
            "Enhanced Photo Editor v2.0\n\n"
            "A professional photo editing application built with PyQt6.\n"
            "Features include advanced filters, adjustments, and transforms.\n\n"
            "Combined from two photo editor projects for maximum functionality."
        )
