import cv2
import torch
import numpy as np
import logging
import os
import shutil
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)

class TorchCVImageAnalyzer:
    def __init__(self, image_path):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        
        if self.device.type == "cuda":
            logging.info("CUDA is available and tensors will be processed on GPU.")
        else:
            logging.warning("CUDA is not available. Tensors will be processed on CPU.")
        
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

        # Convert the image to a PyTorch tensor and move to the specified device
        img_tensor = torch.from_numpy(self.img).float().to(self.device)
        thresh_tensor = torch.threshold(img_tensor, 128, 255)
        thresh = thresh_tensor.cpu().numpy().astype(np.uint8)
        
        # Detecting lines
        lines = cv2.HoughLinesP(thresh, 1, np.pi / 180, threshold=100, minLineLength=10, maxLineGap=5)
        if lines is None:
            return True
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(x2 - x1) > abs(y2 - y1):
                # Horizontal line
                if abs(y1 - self.img.shape[0] // 2) < 5:
                    return False
            else:
                # Vertical line
                if abs(x1 - self.img.shape[1] // 2) < 5:
                    return False
        return True

    def process_directory(self, directory_path):
        files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        matrix_subdir = os.path.join(directory_path, "matrix")

        # Ensure the matrix subdirectory exists
        if not os.path.exists(matrix_subdir):
            os.makedirs(matrix_subdir)

        # Process each image in the directory
        for filename in tqdm(files, desc="Analyzing images"):
            file_path = os.path.join(directory_path, filename)
            analyzer = TorchCVImageAnalyzer(file_path)
            if analyzer.is_upscale():
                logging.info(f"Image {filename} is upscale.")
            else:
                shutil.move(file_path, os.path.join(matrix_subdir, filename))
                logging.info(f"Moved {filename} to matrix_images directory.")


if __name__ == "__main__":
    import sys
    directory_name = sys.argv[1]
    analyzer = TorchCVImageAnalyzer(None)
    analyzer.process_directory(directory_name)
