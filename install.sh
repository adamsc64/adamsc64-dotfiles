# Run anything in this directory that starts with install_*.sh
for file in install_*.sh; do
  if [ -x "$file" ]; then
    echo "Running $file..."
    ./"$file"
  else
    echo "Skipping $file (not executable)"
  fi
done