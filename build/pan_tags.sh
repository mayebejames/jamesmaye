FILES=*.md
for f in $FILES
do
  # extension="${f##*.}"
  filename="${f%.*}"
  echo "Converting $f to $filename.html"
  `pandoc $f -t html -o ~/jamesmaye/_site/tags/$filename.html --template ~/jamesmaye/templates/article.html`
  #uncomment this line to delete the source file.
  rm $f
done