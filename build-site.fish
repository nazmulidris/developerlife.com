#!/usr/bin/env fish

if test -d _site/
    rm -rf _site/
end

if test -d docs/
    rm -rf docs/
end

if test -f /usr/bin/trash
    echo "Emptying trash..."
    trash-empty -f
end

echo "Build the site."
# Generate the site (in the _site/ folder)
bundle exec jekyll build

# Move _site folder to docs/ folder
mv _site/ docs/

# Copy CNAME file to docs/ folder.
cp CNAME docs/
