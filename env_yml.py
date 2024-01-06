import subprocess
import os

# Name of the environment
env_name = "discord"

# Generate list of Conda packages
conda_packages = subprocess.getoutput(f"conda list --name {env_name} --export --no-pip").splitlines()
conda_packages = [pkg.split('=')[0] for pkg in conda_packages if not pkg.startswith("#")]

# Generate list of pip packages
pip_packages = subprocess.getoutput(f"conda activate {env_name} && pip freeze --exclude-editable").splitlines()
pip_packages = [pkg.split('==')[0] for pkg in pip_packages]

# Write to environment.yml
with open("environment.yml", "w") as file:
    file.write(f"name: {env_name}\n")
    file.write("channels:\n  - defaults\n")
    file.write("dependencies:\n")
    for pkg in conda_packages:
        file.write(f"  - {pkg}\n")
    file.write("  - pip:\n")
    for pkg in pip_packages:
        file.write(f"    - {pkg}\n")

print(f"environment.yml generated for {env_name}.")
