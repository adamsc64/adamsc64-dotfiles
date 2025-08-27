#!/bin/bash

# Check if a directory argument is provided
if [ "$1" != "" ]; then
  # Change to the provided directory
  cd "$1" || exit 1
else
  # Default to the macOS Desktop directory
  cd ~/Desktop || exit 1
fi

# Loop through all screenshots
for file in Screenshot*at*.png; do
  # Extract the date from the filename
  date=$(echo $file | awk '{print $2}')
  
  # Create the directory if it doesn't exist
  mkdir -p $date
  
  # Move the file into the directory
  echo "moving '$file' to '$date/'"
  mv "$file" "$date/"
done

