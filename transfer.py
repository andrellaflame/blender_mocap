import bpy
import sys
import numpy as np
import argparse
import os

def clean_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def load_fbx(source):
    bpy.ops.import_scene.fbx(filepath=source)

def load_bvh(source):
    bpy.ops.import_anim.bvh(filepath=source)
    return source.split('/')[-1][:-4]

def extract_weight(me):
    verts = me.data.vertices
    vgrps = me.vertex_groups

    weight = np.zeros((len(verts), len(vgrps)))
    mask = np.zeros(weight.shape, dtype=int)
    vgrp_label = vgrps.keys()

    for i, vert in enumerate(verts):
        for g in vert.groups:
            j = g.group
            weight[i, j] = g.weight
            mask[i, j] = 1

    return weight, vgrp_label, mask

def clean_vgrps(me):
    vgrps = me.vertex_groups
    for _ in range(len(vgrps)):
        vgrps.remove(vgrps[0])

def load_weight(me, label, weight):
    clean_vgrps(me)
    verts = me.data.vertices
    vgrps = me.vertex_groups

    for name in label:
        vgrps.new(name=name)

    for j in range(weight.shape[1]):
        idx = vgrps.find(label[j])
        if idx == -1:
            continue
        for i in range(weight.shape[0]):
            vgrps[idx].add([i], weight[i, j], 'REPLACE')

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

    # Check for exact matches only
    missing_bones = [name for name in source_label if name not in dest_bone_names]
    if missing_bones:
        print("\n[ERROR] The following vertex group names were not found in the destination armature bones:")
        for name in missing_bones:
            print(f" - {name}")
        raise ValueError("Aborting weight transfer due to missing bones.")

    # Proceed with safe mapping
    weight = np.zeros((source_weight.shape[0], len(dest_arm.data.bones)))
    dest_bone_index = {bone.name: i for i, bone in enumerate(dest_arm.data.bones)}

    for j, name in enumerate(source_label):
        idx = dest_bone_index[name]
        weight[:, idx] += source_weight[:, j]

    return weight
    action = armature_obj.animation_data.action
    first_frame = int(action.frame_range[0])
    last_frame = int(action.frame_range[1])
    for fcurve in action.fcurves:
        first_value = fcurve.evaluate(first_frame)
        last_value = fcurve.evaluate(last_frame)

        # Insert keyframe on last frame to match the first
        fcurve.keyframe_points.insert(frame=last_frame + 1, value=first_value, options={'FAST'})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fbx_file', type=str, required=True, help='path of skinned model fbx file')
    parser.add_argument('--bvh_file', type=str, required=True, help='path of animation bvh file')

    if "--" not in sys.argv:
        argv = []
    else:
        argv = sys.argv[sys.argv.index("--") + 1:]

    args = parser.parse_args(argv)

    clean_scene()

    load_fbx(args.fbx_file)
    source_arm = bpy.data.objects['Armature']

    bvh_name = load_bvh(args.bvh_file)
    dest_arm = bpy.data.objects[bvh_name]

    source_arm.scale = dest_arm.scale

    bpy.context.view_layer.update()

    meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']

    for mesh in meshes:
        weight, label, _ = extract_weight(mesh)
        weight = adapt_weight(weight, label, source_arm, dest_arm)
        load_weight(mesh, dest_arm.data.bones.keys(), weight)
        set_modifier(mesh, dest_arm)
        bpy.context.view_layer.update()


    source_arm.hide_viewport = True

if __name__ == "__main__":
    main()

# Usage examples:
# 
# Basic transfer:
# /Applications/Blender.app/Contents/MacOS/Blender --python ./transfer.py -- \
#   --fbx_file ./model/human_model.fbx \
#   --bvh_file ./motion/Walking.bvh
