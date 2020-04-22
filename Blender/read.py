import os
import re
import io
import bpy
import sys
import math
import time
import struct
import codecs
import subprocess
import numpy as np
import bmesh as bmesh
import mathutils as mu
from subprocess import Popen

from rna_prop_ui import rna_idprop_ui_prop_get as prop
from bpy_extras.io_utils import unpack_list, unpack_face_list

from numpy.linalg import inv
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty


from .transforms3d.quaternions import quat2mat

from .utils import *
from .textures import *
from .materials import *



def readFile(filepath, dump_textures):
	files = path_wrangler(filepath)
	files.get_files()
	Dump(files, dump_textures)
	
	md = open(files.data['uexp'], 'rb')
	ua = open(files.data['uasset'], 'rb')
	
	meshName = files.data['meshName']
	submesh_name = files.data['submesh_name']
	
	newCol = bpy.data.collections.new(meshName)
	bpy.context.scene.collection.children.link(newCol)
	
	arm = False
	
	times = {}
	weightData = {}
	Weight_array = []
	vertexArray = []
	NA = []
	normal_array = []
	faces = []
	UVs0 = []
	UVs1 = []
	UVs2 = []
	UVs3 = []
	UVs4 = []
	UVs5 = []
	UVs6 = []
	UVs7 = []
	UVs8 = []
	UVs9 = []
	
	
	t1 = time.time()
	names = readUasset(ua)
	
	
	pattern0 = re.compile(b'\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00........')
	for x in range(20000):
		s1 = struct.unpack("18s",md.read(18))[0]
		if pattern0.match(s1):
			c0 = struct.unpack("<L",md.read(4))[0]
			c1 = struct.unpack("<L",md.read(4))[0]
			c2 = struct.unpack("<L",md.read(4))[0]
			c3 = struct.unpack("<L",md.read(4))[0]
			c4 = struct.unpack("<L",md.read(4))[0]
			if (c0 and c1 and c2 and c3 and c4 > 1000000000):
				break
			else:
				md.seek(-20,1)
		md.seek(-17,1)
	
	materialCount = struct.unpack("<L",md.read(4))[0]
	materials = {}
	for m in range(materialCount):
		materials[m] = {}
		materials[m]['val0'] = struct.unpack("<l",md.read(4))[0]
		stringIndex = struct.unpack("<L",md.read(4))[0]
		unk0 = struct.unpack("<L",md.read(4))[0]
		unk1 = struct.unpack("<L",md.read(4))[0]
		unk2 = struct.unpack("<L",md.read(4))[0]
		unk3 = struct.unpack("<f",md.read(4))[0]
		unk4 = struct.unpack("<f",md.read(4))[0]
		unk5 = struct.unpack("<L",md.read(4))[0]
		unk6 = struct.unpack("<L",md.read(4))[0]
		
		materials[m]['name'] = names[stringIndex]
	
	
	
	boneCount = struct.unpack("<L",md.read(4))[0]
	armName = meshName +"_Armature"
	armature_da = bpy.data.armatures.new(armName)
	armature_da.display_type = 'STICK'
	armature_ob = bpy.data.objects.new(armName, armature_da)
	
	bpy.context.scene.collection.objects.link(armature_ob)
	bpy.context.view_layer.objects.active = armature_ob
	armature_ob.show_in_front = True
	joint_data = {}
	for i in range(boneCount):
		string_index = struct.unpack("<L",md.read(4))[0]
		jName = names[string_index]
		unk = struct.unpack("<L",md.read(4))[0]
		parent = struct.unpack("<l",md.read(4))[0]
		
		joint_data[i] = {"name": jName, "parent":parent}
	
	boneCount2 = struct.unpack("<L",md.read(4))[0]
	mArray = []
	bone_list = []
	bpy.ops.object.mode_set(mode='EDIT')
	for k in range(boneCount2):
		m1 = struct.unpack("<10f",md.read(40))
		boneName = joint_data[k]["name"]
		BNparent = joint_data[k]["parent"]
		
		BNrt = (m1[3], -m1[0], m1[1], m1[2])
		rt = quat2mat(BNrt)
		bnXM = np.matrix(
					[[rt[0][0], rt[0][1], rt[0][2], 0], \
					[ rt[1][0], rt[1][1], rt[1][2], 0], \
					[ rt[2][0], rt[2][1], rt[2][2], 0], \
					[    -m1[4],    m1[5],    m1[6], 1]]
					)
		
		
		newBone = bpy.context.active_object.data.edit_bones.new(boneName)
		prop(newBone,"ID", create = True)
		newBone["ID"] = k
		if BNparent != -1:
			mm = bnXM * mArray[BNparent]
			parentName = joint_data[BNparent]["name"]
			pt = mu.Vector((mm[3,0], mm[3,1], mm[3,2]))
			newBone.parent = bpy.context.active_object.data.edit_bones[parentName]
			newBone.head = pt
			newBone.tail = pt + mu.Vector((0.001, 0.001, 0.001))
			mArray.append(mm)
		else:
			newBone.head = mu.Vector((0,0,0))
			newBone.tail = mu.Vector((0,0,0.1))
			mArray.append(bnXM)
		bone_list.append(newBone)
	bpy.ops.object.mode_set(mode='OBJECT')
	arm = True
	
	boneCount3 = struct.unpack("<L",md.read(4))[0]
	md.seek(boneCount3 * 12, 1)
	
	
	vertexGroups = {}
	unk0 = struct.unpack("<L",md.read(4))[0]
	unk1 = struct.unpack("B",md.read(1))[0]
	unk2 = struct.unpack("B",md.read(1))[0]
	groupCount = struct.unpack("<L",md.read(4))[0]
	for m in range(groupCount):
		z1 = struct.unpack("<H",md.read(2))[0]
		ID = struct.unpack("<H",md.read(2))[0]
		
		md.seek(24,1)
		vertexGroups[ID] = {'range':0, 'bones':[]}
		
		# pragma region bone palette
		start = struct.unpack("<L",md.read(4))[0]
		count = struct.unpack("<L",md.read(4))[0]
		for bn in range(count):
			bid = struct.unpack("<H",md.read(2))[0]
			vertexGroups[ID]['bones'].append(bid)
		# pragma endregion bone palette
		
		size = struct.unpack("<L",md.read(4))[0]
		stop = start + size
		
		vertexGroups[ID]['start'] = start
		vertexGroups[ID]['stop']  = stop
		vertexGroups[ID]['range'] = range(start, stop)
		
		
		md.seek(34,1)
		FFx4 = readHexString(md, 4)
		flag = struct.unpack("<L",md.read(4))[0]
		if flag: # extra data for this group
			count = struct.unpack("<L",md.read(4))[0]
			md.seek(count * 16, 1)
		else:
			null = struct.unpack("<L",md.read(4))[0]
	
	
	
	
	unk = struct.unpack("B",md.read(1))[0]
	checkHere = md.tell()
	stride = struct.unpack("<L",md.read(4))[0]
	fCount = struct.unpack("<L",md.read(4))[0]
	
	
	
	
	faceByteCount = fCount * stride
	vi = np.fromfile(md, dtype = 'B', count = faceByteCount)
	if stride == 4:
		fi_0 = vi.view(dtype = '<L').reshape(fCount//3, 3)
	elif stride == 2:
		fi_0 = vi.view(dtype = '<H').reshape(fCount//3, 3)
	fi_1 = np.flip(fi_0,1)
	fi_1[:,[0,1]] = fi_1[:,[1,0]]
	fi_2 = fi_1.ravel()
	faces = tuple(fi_1)
	
	
	
	
	unkCount = struct.unpack("<L",md.read(4))[0]
	md.seek(unkCount * 2, 1)
	
	unk = struct.unpack("<L",md.read(4))[0]
	vertexCount = struct.unpack("<L",md.read(4))[0]
	boneCount = struct.unpack("<L",md.read(4))[0]
	md.seek(boneCount * 2, 1)
	
	
	null0 = struct.unpack("<L",md.read(4))[0]
	null1 = struct.unpack("<L",md.read(4))[0]
	
	uv_count  = struct.unpack("<L",md.read(4))[0]
	unk0     = struct.unpack("<H",md.read(2))[0]
	uv_count2 = struct.unpack("<L",md.read(4))[0]
	
	null2 = struct.unpack("<L",md.read(4))[0]
	
	unk1  = struct.unpack("<f",md.read(4))[0]
	unk2  = struct.unpack("<f",md.read(4))[0]
	unk3  = struct.unpack("<f",md.read(4))[0]
	
	null3 = struct.unpack("<L",md.read(4))[0]
	null4 = struct.unpack("<L",md.read(4))[0]
	null5 = struct.unpack("<L",md.read(4))[0]
	
	vStride = struct.unpack("<L",md.read(4))[0]
	vCount  = struct.unpack("<L",md.read(4))[0]
	
	
	byteCount = vCount * vStride
	vi = np.fromfile(md, dtype = 'B', count = byteCount).reshape((vCount, vStride))
	pos = vi[:,8:20].ravel().view(dtype = '<f').reshape((vCount, 3))
	#pos[:,[0,2]] = pos[:,[2,0]]
	pos[:,[0,0]] *= -1
	vertexArray = pos.tolist()
	
	if uv_count > 0:
		uvData = vi[:,20:24].ravel().view(dtype = '<f2').reshape((vCount, 2))
		uvData[:,1:2] *= -1
		uvData[:,1:2] += 1
		uvData0 = uvData.tolist()
		UVs0 = [mu.Vector(x) for x in uvData0]
	if uv_count > 1:
		uvData = vi[:,24:28].ravel().view(dtype = '<f2').reshape((vCount, 2))
		uvData[:,1:2] *= -1
		uvData[:,1:2] += 1
		uvData1 = uvData.tolist()
		UVs1 = [mu.Vector(x) for x in uvData1]
	if uv_count > 2:
		uvData = vi[:,28:32].ravel().view(dtype = '<f2').reshape((vCount, 2))
		uvData[:,1:2] *= -1
		uvData[:,1:2] += 1
		uvData2 = uvData.tolist()
		UVs2 = [mu.Vector(x) for x in uvData2]
	if uv_count > 3:
		uvData = vi[:,32:36].ravel().view(dtype = '<f2').reshape((vCount, 2))
		uvData[:,1:2] *= -1
		uvData[:,1:2] += 1
		uvData3 = uvData.tolist()
		UVs3 = [mu.Vector(x) for x in uvData3]
	
	#UVs0
	
	#loc = md.tell()
	#self.report({'INFO'}, "\n\nmaterials: " + str(materials))
	#self.report({'INFO'}, "location: " + str(loc) + "\n\n")
	
	mesh = bpy.data.meshes.new(submesh_name)
	mesh.from_pydata(vertexArray, [], faces)
	
	
	mesh.validate()
	mesh.update()
	
	
	meshObject = bpy.data.objects.new(submesh_name, mesh)
	bpy.data.collections[meshName].objects.link(meshObject)
	
	mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
	
	
	
	
	unkS = struct.unpack("<H",md.read(2))[0]
	extraBoneWeights = struct.unpack("<L",md.read(4))[0]
	wCount = struct.unpack("<L",md.read(4))[0]
	stride = struct.unpack("<L",md.read(4))[0]
	wCount2 = struct.unpack("<L",md.read(4))[0]
	
	subRange = int(stride / 2)
	
	
	
	
	for g in range(uv_count):
		mesh.uv_layers.new(name = "UVmap" + "_" + str(g))
	
	UVS = 0
	for g in range(uv_count):
		if   g == 0: UVS = UVs0
		elif g == 1: UVS = UVs1
		elif g == 2: UVS = UVs2
		elif g == 3: UVS = UVs3
		elif g == 4: UVS = UVs4
		elif g == 5: UVS = UVs5
		elif g == 6: UVS = UVs6
		elif g == 7: UVS = UVs7
		elif g == 8: UVS = UVs8
		elif g == 9: UVS = UVs9
		
		vi_uv = {i: uv for i, uv in enumerate(UVS)}
		per_loop_list = [0.0] * len(mesh.loops)
		for loop in mesh.loops:
			per_loop_list[loop.index] = vi_uv.get(loop.vertex_index)
		per_loop_list = [uv for pair in per_loop_list for uv in pair]
		mesh.uv_layers[g].data.foreach_set("uv", per_loop_list)
	
	
	createMaterials(files, submesh_name, vertexGroups, materials, meshObject)
	
	t3 = time.time()
	wd={0:{'boneNames':[], 'weights':[]}}
	for w in range(wCount):
		group = getGroup(w, vertexGroups)
		wd[w] = {'boneNames':[], 'weights':[]}
		b_temp = []
		for m in range(subRange):
			b_id = struct.unpack("B",md.read(1))[0]
			b_temp.append(b_id)
		
		for b in range(subRange):
			weight = struct.unpack("B",md.read(1))[0] /255.0
			bt = b_temp[b]
			if weight != 0:
				bone_id = group['bones'][bt]
				bone_name = joint_data[bone_id]["name"]
				wd[w]['boneNames'].append(bone_name)
				wd[w]['weights'].append(weight)
	t4 = time.time()
	weightTime = t4 - t3
	times["weights"] = weightTime
	
	
	
	for x in wd:
		for p in range(len(wd[x]['weights'])):
			vertexWeight = wd[x]['weights'][p]
			boneName = wd[x]['boneNames'][p]
			vertGroup = meshObject.vertex_groups.get(boneName)
			if not vertGroup:
				vertGroup = meshObject.vertex_groups.new(name = boneName)
			vertGroup.add([x], vertexWeight, 'ADD')
	mod = meshObject.modifiers.new(type="ARMATURE", name="ArmatureMOD")
	mod.use_vertex_groups = True
	mod.object = armature_ob
	
	
	if arm:
		bpy.data.collections[meshName].objects.link(armature_ob)
		bpy.context.scene.collection.objects.unlink(armature_ob)
	
	elapsed = time.time() - t1
	times["everything"] = elapsed
	#print ("\n\n\n\n")
	#print ('Imported file in ', elapsed, ' seconds.')
	return times
	
	md.close()
	ua.close()