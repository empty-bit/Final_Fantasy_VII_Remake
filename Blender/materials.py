import bpy
from bpy import data

from .utils import *




def createMaterials(files, submesh_name, vertexGroups, materials, meshObject):
	'''
	for block in data.materials:
		if block.users == 0:
			data.materials.remove(block)
	'''
	textures = getMaterialTypes(files)
	print ("\n\n")
	print ("textures:")
	print (textures)
	print ("\n\n")
	
	# https://blender.stackexchange.com/questions/132825/python-selecting-object-by-name-in-2-8
	'''ಠ~ಠ'''
	ob = bpy.context.scene.objects[submesh_name] # Get the object
	bpy.ops.object.select_all(action='DESELECT') # Deselect all objects
	bpy.context.view_layer.objects.active = ob   # Make the object the active object 
	ob.select_set(True)
	
	
	
	for k in range(len(vertexGroups)):
		mat_name = materials[k]['name']
		texture_list = textures[mat_name]
		print(texture_list)
		print("\n\n")
		mat = bpy.data.materials.new(name=mat_name)
		mat.use_nodes = True
		bsdf = mat.node_tree.nodes["Principled BSDF"]
		bsdf.inputs[5].default_value = 0.1  # specular
		bsdf.inputs[7].default_value = 0.9  # roughness
		
		start = vertexGroups[k]["start"]
		stop  = vertexGroups[k]["stop"]
		print("Material name: " + mat_name)
		print("Start: " + str(start))
		print("Stop: " + str(stop))
		
		bpy.ops.object.material_slot_add()
		bpy.context.object.material_slots[k].link = 'OBJECT'
		ob.active_material = bpy.data.materials[mat_name]
		
		color_node = None
		normal_node = None
		occlusion_node = None
		normal_vector_node = None
		nodes = mat.node_tree.nodes
		links = mat.node_tree.links
		for t in texture_list:
			if t == 'A':
				alpha_node = nodes.new('ShaderNodeTexImage')
				links.new(bsdf.inputs["Alpha"], alpha_node.outputs["Color"])
				alpha_node.location.x = -600
				alpha_file = files.data['tex_dir'] + texture_list[t] + ".png"
				if os.path.exists(alpha_file):
					alpha_node.image = bpy.data.images.load(alpha_file)
			if t == 'C':
				color_node = nodes.new('ShaderNodeTexImage')
				links.new(bsdf.inputs["Base Color"], color_node.outputs["Color"])
				color_node.location.x = -600
				color_node.location.y = 400
				color_file = files.data['tex_dir'] + texture_list[t] + ".png"
				if os.path.exists(color_file) and occlusion_node == None:
					color_node.image = bpy.data.images.load(color_file)
			if t == 'N':
				if normal_node:
					normal_node.location.x = -200
					normal_node.location.y = -500
				
				if normal_vector_node == None:
					normal_vector_node = nodes.new("ShaderNodeNormalMap")
					normal_vector_node.location.x = -200
					normal_vector_node.location.y = -200
				
				normal_node = nodes.new('ShaderNodeTexImage')
				
				links.new(normal_vector_node.inputs["Color"], normal_node.outputs["Color"])
				links.new(bsdf.inputs["Normal"], normal_vector_node.outputs["Normal"])
				
				
				
				normal_node.location.x = -600
				normal_node.location.y = -300
				normal_file = files.data['tex_dir'] + texture_list[t] + ".png"
				if os.path.exists(normal_file):
					normal_node.image = bpy.data.images.load(normal_file)
					normal_node.image.colorspace_settings.name = "Non-Color"
			if t == 'O':
				occlusion_file = files.data['tex_dir'] + texture_list[t] + ".png"
				if os.path.exists(occlusion_file):
					occlusion_node = nodes.new('ShaderNodeTexImage')
				occlusion_node.image = bpy.data.images.load(occlusion_file)
				occlusion_node.location.x = -900
				occlusion_node.location.y = 200
				
				uv_node = nodes.new("ShaderNodeUVMap")
				uv_node.uv_map = "UVmap_1"
				uv_node.location.x = -1100
				
				multiply_node = nodes.new("ShaderNodeMixRGB")
				multiply_node.blend_type = 'MULTIPLY'
				multiply_node.inputs[0].default_value = 1
				multiply_node.location.x = -300
				multiply_node.location.y = 200
				
				links.new(occlusion_node.inputs["Vector"], uv_node.outputs["UV"])
				links.new(multiply_node.inputs["Color2"], occlusion_node.outputs["Color"])
				
				if not color_node:
					color_node = nodes.new('ShaderNodeTexImage')
					color_file = files.data['tex_dir'] + texture_list['C'] + ".png"
					color_node.image = bpy.data.images.load(color_file)
				
				color_node.location.x = -900
				color_node.location.y = 500
				
				links.new(multiply_node.inputs["Color1"], color_node.outputs["Color"])
				links.new(bsdf.inputs["Base Color"], multiply_node.outputs["Color"])
	
	
	
	
	for x in vertexGroups:
		mat_name = materials[x]['name']
		temp = meshObject.vertex_groups.new(name = mat_name)
		temp.add(vertexGroups[x]['range'], 1.0, 'ADD')
	
	
	context = bpy.context
	obj = context.object
	bpy.ops.object.mode_set(mode='EDIT')
	for vg in obj.vertex_groups:
		bpy.ops.mesh.select_all(action='DESELECT')
		obj.vertex_groups.active_index = vg.index
		bpy.ops.object.vertex_group_select()
		i = obj.material_slots.find(vg.name)
		if i >= 0:
			obj.active_material_index = i
			bpy.ops.object.material_slot_assign()
	
	bpy.ops.mesh.select_all(action='DESELECT')
	bpy.ops.object.mode_set(mode='OBJECT')