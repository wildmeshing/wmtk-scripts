# in_name = INPUT_PATH
# out_png = 'out.png'

import bpy
for l in bpy.data.objects:
	if l.type == 'MESH':
		l.hide_render = True


bpy.ops.import_mesh.ply(filepath=in_name)

obj = bpy.context.active_object
print(list(bpy.data.materials))
obj.active_material = bpy.data.materials['main']

assert obj.type == 'MESH'

if PLOT_EDGE:
	for edge in obj.data.edges:
		edge.use_freestyle_mark = True

bpy.data.scenes['Scene'].render.engine = 'CYCLES'
bpy.data.scenes["Scene"].render.filepath = out_png
bpy.ops.render.render(write_still=True)