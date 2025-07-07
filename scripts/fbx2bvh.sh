#!/bin/bash

BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
SCRIPT_PATH="./data_transfer/fbx2bvh.py"

FBX_PATH="$1"
BVH_PATH="$2"

if [ -z "$FBX_PATH" ]; then
  echo "Usage: $0 path/to/file.fbx [path/to/output.bvh]"
  exit 1
fi

if [ -n "$BVH_PATH" ]; then
  "$BLENDER" --background --python "$SCRIPT_PATH" -- "$FBX_PATH" "$BVH_PATH"
else
  "$BLENDER" --background --python "$SCRIPT_PATH" -- "$FBX_PATH"
fi