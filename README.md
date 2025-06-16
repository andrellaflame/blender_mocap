# Blender Mocap Retargeting Utility

This is a Blender utility script designed to **retarget motion capture (.bvh) animations** onto **Mixamo-style rigged characters (.fbx)**. It automates the transfer of animation while preserving skin weights and mesh deformation.

## Features

- Retargets BVH animation onto FBX armatures with matching bone names.
- Handles Mixamo-style skeletons.
- Preserves skinning and vertex weights.
- Optional in-place motion and looping for seamless animation playback.

## Usage

Run the script via Blender in command-line mode:

```bash
/Applications/Blender.app/Contents/MacOS/Blender --python transfer.py -- \
  --fbx_file /path/to/model.fbx \
  --bvh_file /path/to/animation.bvh
```
