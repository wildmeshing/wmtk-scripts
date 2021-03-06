import bpy
in_name = 'out/0.obj.unit.ply'
out_png = 'out.png'

bpy.ops.import_mesh.ply(filepath=in_name)

obj = bpy.context.active_object
obj.active_material = bpy.data.materials['main']

assert obj.type == 'MESH'

for edge in obj.data.edges:
	edge.use_freestyle_mark = True

bpy.data.scenes['Scene'].render.engine = 'CYCLES'
bpy.data.scenes["Scene"].render.filepath = out_png
bpy.ops.render.render(write_still=True)