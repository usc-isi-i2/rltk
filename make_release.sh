#!/usr/bin/env bash

# requirement: update VERSION and make a git commit first

version=$(head -n 1 VERSION)
git tag $version
git push origin $version
