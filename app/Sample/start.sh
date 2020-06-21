#!/bin/bash

DIR="node_modules"
if [ ! -d "$DIR" ]; then
  echo 'Running npm install as this is the first time app is being built'
  npm install
fi
echo 'Running ng build'
ng build --watch --deleteOutputPath=false