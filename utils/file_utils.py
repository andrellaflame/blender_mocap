import bpy

def load_fbx(source):
    bpy.ops.import_scene.fbx(filepath=source)

def load_bvh(source):
    bpy.ops.import_anim.bvh(filepath=source)
    return source.split('/')[-1][:-4]
