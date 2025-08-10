#!/bin/sh

set -e

echo "Committing cache updates..."
git add cache/
if git diff --staged --quiet; then
    echo "No cache changes to commit"
else
    git commit -m "Update PyPI stats cache - $(date '+%Y-%m-%d')"
    git push
    echo "Cache committed and pushed"
fi