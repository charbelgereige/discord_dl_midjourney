# Get the current location
$CurrentLocation = Get-Location

# Get all items recursively in the current directory, excluding PNG files
$Items = Get-ChildItem -Recurse -Exclude *.png

# Display the directory structure in a formatted table
$Items | Format-Table Name, FullName -AutoSize
