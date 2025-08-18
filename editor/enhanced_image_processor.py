from PIL import Image, ImageDraw, ImageFont
import os
import sys
from typing import Optional

try:
    # Optional but recommended for resolving system font paths by family name
    import matplotlib.font_manager as fm  # type: ignore
except Exception:  # pragma: no cover
    fm = None
from .enhanced_filters import EnhancedFilters
from .enhanced_adjustments import EnhancedAdjustments
from .enhanced_transforms import EnhancedTransforms

class EnhancedImageProcessor:
    def __init__(self):
        self.original_image = None
        self.current_image = None
        self.history = []
        self.history_index = -1
        self.max_history = 20
        
    def load_image(self, file_path):
        """Load image from file"""
        try:
            image = Image.open(file_path)
            # Convert to RGB if necessary
            if image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGB')
            elif image.mode == 'RGBA':
                # Create white background for RGBA images
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                image = background
            
            self.original_image = image.copy()
            self.current_image = image.copy()
            self.history = [image.copy()]
            self.history_index = 0
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def save_image(self, file_path):
        """Save current image to file"""
        try:
            if self.current_image:
                self.current_image.save(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    def get_current_image(self):
        """Get current image"""
        return self.current_image
    
    def get_original_image(self):
        """Get original image"""
        return self.original_image
    
    def get_image_info(self):
        """Get image information"""
        if self.current_image:
            return {
                'size': self.current_image.size,
                'mode': self.current_image.mode,
                'format': getattr(self.current_image, 'format', 'Unknown')
            }
        return None
    
    def apply_filter(self, filter_name, params=None):
        """Apply filter to current image"""
        if not self.current_image:
            return False
        
        try:
            result = EnhancedFilters.apply(self.current_image, filter_name, params)
            if result:
                self._add_to_history(result)
                return True
            return False
        except Exception as e:
            print(f"Error applying filter {filter_name}: {e}")
            return False
    
    def apply_adjustment(self, adjustment_name, value):
        """Apply adjustment to current image"""
        if not self.current_image:
            return False
        
        try:
            result = EnhancedAdjustments.apply(self.current_image, adjustment_name, value)
            if result:
                self._add_to_history(result)
                return True
            return False
        except Exception as e:
            print(f"Error applying adjustment {adjustment_name}: {e}")
            return False
    
    def apply_transform(self, transform_name, params):
        """Apply transform to current image"""
        if not self.current_image:
            return False
        
        try:
            result = EnhancedTransforms.apply(self.current_image, transform_name, params)
            if result:
                self._add_to_history(result)
                return True
            return False
        except Exception as e:
            print(f"Error applying transform {transform_name}: {e}")
            return False
    
    def add_text(self, text, x, y, font_name="arial", font_size=40, color="#FFFFFF"):
        """Add text to image"""
        if not self.current_image:
            return False
        
        try:
            new_image = self.current_image.copy()
            draw = ImageDraw.Draw(new_image)

            def _resolve_font_path(name: str) -> Optional[str]:
                """Try to resolve a TTF/OTF font path from a family or filename."""
                if not name:
                    return None

                # If user passed a direct path
                if os.path.sep in name or name.lower().endswith((".ttf", ".otf")):
                    return name if os.path.exists(name) else None

                # Common Windows fonts location
                windows_fonts = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
                candidates = [
                    os.path.join(windows_fonts, f"{name}.ttf"),
                    os.path.join(windows_fonts, f"{name}.otf"),
                    os.path.join(windows_fonts, f"{name.lower()}.ttf"),
                    os.path.join(windows_fonts, f"{name.lower()}.otf"),
                ]
                for path in candidates:
                    if os.path.exists(path):
                        return path

                # Try relative to cwd
                for ext in (".ttf", ".otf"):
                    local_path = f"{name}{ext}"
                    if os.path.exists(local_path):
                        return local_path

                # Try matplotlib's font lookup if available
                if fm is not None:
                    try:
                        prop = fm.FontProperties(family=name)
                        font_path = fm.findfont(prop, fallback_to_default=True)
                        if font_path and os.path.exists(font_path):
                            return font_path
                    except Exception:
                        pass

                return None

            # Resolve font path and load a scalable font so size is respected
            resolved_path = _resolve_font_path(font_name)
            font = None
            if resolved_path:
                try:
                    font = ImageFont.truetype(resolved_path, int(font_size))
                except Exception:
                    font = None

            if font is None:
                # Try a very common bundled font in Pillow
                try:
                    font = ImageFont.truetype("DejaVuSans.ttf", int(font_size))
                except Exception:
                    font = None

            if font is None:
                # Last resort (bitmap, ignores size but prevents crash)
                font = ImageFont.load_default()
            
            # Add text with outline
            outline_color = "black"
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                draw.text((x + dx, y + dy), text, fill=outline_color, font=font)
            draw.text((x, y), text, fill=color, font=font)
            
            self._add_to_history(new_image)
            return True
        except Exception as e:
            print(f"Error adding text: {e}")
            return False
    
    def reset_to_original(self):
        """Reset to original image"""
        if self.original_image:
            self._add_to_history(self.original_image.copy())
            return True
        return False
    
    def undo(self):
        """Undo last operation"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.history[self.history_index].copy()
            return True
        return False
    
    def redo(self):
        """Redo last undone operation"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_image = self.history[self.history_index].copy()
            return True
        return False
    
    def can_undo(self):
        """Check if undo is possible"""
        return self.history_index > 0
    
    def can_redo(self):
        """Check if redo is possible"""
        return self.history_index < len(self.history) - 1
    
    def _add_to_history(self, image):
        """Add image to history"""
        # Remove any redo history if we're not at the end
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        self.history.append(image.copy())
        self.history_index += 1
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.history_index -= 1
        
        self.current_image = image.copy()
    
    def get_preview_with_adjustments(self, adjustments):
        """Get preview with adjustments without modifying history"""
        if not self.current_image:
            return None
        
        try:
            preview_image = self.current_image.copy()
            
            for adjustment_name, value in adjustments.items():
                try:
                    result = EnhancedAdjustments.apply(preview_image, adjustment_name, value)
                    if result:
                        preview_image = result
                except Exception as adj_error:
                    # Silently skip problematic adjustments in preview
                    continue
            
            return preview_image
        except Exception as e:
            # Return original image if preview fails
            return self.current_image.copy()
