#!/bin/sh

set -e

# Variables
REPO_URL="https://github.com/bitplane/bitplane.net.git"
SRC_FILE="stats.png"
DEST_PATH="dev/python/stats.png"
COMMIT_MSG="Update PyPI stats chart"

# Check that stats.png exists
if [ ! -f "$SRC_FILE" ]; then
    echo "Error: $SRC_FILE not found. Run 'make stats.png' first."
    exit 1
fi

# Check out the main website repo
TMP_DIR=$(mktemp -d)

# Cleanup on exit
cleanup() {
    echo "Cleaning up..."
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

# Clone the repository
echo "Cloning $REPO_URL into $TMP_DIR..."
git clone --depth=1 "https://x-access-token:${GITHUB_TOKEN}@github.com/bitplane/bitplane.net.git" "$TMP_DIR"

# Set up the destination path
FULL_DEST_PATH="$TMP_DIR/$DEST_PATH"
DEST_DIR=$(dirname "$FULL_DEST_PATH")

# Create directory if needed
echo "Creating directory $DEST_DIR..."
mkdir -p "$DEST_DIR"

# Copy the stats.png file
echo "Copying $SRC_FILE to $FULL_DEST_PATH..."
cp "$SRC_FILE" "$FULL_DEST_PATH"

# Commit and push
echo "Committing and pushing changes..."
cd "$TMP_DIR"
git add "$DEST_PATH"
git commit -m "$COMMIT_MSG"
git push

echo "Stats chart published!"