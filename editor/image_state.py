class ImageState:
    def __init__(self):
        self.history = []
        self.image = None

    def set_image(self, img):
        self.image = img
        self.history = [img.copy()]

    def apply(self, func):
        if self.image:
            self.image = func(self.image)
            self.history.append(self.image.copy())

    def undo(self):
        if len(self.history) > 1:
            self.history.pop()
            self.image = self.history[-1].copy()
