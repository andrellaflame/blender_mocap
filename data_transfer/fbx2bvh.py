import os
import sys
import bpy

argv = sys.argv
if "--" in argv:
    argv = argv[argv.index("--") + 1:]
else:
    argv = []

if len(argv) < 1:
    print("Usage: blender --background --python fbx2bvh.py -- <fbx_path> [bvh_output_path]")
    sys.exit(1)

fbx_path = os.path.abspath(argv[0])

if not os.path.isfile(fbx_path):
    sys.exit(f"FBX file does not exist or is not a file: {fbx_path}")

if not fbx_path.lower().endswith(".fbx"):
    sys.exit("Input file must have a .fbx extension")

if len(argv) > 1:
    bvh_path = os.path.abspath(argv[1])
else:
    base, ext = os.path.splitext(fbx_path)
    bvh_path = base + ".bvh"

print(f"Arguments passed: {argv}")
print(f"Using FBX path: {fbx_path}")
print(f"Using BVH path: {bvh_path}")

def fbx2bvh(sourcepath, bvh_output_path):
    bpy.ops.import_scene.fbx(filepath=sourcepath)

    frame_start = 9999
    frame_end = -9999
    action = bpy.data.actions[-1]
    if action.frame_range[1] > frame_end:
        frame_end = action.frame_range[1]
    if action.frame_range[0] < frame_start:
        frame_start = action.frame_range[0]

    frame_end = max(60, frame_end)

    frame_start = int(frame_start)
    frame_end = int(frame_end)

    bpy.ops.export_anim.bvh(
        filepath=bvh_output_path,
        frame_start=frame_start,
        frame_end=frame_end,
        root_transform_only=True,
    )
    bpy.data.actions.remove(bpy.data.actions[-1])
    print(f"Exported BVH to: {bvh_output_path}")

try:
    import data_transfer
    data_transfer.clear_scene()
except ImportError as e:
    print(f"Scene clear skipped or failed: {e}")

print(f"Processing FBX file: {fbx_path}")
fbx2bvh(fbx_path, bvh_path)
print("Done.")
