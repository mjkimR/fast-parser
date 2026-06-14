#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Repository configuration
REGISTRY="ghcr.io"
DEFAULT_OWNER="mjkimr"
DEFAULT_IMAGE="fast-parser"

# Resolve directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Usage information
usage() {
    echo "Usage: $0 [options] [tag]"
    echo ""
    echo "Options:"
    echo "  -d, --dry-run     Build the image but do not push it to the registry."
    echo "  -h, --help        Show this help message."
    echo ""
    echo "Arguments:"
    echo "  tag               The docker image tag (default: latest)."
    exit 1
}

# Parse options
DRY_RUN=false
TAG="latest"

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        -*)
            echo "Unknown option: $1"
            usage
            ;;
        *)
            TAG="$1"
            shift
            ;;
    esac
done

IMAGE_NAME="${IMAGE_NAME:-$REGISTRY/$DEFAULT_OWNER/$DEFAULT_IMAGE}"
FULL_IMAGE_TAG="$IMAGE_NAME:$TAG"

echo "=== Build Configuration ==="
echo "Project Root: $PROJECT_ROOT"
echo "Image Tag:    $FULL_IMAGE_TAG"
echo "Dry Run:      $DRY_RUN"
echo "==========================="

# Navigate to project root
cd "$PROJECT_ROOT"

# Build Docker image
echo "Building Docker image..."
docker build -t "$FULL_IMAGE_TAG" .

if [ "$DRY_RUN" = true ]; then
    echo "Dry run enabled. Skipping login and push."
    echo "Successfully built: $FULL_IMAGE_TAG"
    exit 0
fi

# Ask or verify GHCR login in interactive environments
if [ -t 0 ]; then
    echo "Checking registry login..."
    read -p "Do you need to log in to $REGISTRY? (y/N): " -r LOGIN_CHOICE
    if [[ "$LOGIN_CHOICE" =~ ^[Yy]$ ]]; then
        read -p "GitHub Username: " -r GH_USER
        echo "Please enter your GitHub Personal Access Token (PAT) with write:packages scope:"
        docker login "$REGISTRY" -u "$GH_USER"
    fi
else
    echo "Non-interactive environment detected. Skipping interactive login prompt."
    echo "Ensure you are already logged in to $REGISTRY via 'docker login'."
fi

# Push Docker image
echo "Pushing Docker image to $REGISTRY..."
docker push "$FULL_IMAGE_TAG"

echo "Successfully pushed $FULL_IMAGE_TAG"
