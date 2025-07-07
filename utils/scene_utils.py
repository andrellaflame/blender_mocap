import bpy

def clear_scene():
    """Clears all objects from the scene and orphaned data."""
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in [bpy.data.meshes, bpy.data.armatures, bpy.data.actions, bpy.data.materials]:
        for element in list(block):
            if element.users == 0:
                block.remove(element)
    print("Scene cleared.")
