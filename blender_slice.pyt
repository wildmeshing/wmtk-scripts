import bpy
# cut_name = 'out/32.msh_final.msh.slice0.ply'
# out_png = 'out.png'
# sf_name = 'out/32.msh_final.msh.slice1.ply'

for l in bpy.data.objects:
	if l.type == 'MESH':
		l.hide_render = True

for name, mat in [(cut_name, 'cut'), (sf_name, 'main')]:
	bpy.ops.import_mesh.ply(filepath=name)
	obj = bpy.context.active_object
	obj.active_material = bpy.data.materials[mat]

	assert obj.type == 'MESH'

	for edge in obj.data.edges:
		edge.use_freestyle_mark = True

bpy.data.scenes['Scene'].render.engine = 'CYCLES'
bpy.data.scenes["Scene"].render.filepath = out_png
bpy.ops.render.render(write_still=True)
