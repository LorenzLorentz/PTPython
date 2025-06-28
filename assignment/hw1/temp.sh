for file in hw*.py; do
    num=$(echo "$file" | grep -o '[0-9]\+')
    mv "$file" "T${num}.py"
done