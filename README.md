# Enhanced Photo Editor v2.0

A professional photo editing application built with PyQt6 and PIL (Python Imaging Library)

## 🚀  Features

### ✨ Enhanced UI/UX
- **Professional Interface**: Modern PyQt6-based UI with menu bar, status bar, and organized tool panels
- **Responsive Layout**: Resizable splitter with collapsible tool panel
- **Real-time Preview**: Live preview of adjustments as you move sliders
- **Status Bar**: Shows image information and operation status
- **High DPI Support**: Optimized for high-resolution displays

### 🎨 Advanced Adjustments
- **Basic Adjustments**: Brightness, Contrast, Saturation, Sharpness
- **Advanced Adjustments**: Gamma, Exposure, Hue, Color Temperature
- **Auto Adjustments**: Auto Levels, Auto Color
- **Real-time Sliders**: See changes instantly as you adjust

### 🎯 Professional Filters
- **Basic Filters**: Grayscale, Sepia, Blur (with radius control)
- **Advanced Filters**: Sharpen, Edge Enhance, Emboss, Find Edges
- **Special Effects**: Vintage, Random Filter
- **One-click Application**: Instant filter effects

### 🔄 Enhanced Transforms
- **Rotation**: 90°, 180°, 270° rotations
- **Flip**: Horizontal and vertical flipping
- **Scale**: 50% to 200% scaling options
- **Crop**: Interactive crop tool with visual selection

### 🛠️ Professional Tools
- **Crop Tool**: Click and drag to select crop area
- **Text Tool**: Add text with custom fonts, sizes, and colors
- **Undo/Redo**: Full history support (up to 20 operations)
- **Reset**: Return to original image anytime

### 📁 File Management
- **Multiple Formats**: Support for PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP
- **Save Options**: Save in various formats with quality control
- **Image Info**: Display size, mode, and format information

## Installation

1. Make sure you have Python 3.7+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the enhanced application:
```bash
python main.py
```

### How to Use

1. **Open an Image**: Use File → Open or click "Open Image" button
2. **Basic Editing**: Use sliders for real-time adjustments
3. **Apply Filters**: Click filter buttons for instant effects
4. **Transform**: Use rotation, flip, and scale options
5. **Crop**: Click "Crop Tool" then click and drag to select area
6. **Add Text**: Click "Add Text", enter text details, then click where to place it
7. **Save**: Use File → Save As or click "Save Image" button

### Keyboard Shortcuts
- `Ctrl+O`: Open image
- `Ctrl+S`: Save image
- `Ctrl+Z`: Undo
- `Ctrl+Y`: Redo
- `Ctrl+R`: Reset to original

## Technical Details

### Architecture
- **UI Framework**: PyQt6 (migrated from Tkinter)
- **Image Processing**: PIL (Python Imaging Library)
- **Advanced Processing**: NumPy for complex operations
- **Layout**: QSplitter with organized tool panels
- **Image Display**: Custom QWidget-based viewer with scaling

### Key Components
- `main.py`: Application entry point with high DPI support
- `ui/enhanced_main_window.py`: Main window with professional layout
- `ui/enhanced_tool_panel.py`: Comprehensive tool panel with all features
- `ui/menu_bar.py`: Professional menu bar with shortcuts
- `ui/status_bar.py`: Status bar with image information
- `editor/enhanced_image_processor.py`: Advanced image processing engine
- `editor/enhanced_filters.py`: Professional filter collection
- `editor/enhanced_adjustments.py`: Advanced adjustment algorithms
- `editor/enhanced_transforms.py`: Image transformation tools

### Migration Notes
This application successfully combines two photo editor projects:
- **Original App**: Basic PyQt6 photo editor with simple features
- **Friend's App**: Advanced PyQt5 photo editor with professional features
- **Result**: Enhanced PyQt6 photo editor with all features from both

### Performance Improvements
- **Better Memory Management**: Efficient image processing pipeline
- **Real-time Preview**: Instant feedback on adjustments
- **Optimized Rendering**: Smooth image display and scaling
- **Professional UI**: Responsive and intuitive interface

## Requirements

- Python 3.7+
- PyQt6 >= 6.4.0
- Pillow >= 10.0.0
- NumPy >= 1.24.0
- Matplotlib >= 3.7.0
