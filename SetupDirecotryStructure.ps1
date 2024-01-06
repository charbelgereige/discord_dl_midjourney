# PowerShell script to rearrange files to the recommended directory structure

# Navigate to the project root directory
Set-Location -Path "D:\charbel\Documents\GitHub\discord_dl_midjourney"

# Create the required directories if they do not exist
$directories = "src", "tests", "data", "data\my_downloads"
foreach ($dir in $directories) {
    if (-Not (Test-Path -Path $dir)) {
        New-Item -ItemType Directory -Path $dir
    }
}

# Move Python scripts to src directory
Move-Item -Path "cv_image_analyzer.py" -Destination "src"
Move-Item -Path "discord_bot.py" -Destination "src"
Move-Item -Path "image_analyzer.py" -Destination "src"
Move-Item -Path "web_model_testing.py" -Destination "src"
Move-Item -Path "resnet_finetuning.py" -Destination "src"

# Move data files to data directory
Move-Item -Path "my_downloads" -Destination "data"

# Move environment files to the project root directory
Move-Item -Path "environment.yml" -Destination "."
Move-Item -Path "local.env" -Destination "."

# Clear the __pycache__ directory and then remove it
Remove-Item -Path "__pycache__\*" -Force
Remove-Item -Path "__pycache__" -Force

# Note: The script does not handle files that already exist in the destination directory.
# You might want to add error handling to manage such cases.
