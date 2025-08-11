from tkinter import *
from tkinter import filedialog, simpledialog, Toplevel, Label, Entry, Button, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
from editor.image_state import ImageState
from editor.image_utils import *
from tkinter import messagebox

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Editor")
        self.root.geometry("1000x600")  # Kích thước mặc định trước khi maximize
        self.root.state('zoomed')  # Maximize cửa sổ khi khởi động
        self.image_state = ImageState()

        # Biến trạng thái cho crop và text, đặt lại mặc định
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.image_id = None
        self.text_start_x = None
        self.text_start_y = None
        self.text_mode = False

        # Frame chính để chứa toàn bộ giao diện
        self.main_frame = Frame(root)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Frame điều khiển (trái)
        self.controls_frame = Frame(self.main_frame, width=200)
        self.controls_frame.pack(side=LEFT, fill=Y, padx=5)

        # Nhóm nút chức năng cơ bản
        self.basic_controls = LabelFrame(self.controls_frame, text="Chức năng cơ bản", padx=5, pady=5)
        self.basic_controls.pack(fill=X, pady=5)
        Button(self.basic_controls, text="Mở ảnh", command=self.open_image).pack(fill=X, pady=2)
        Button(self.basic_controls, text="Xoay 90°", command=self.rotate_image).pack(fill=X, pady=2)
        Button(self.basic_controls, text="Trắng đen", command=self.to_grayscale).pack(fill=X, pady=2)
        Button(self.basic_controls, text="Undo", command=self.undo).pack(fill=X, pady=2)
        Button(self.basic_controls, text="Lưu", command=self.save_image).pack(fill=X, pady=2)

        # Nhóm điều chỉnh ảnh
        self.adjust_controls = LabelFrame(self.controls_frame, text="Điều chỉnh", padx=5, pady=5)
        self.adjust_controls.pack(fill=X, pady=5)
        self.brightness_scale = Scale(self.adjust_controls, from_=0.1, to=2.0, resolution=0.1,
                                     orient=HORIZONTAL, label="Độ sáng", command=self.adjust_brightness)
        self.brightness_scale.set(1.0)
        self.brightness_scale.pack(fill=X, pady=5)
        Button(self.adjust_controls, text="Điều chỉnh tương phản", command=self.adjust_contrast).pack(fill=X, pady=2)
        self.contrast_scale = Scale(self.adjust_controls, from_=0.1, to=2.0, resolution=0.1,
                                    orient=HORIZONTAL, label="Độ tương phản", command=self.update_contrast)
        self.contrast_scale.set(1.0)
        self.contrast_scale.pack(fill=X, pady=5)
        Button(self.adjust_controls, text="Làm mờ", command=self.blur).pack(fill=X, pady=2)
        self.blur_scale = Scale(self.adjust_controls, from_=1, to=10, resolution=1,
                               orient=HORIZONTAL, label="Mức độ làm mờ", command=self.update_blur)
        self.blur_scale.set(1)
        self.blur_scale.pack(fill=X, pady=5)
        self.saturation_scale = Scale(self.adjust_controls, from_=0.1, to=2.0, resolution=0.1,
                                     orient=HORIZONTAL, label="Độ bão hòa", command=self.update_saturation)
        self.saturation_scale.set(1.0)
        self.saturation_scale.pack(fill=X, pady=5)
        Button(self.adjust_controls, text="Cắt ảnh", command=self.start_crop).pack(fill=X, pady=2)
        Button(self.adjust_controls, text="Bộ lọc ngẫu nhiên", command=self.apply_random_filter).pack(fill=X, pady=2)
        Button(self.adjust_controls, text="Chèn văn bản", command=self.start_add_text).pack(fill=X, pady=2)

        # Frame hiển thị ảnh (phải) với thanh cuộn
        self.image_frame = Frame(self.main_frame)
        self.image_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=5)

        # Canvas để hiển thị ảnh với thanh cuộn
        self.canvas = Canvas(self.image_frame, bg="gray")
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        # Thanh cuộn ngang và dọc
        self.h_scroll = Scrollbar(self.image_frame, orient=HORIZONTAL, command=self.canvas.xview)
        self.h_scroll.pack(side=BOTTOM, fill=X)
        self.v_scroll = Scrollbar(self.image_frame, orient=VERTICAL, command=self.canvas.yview)
        self.v_scroll.pack(side=RIGHT, fill=Y)

        self.canvas.config(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        # Sự kiện thay đổi kích thước ảnh
        self.canvas.bind("<Configure>", self.update_scroll_region)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_crop_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def open_image(self):
        path = filedialog.askopenfilename()
        if path:
            self.image_state.set_image(Image.open(path))
            self.display_image()
            # Đặt lại trạng thái khi mở ảnh mới
            self.start_x = None
            self.start_y = None
            self.text_start_x = None
            self.text_start_y = None
            self.text_mode = False

    def rotate_image(self):
        if self.image_state.image:
            self.image_state.apply(rotate_90)
            self.display_image()

    def to_grayscale(self):
        if self.image_state.image:
            self.image_state.apply(to_grayscale)
            self.display_image()

    def undo(self):
        self.image_state.undo()
        self.display_image()

    def save_image(self):
        if self.image_state.image:
            path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("BMP files", "*.bmp"), ("All files", "*.*")]
            )
            if path:
                try:
                    self.image_state.image.save(path)
                    messagebox.showinfo("Thành công", f"Ảnh đã được lưu tại:\n{path}")
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể lưu ảnh:\n{e}")

    def display_image(self):
        if self.image_state.image:
            # Resize ảnh để vừa với canvas (giữ tỷ lệ)
            max_size = (800, 500)
            img = self.image_state.image.copy()
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            
            # Xóa ảnh cũ nếu có
            if self.image_id:
                self.canvas.delete(self.image_id)
            
            # Tạo ảnh mới trên canvas
            self.image_id = self.canvas.create_image(0, 0, anchor="nw", image=img_tk)
            self.canvas.image = img_tk  # Lưu tham chiếu để tránh bị garbage collected
            
            # Tính toán vị trí trung tâm
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width, img_height = img.size
            x = (canvas_width - img_width) / 2 if canvas_width > img_width else 0
            y = (canvas_height - img_height) / 2 if canvas_height > img_height else 0
            
            # Di chuyển ảnh đến vị trí trung tâm
            self.canvas.coords(self.image_id, x, y)
            # Cập nhật vùng cuộn
            self.canvas.config(scrollregion=(0, 0, max(img_width, canvas_width), max(img_height, canvas_height)))
        else:
            # Xóa ảnh trên canvas nếu không có ảnh
            if self.image_id:
                self.canvas.delete(self.image_id)
                self.image_id = None
            self.canvas.config(scrollregion=(0, 0, 0, 0))

    def adjust_brightness(self, val):
        if self.image_state.history:
            base = self.image_state.history[-1]
            factor = float(val)
            brightened = adjust_brightness(base, factor)
            self.image_state.apply(lambda x: brightened)
            self.display_image()

    def adjust_contrast(self):
        if self.image_state.history:
            self.image_state.apply(lambda img: adjust_contrast(img, self.contrast_scale.get()))
            self.display_image()

    def update_contrast(self, val):
        if self.image_state.history:
            base = self.image_state.history[-1]
            factor = float(val)
            contrasted = adjust_contrast(base, factor)
            self.image_state.image = contrasted
            self.display_image()

    def blur(self):
        if self.image_state.history:
            self.image_state.apply(lambda img: blur(img, self.blur_scale.get()))
            self.display_image()

    def update_blur(self, val):
        if self.image_state.history:
            base = self.image_state.history[-1]
            radius = int(val)
            blurred = blur(base, radius)
            self.image_state.image = blurred
            self.display_image()

    def update_saturation(self, val):
        if self.image_state.history:
            base = self.image_state.history[-1]
            factor = float(val)
            saturated = adjust_saturation(base, factor)
            self.image_state.apply(lambda x: saturated)
            self.display_image()

    def start_crop(self):
        if self.image_state.image:
            self.start_x = None
            self.start_y = None
            self.rect = None
            self.text_mode = False
            self.canvas.config(cursor="crosshair")
        else:
            messagebox.showerror("Lỗi", "Vui lòng mở ảnh trước khi cắt!")

    def start_add_text(self):
        if self.image_state.image:
            self.text_start_x = None
            self.text_start_y = None
            self.rect = None
            self.text_mode = True
            self.canvas.config(cursor="crosshair")
            self.show_text_dialog()
        else:
            messagebox.showerror("Lỗi", "Vui lòng mở ảnh trước khi chèn văn bản!")

    def show_text_dialog(self):
        dialog = Toplevel(self.root)
        dialog.title("Chèn văn bản")
        dialog.geometry("300x300")
        dialog.transient(self.root)
        dialog.grab_set()

        Label(dialog, text="Font (ví dụ: arial):").pack(pady=5)
        font_entry = Entry(dialog)
        font_entry.pack(pady=5)
        font_entry.insert(0, "arial")  # Giá trị mặc định

        Label(dialog, text="Văn bản:").pack(pady=5)
        text_entry = Entry(dialog)
        text_entry.pack(pady=5)

        Label(dialog, text="Kích thước font:").pack(pady=5)
        size_entry = Entry(dialog)
        size_entry.pack(pady=5)
        size_entry.insert(0, "40")  # Giá trị mặc định

        Label(dialog, text="Chọn màu văn bản:").pack(pady=5)
        Button(dialog, text="Chọn màu", command=lambda: self.choose_color(dialog)).pack(pady=5)

        def on_submit():
            self.selected_font = font_entry.get() or "arial"
            self.selected_text = text_entry.get() or "Text"
            try:
                self.selected_font_size = int(size_entry.get()) or 40
                if self.selected_font_size < 10 or self.selected_font_size > 200:
                    self.selected_font_size = 40  # Giới hạn hợp lý
                dialog.destroy()
            except ValueError:
                self.selected_font_size = 40  # Mặc định nếu nhập không hợp lệ
                dialog.destroy()

        Button(dialog, text="OK", command=on_submit).pack(pady=10)

    def choose_color(self, dialog):
        color = colorchooser.askcolor(title="Chọn màu văn bản")[1]  # Lấy mã hex của màu
        if color:
            self.selected_color = color  # Lưu màu đã chọn

    def on_click(self, event):
        if self.text_mode and self.text_start_x is None and self.text_start_y is None and self.image_state.image:
            self.text_start_x = self.canvas.canvasx(event.x)
            self.text_start_y = self.canvas.canvasy(event.y)
        elif not self.text_mode and self.start_x is None and self.start_y is None and self.image_state.image:
            self.start_x = self.canvas.canvasx(event.x)
            self.start_y = self.canvas.canvasy(event.y)
        if self.rect:
            self.canvas.delete(self.rect)

    def on_crop_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        if self.rect:
            self.canvas.delete(self.rect)
        if self.text_mode and self.text_start_x is not None and self.text_start_y is not None:
            self.rect = self.canvas.create_rectangle(self.text_start_x, self.text_start_y, cur_x, cur_y, outline="green")
        elif not self.text_mode and self.start_x is not None and self.start_y is not None:
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, cur_x, cur_y, outline="red")

    def on_release(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.config(cursor="arrow")
        
        if self.text_mode and self.text_start_x is not None and self.text_start_y is not None:
            # Lấy thông tin ảnh và canvas
            img = self.image_state.image
            if img is None:
                messagebox.showerror("Lỗi", "Vui lòng mở ảnh trước khi chèn văn bản!")
                self.text_start_x = None
                self.text_start_y = None
                self.text_mode = False
                return
            
            img_width, img_height = img.size
            
            # Lấy tọa độ và kích thước ảnh hiển thị trên canvas
            canvas_coords = self.canvas.coords(self.image_id)
            displayed_img = img.copy()
            max_size = (800, 500)
            displayed_img.thumbnail(max_size, Image.Resampling.LANCZOS)
            displayed_width, displayed_height = displayed_img.size
            
            # Tính offset (vị trí ảnh trên canvas)
            x_offset = canvas_coords[0]
            y_offset = canvas_coords[1]
            
            # Tính tỷ lệ thu nhỏ dựa trên kích thước hiển thị
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            scale_x = img_width / displayed_width if displayed_width > 0 else 1
            scale_y = img_height / displayed_height if displayed_height > 0 else 1
            
            # Điều chỉnh tọa độ văn bản dựa trên offset và tỷ lệ
            text_x = (self.text_start_x - x_offset) * scale_x
            text_y = (self.text_start_y - y_offset) * scale_y
            
            # Áp dụng văn bản đã nhập từ dialog
            if self.selected_text:
                self.image_state.apply(lambda img: add_text_to_image(img, self.selected_text, text_x, text_y, self.selected_font, self.selected_font_size, self.selected_color if hasattr(self, 'selected_color') else "#FFFFFF"))
                self.display_image()
            self.text_start_x = None
            self.text_start_y = None
            self.text_mode = False
        elif not self.text_mode and self.start_x is not None and self.start_y is not None:
            # Lấy thông tin ảnh và canvas
            img = self.image_state.image
            if img is None:
                messagebox.showerror("Lỗi", "Vui lòng mở ảnh trước khi cắt!")
                self.start_x = None
                self.start_y = None
                return
            
            img_width, img_height = img.size
            
            # Lấy tọa độ và kích thước ảnh hiển thị trên canvas
            canvas_coords = self.canvas.coords(self.image_id)
            displayed_img = img.copy()
            max_size = (800, 500)
            displayed_img.thumbnail(max_size, Image.Resampling.LANCZOS)
            displayed_width, displayed_height = displayed_img.size
            
            # Tính offset (vị trí ảnh trên canvas)
            x_offset = canvas_coords[0]
            y_offset = canvas_coords[1]
            
            # Tính tỷ lệ thu nhỏ dựa trên kích thước hiển thị
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            scale_x = img_width / displayed_width if displayed_width > 0 else 1
            scale_y = img_height / displayed_height if displayed_height > 0 else 1
            
            # Điều chỉnh tọa độ chuột dựa trên offset và tỷ lệ
            left = (min(self.start_x, cur_x) - x_offset) * scale_x
            top = (min(self.start_y, cur_y) - y_offset) * scale_y
            right = (max(self.start_x, cur_x) - x_offset) * scale_x
            bottom = (max(self.start_y, cur_y) - y_offset) * scale_y
            
            # Đảm bảo tọa độ hợp lệ
            left = max(0, min(left, img_width))
            top = max(0, min(top, img_height))
            right = max(left, min(right, img_width))
            bottom = max(top, min(bottom, img_height))
            
            # Cắt ảnh
            cropped = img.crop((left, top, right, bottom))
            self.image_state.set_image(cropped)
            self.display_image()
        if self.rect:
            self.canvas.delete(self.rect)

    def apply_random_filter(self):
        if self.image_state.history:
            self.image_state.apply(apply_random_filter)
            self.display_image()

    def update_scroll_region(self, event):
        if self.image_state.image:
            # Chỉ cập nhật scroll region nếu có ảnh và không can thiệp vào chế độ crop/text
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            self.display_image()  # Cập nhật lại vị trí trung tâm khi resize
            # Đặt lại trạng thái để tránh kích hoạt chế độ crop/text không mong muốn
            if not self.text_mode and self.start_x is None and self.start_y is None:
                self.canvas.config(cursor="arrow")