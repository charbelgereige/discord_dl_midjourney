import cv2
import logging

class ImageAnalyzer:
    def __init__(self, image_path):
        self.image_path = image_path
        try:
            self.img = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
            if self.img is None:
                raise ValueError("Could not read the image.")
        except Exception as e:
            logging.error(f"An error occurred while processing the image: {self.image_path}. Error: {str(e)}")
            self.img = None

    def is_upscale(self):
        if self.img is None:
            return False

        # Binary threshold to distinguish the main content
        _, thresh = cv2.threshold(self.img, 127, 255, cv2.THRESH_BINARY_INV)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter out very small contours which are probably noise
        large_contours = [c for c in contours if cv2.contourArea(c) > (self.img.shape[0] * self.img.shape[1]) * 0.05]

        # If we have more than one large contour, it's likely a matrix
        if len(large_contours) > 1:
            return False

        return True
