#!/bin/bashTAGS
# This script takes the lastest nl_to_table local image, labels it, pushes it
# and restarts the service.
#
# It asks for confirmation on each step.
DEV_IMAGE="nl_to_table-app"
PRODUCTION_IMAGE="bro3jo2/nltotable"
DEV_TAGS=$(docker inspect -f {{.RepoTags}} $DEV_IMAGE:latest)
DEV_DATE=$(docker inspect -f {{.Created}} $DEV_IMAGE:latest)
VERSION=$(curl -s https://raw.githubusercontent.com/jueves/NL_to_table/main/version.txt)

# Show info
echo "### INFO ABOUT $DEV_IMAGE:latest ###"
echo "Image tags: $DEV_TAGS"
echo "Creation date: $DEV_DATE"
echo "Version to be tagged with: $VERSION"

# Ask for confirmation
read -p "Are you sure you want to tag $DEV_IMAGE:latest to $PRODUCTION_IMAGE:$VERSION? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Tag image
    docker tag $DEV_IMAGE:latest $PRODUCTION_IMAGE:$VERSION
    docker tag $DEV_IMAGE:latest $PRODUCTION_IMAGE:latest
fi

read -p "Are you sure you want to use $PRODUCTION_IMAGE:$VERSION in production? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Set new version in .env file
    cat env_keys > .env
    echo "VERSION=$VERSION" >> .env
fi

# Restart docker compose
read -p "Do you want to restart the stack? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    docker compose -f production.yml down
    docker compose -f production.yml up -d
fi

# Push new images to DockerHub
read -p "Would you like to push the new image to DockerHub? " -n 1 -r
echo    
if [[ $REPLY =~ ^[Yy]$ ]]
then
    docker push $PRODUCTION_IMAGE:$VERSION
    docker push $PRODUCTION_IMAGE:latest
fi
