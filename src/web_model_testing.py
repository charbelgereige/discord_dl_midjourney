from flask import Flask, render_template, request, jsonify
import torch
import os
from torchvision import transforms
from PIL import Image
import logging
import torch.nn as nn
from torchvision import models

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


class ImageClassifier:
    def __init__(self, model_path):
        logging.warning(f"model path is {model_path}")
        
        # Define the same architecture as it was during training
        self.model = models.resnet18()
        self.model.fc = nn.Linear(self.model.fc.in_features, 2)  # Adjust the number of classes
        
        # Load the state dict
        state_dict = torch.load(model_path, map_location=torch.device('cpu'))
        
        # Apply the state dict to your model
        self.model.load_state_dict(state_dict)
        
        self.model.eval()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])

    
    def classify_image(self, image_path):
        image = Image.open(image_path).convert('RGB')
        image = self.transform(image).unsqueeze(0)
        output = self.model(image)
        _, predicted = torch.max(output.data, 1)
        return 'Matrix' if predicted.item() == 0 else 'Upscale'

@app.route('/')
def index():
    models = os.listdir('models')  # Replace with the path to your models directory
    return render_template('index.html', models=models)

@app.route('/classify', methods=['POST'])
def classify():
    model_name = request.form['model']
    directory = request.form['directory']
    logging.warning(f"Model Name: {model_name}")
    logging.info(f"Model Name: {model_name}")
    classifier = ImageClassifier(f'models/{model_name}') 
    
    images = []
    for filename in os.listdir(directory):
        if filename.endswith(('png', 'jpg', 'jpeg')):
            image_path = os.path.join(directory, filename)
            label = classifier.classify_image(image_path)
            images.append({'path': image_path, 'classification': label})

    return jsonify({'images': images})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
