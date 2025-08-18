import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.enhanced_main_window import EnhancedMainWindow

def main():
    # Enable high DPI support (PyQt6 handles this automatically)
    # The old attributes are deprecated in PyQt6
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Enhanced Photo Editor")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Python Project")
    
    # Create and show main window
    window = EnhancedMainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
