import argparse
import torch
import torch.nn as nn
from torchvision import models, transforms, datasets
from torch.utils.data import DataLoader, random_split
import os
from tqdm import tqdm
import logging

# Set up argument parser
parser = argparse.ArgumentParser(description='Fine-tune a ResNet model')
parser.add_argument('dataset_path', type=str, help='Path to the dataset')
args = parser.parse_args()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set device to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logging.info(f'Using device: {device}')

# Load the pre-trained ResNet model
model = models.resnet18(pretrained=True)

# Freeze the early layers of the model
for param in model.parameters():
    param.requires_grad = False

# Replace the final layer to match the number of classes in your dataset
model.fc = nn.Linear(model.fc.in_features, 2)  # Adjust the number of classes here
model.to(device)

# Define transformations for your dataset
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# Load your dataset
dataset = datasets.ImageFolder(root=args.dataset_path, transform=transform)

# Split the dataset into training, validation, and test sets
train_size = int(0.75 * len(dataset))
val_size = int(0.15 * len(dataset))
test_size = len(dataset) - train_size - val_size

train_data, val_data, test_data = random_split(dataset, [train_size, val_size, test_size])

# Create data loaders
train_loader = DataLoader(train_data, batch_size=16, shuffle=True)
val_loader = DataLoader(val_data, batch_size=16, shuffle=False)
test_loader = DataLoader(test_data, batch_size=16, shuffle=False)

# Define a loss function and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.fc.parameters(), lr=0.001)

# Train the model (a very basic training loop)
num_epochs = 5
for epoch in range(num_epochs):
    model.train()
    epoch_loss = 0
    for inputs, labels in tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs}', unit='batch'):
        inputs, labels = inputs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        epoch_loss += loss.item()
    
    # Print loss
    logging.info(f'Epoch {epoch+1}/{num_epochs}, Loss: {epoch_loss / len(train_loader)}')

# Save the trained model
torch.save(model.state_dict(), 'fine_tuned_resnet.pth')
