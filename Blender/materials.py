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
	#self.report({'INFO'}, "\n\ntextures: " + str(textures) + "\n\n")
	"""
	textures: {
	'NP0002_00_Body':    {'NP0002_00_Body_C', 'NP0002_00_Body_A', 'NP0002_00_Body_N'},
	'NP0002_00_Eye':     {'NP0002_00_Eye_C'},
	'NP0002_00_Eyelash': {'NP0002_00_Head_N', 'NP0002_00_Head_C'},
	'NP0002_00_Hair':    {'NP0002_00_Hair_C', 'NP0002_00_Hair_A', 'NP0002_00_Hair_N'},
	'NP0002_00_Head':    {'NP0002_00_Head_N', 'NP0002_00_Head_C'},
	'NP0002_00_Mouth':   set(),
	'NP0002_00_Skin':    {'NP0002_00_Body_C', 'NP0002_00_Body_N'}
	}
	"""
	
	
	
	
	# https://blender.stackexchange.com/questions/132825/python-selecting-object-by-name-in-2-8
	'''ಠ~ಠ'''
	ob = bpy.context.scene.objects[submesh_name] # Get the object
	bpy.ops.object.select_all(action='DESELECT') # Deselect all objects
	bpy.context.view_layer.objects.active = ob   # Make the object the active object 
	ob.select_set(True)
	
	
	
	for k in range(len(vertexGroups)):
		mat_name = materials[k]['name']
		texture_list = textures[mat_name]
		mat = bpy.data.materials.new(name=mat_name)
		mat.use_nodes = True
		bsdf = mat.node_tree.nodes["Principled BSDF"]
		
		start = vertexGroups[k]["start"]
		stop  = vertexGroups[k]["stop"]
		print("Material name: " + mat_name)
		print("Start: " + str(start))
		print("Stop: " + str(stop))
		
		bpy.ops.object.material_slot_add()
		bpy.context.object.material_slots[k].link = 'OBJECT'
		ob.active_material = bpy.data.materials[mat_name]
		
		nodes = mat.node_tree.nodes
		links = mat.node_tree.links
		for t in texture_list:
			if t[-2:] == '_A':
				alpha_node = nodes.new('ShaderNodeTexImage')
				links.new(bsdf.inputs["Alpha"], alpha_node.outputs["Color"])
				alpha_node.location.x = -800
				alpha_file = files.data['tex_dir'] + t + ".png"
				if os.path.exists(alpha_file):
					alpha_node.image = bpy.data.images.load(alpha_file)
			elif t[-2:] == '_C':
				color_node = nodes.new('ShaderNodeTexImage')
				links.new(bsdf.inputs["Base Color"], color_node.outputs["Color"])
				color_node.location.x = -600
				color_node.location.y = 400
				color_file = files.data['tex_dir'] + t + ".png"
				if os.path.exists(color_file):
					color_node.image = bpy.data.images.load(color_file)
			elif t[-2:] == '_N':
				normal_node = nodes.new('ShaderNodeTexImage')
				normal_vector_node = nodes.new("ShaderNodeNormalMap")
				links.new(normal_vector_node.inputs["Color"], normal_node.outputs["Color"])
				links.new(bsdf.inputs["Normal"], normal_vector_node.outputs["Normal"])
				normal_vector_node.location.x = -500
				normal_vector_node.location.y = -300
				normal_node.location.x = -900
				normal_node.location.y = -400
				normal_file = files.data['tex_dir'] + t + ".png"
				if os.path.exists(normal_file):
					normal_node.image = bpy.data.images.load(normal_file)
					normal_node.image.colorspace_settings.name = "Non-Color"
	
	
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
	
	bpy.ops.object.mode_set(mode='OBJECT')