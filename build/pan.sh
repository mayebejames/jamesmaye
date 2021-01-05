FILES=*.md
for f in $FILES
do
  # extension="${f##*.}"
  filename="${f%.*}"
  echo "Converting $f to $filename.html"
  `pandoc $f -t html -o $filename.html --template ../templates/article.html`
  # uncomment this line to delete the source file.
  # rm $f
done