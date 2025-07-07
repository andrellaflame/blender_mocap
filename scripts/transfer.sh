#!/bin/bash

/Applications/Blender.app/Contents/MacOS/Blender --python ./transfer.py -- \
  --fbx_file ./model/human_model.fbx \
  --bvh_file ./motion/Bicycle_Crunch.bvh
