# Build instructions


Move md files to _site directory.

Run pandoc preprocessor on md files, producing preprocessed files in separate folder:

    cd ~/jamesmaye/_site
    python3 ../build/preproc.py

move to separate folder to run pandoc, deleting the preprocessed files
    cd ../md
    ../build/./pan.sh

move to tags folder to run pandoc again
    cd ~/jamesmaye/_site/tags
    ../../build/./pan_tags.sh
