import bpy

for l in bpy.data.objects:
	if l.type == 'MESH':
            bpy.data.objects.remove(l, do_unlink=True)
bpy.ops.wm.save_mainfile()

