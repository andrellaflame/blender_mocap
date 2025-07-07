import bpy
import sys
import numpy as np
import argparse
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from data_transfer import weights_transfer
from utils import scene_utils, file_utils

def _make_animation_looped(armature_obj):
    """
    Make the animation loop indefinitely by adding a Cycles modifier
    """
    if not armature_obj.animation_data or not armature_obj.animation_data.action:
        print("No animation data found on armature")
        return
    
    action = armature_obj.animation_data.action
    first_frame = int(action.frame_range[0])
    last_frame = int(action.frame_range[1])
    original_duration = last_frame - first_frame + 1
    
    print(f"Original animation: frames {first_frame} to {last_frame} ({original_duration} frames)")
    
    # Add Cycles modifier to each F-curve to make it loop infinitely
    for fcurve in action.fcurves:
        # Check if Cycles modifier already exists
        has_cycles = any(mod.type == 'CYCLES' for mod in fcurve.modifiers)
        
        if not has_cycles:
            cycles_mod = fcurve.modifiers.new(type='CYCLES')
            cycles_mod.mode_after = 'REPEAT'
            cycles_mod.mode_before = 'REPEAT'
    
    print("Animation set to loop indefinitely using Cycles modifiers")

def set_modifier(me, arm):
    modifiers = me.modifiers
    for modifier in modifiers:
        if modifier.type == 'ARMATURE':
            modifier.object = arm
            modifier.use_vertex_groups = True
            modifier.use_deform_preserve_volume = True
            return

    modifier = modifiers.new(name='Armature', type='ARMATURE')
    modifier.object = arm
    modifier.use_vertex_groups = True
    modifier.use_deform_preserve_volume = True

def adapt_weight(source_weight, source_label, source_arm, dest_arm):
    dest_bone_names = {bone.name for bone in dest_arm.data.bones}

    missing_bones = [name for name in source_label if name not in dest_bone_names]
    if missing_bones:
        print("\n[ERROR] The following vertex group names were not found in the destination armature bones:")
        for name in missing_bones:
            print(f" - {name}")
        raise ValueError("Aborting weight transfer due to missing bones.")

    weight = np.zeros((source_weight.shape[0], len(dest_arm.data.bones)))
    dest_bone_index = {bone.name: i for i, bone in enumerate(dest_arm.data.bones)}

    for j, name in enumerate(source_label):
        idx = dest_bone_index[name]
        weight[:, idx] += source_weight[:, j]

    return weight

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fbx_file', type=str, required=True, help='path of skinned model fbx file')
    parser.add_argument('--bvh_file', type=str, required=True, help='path of animation bvh file')
    parser.add_argument('--looped', action='store_true', help='make animation loop indefinitely')

    if "--" not in sys.argv:
        argv = []
    else:
        argv = sys.argv[sys.argv.index("--") + 1:]

    args = parser.parse_args(argv)

    scene_utils.clear_scene()

    file_utils.load_fbx(args.fbx_file)
    source_arm = bpy.data.objects['Armature']

    bvh_name = file_utils.load_bvh(args.bvh_file)
    dest_arm = bpy.data.objects[bvh_name]

    source_arm.scale = dest_arm.scale

    bpy.context.view_layer.update()

    meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']

    for mesh in meshes:
        weight, label, _ = weights_transfer.extract_weight(mesh)
        weight = adapt_weight(weight, label, source_arm, dest_arm)
        weights_transfer.load_weight(mesh, dest_arm.data.bones.keys(), weight)
        set_modifier(mesh, dest_arm)
        bpy.context.view_layer.update()

    source_arm.hide_viewport = True
    
    # Apply animation looping if requested
    if args.looped:
        _make_animation_looped(dest_arm)

if __name__ == "__main__":
    main()

# Usage examples:
# 
# Basic transfer (original animation):
# /Applications/Blender.app/Contents/MacOS/Blender --python ./transfer.py -- \
#   --fbx_file ./model/human_model.fbx \
#   --bvh_file ./motion/Bicycle_Crunch.bvh
#
# Transfer with looped animation:
# /Applications/Blender.app/Contents/MacOS/Blender --python ./transfer.py -- \
#   --fbx_file ./model/human_model.fbx \
#   --bvh_file ./motion/Bicycle_Crunch.bvh \
#   --looped