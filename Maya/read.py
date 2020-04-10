import os
import re
import io
import sys
import math
import time
import struct
import numpy as np
import maya.mel as mm
import pymel.core as pm
import maya.cmds as cmds
import maya.OpenMaya as om
from numpy.linalg import inv
from functools import partial
import maya.api.OpenMaya as om2
import maya.OpenMayaAnim as oma
m_util = om.MScriptUtil()



from utils import *
from materials import *




def readFile(filepath):
	files = path_wrangler(filepath)
	files.get_files()

	md = open(files.data['uexp'], 'rb')
	ua = open(files.data['uasset'], 'rb')

	meshName = files.data['meshName']
	submesh_name = files.data['submesh_name']

	arm = False
	weightData = {}
	Weight_array = []
	vertexArray = []
	NA = []
	normal_array = []

	faces = []

	U0 = om2.MFloatArray()
	V0 = om2.MFloatArray()
	U1 = om2.MFloatArray()
	V1 = om2.MFloatArray()
	U2 = om2.MFloatArray()
	V2 = om2.MFloatArray()
	U3 = om2.MFloatArray()
	V3 = om2.MFloatArray()
	U4 = om2.MFloatArray()
	V4 = om2.MFloatArray()
	U5 = om2.MFloatArray()
	V5 = om2.MFloatArray()


	t1 = time.time()
	names = readUasset(ua)


	pattern0 = re.compile(b'\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00........')
	for x in xrange(20000):
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
	for m in xrange(materialCount):
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
	joint_data = {}
	bt = np.empty([1, boneCount], dtype='U32')
	for i in xrange(boneCount):
		string_index = struct.unpack("<L",md.read(4))[0]
		jName = names[string_index]
		unk = struct.unpack("<L",md.read(4))[0]
		parent = struct.unpack("<l",md.read(4))[0]
		
		joint_data[i] = {"name": jName, "parent":parent}
		bt[0,i] = jName

	boneCount2 = struct.unpack("<L",md.read(4))[0]
	bone_list = []
	boneArray = []
	for k in xrange(boneCount2):
		m1 = struct.unpack("<10f",md.read(40))
		boneName = joint_data[k]["name"]
		BNparent = joint_data[k]["parent"]
		boneArray.append(boneName)
		
		BNps = om.MVector(-m1[5],-m1[6],m1[4])
		BNrt = om.MQuaternion(m1[1],m1[2],-m1[0],-m1[3])
		BNsc = om.MVector(-m1[8],-m1[9],-m1[7])
		
		if BNparent == -1:
			cmds.select(clear=True)
		else:
			pm.select(bone_list[BNparent])
		newBone = pm.joint( p=(0,0,0), name=boneName , radius = 0.1 )
		newBone.setTranslation(BNps)
		newBone.setOrientation(BNrt)
		newBone.setScale(BNsc)
		
		bone_list.append(newBone)
	arm = True
	



	boneCount3 = struct.unpack("<L",md.read(4))[0]
	md.seek(boneCount3 * 12, 1)


	vertexGroups = {}
	unk0 = struct.unpack("<L",md.read(4))[0]
	unk1 = struct.unpack("B",md.read(1))[0]
	unk2 = struct.unpack("B",md.read(1))[0]
	groupCount = struct.unpack("<L",md.read(4))[0]
	for m in xrange(groupCount):
		z1 = struct.unpack("<H",md.read(2))[0]
		ID = struct.unpack("<H",md.read(2))[0]
		
		md.seek(24,1)
		vertexGroups[ID] = {'range':0, 'bones':[]}
		
		# pragma region bone palette
		start = struct.unpack("<L",md.read(4))[0]
		count = struct.unpack("<L",md.read(4))[0]
		bt = np.empty([1, count], dtype='U32')
		for bn in xrange(count):
			bid = struct.unpack("<H",md.read(2))[0]
			vertexGroups[ID]['bones'].append(bid)
			bt[0,bn] = joint_data[bid]["name"]
		# pragma endregion bone palette
		
		size = struct.unpack("<L",md.read(4))[0]
		stop = start + size
		vertexGroups[ID]['range'] = range(start, stop)
		vertexGroups[ID]["start"] = start
		vertexGroups[ID]["stop"]  = stop
		vertexGroups[ID]["size"]  = size
		vertexGroups[ID]["names"] = bt
		
		
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
	fi = np.fromfile(md, dtype = 'B', count = faceByteCount)
	if stride == 4:
		fi_0 = fi.view(dtype = '<L').reshape(fCount//3, 3)
	elif stride == 2:
		fi_0 = fi.view(dtype = '<H').reshape(fCount//3, 3)
	fi_1 = fi_0.ravel()
	faces = tuple(fi_1)

	pCounts =[3]*(len(faces)//3)

	gh = pCounts[0]




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
	pos[:,[0,2]] = pos[:,[2,0]]
	pos[:,[0,1]] = pos[:,[1,0]]
	pos[:,[2]] *= -1
	positions = pos.tolist()
	VA = om2.MFloatPointArray(positions)
	
	
	if uv_count > 0:
		uvData_ = vi[:,20:24].ravel().view(dtype = '<f2').reshape((vCount, 2))
		uvData_[:,1:2] *= -1
		uvData_[:,1:2] += 1
		uvData = tuple(map(tuple, uvData_))
		u = zip(*uvData)[0]
		v = zip(*uvData)[1]
		U0.copy(u)
		V0.copy(v)
	if uv_count > 1:
		uvData_ = vi[:,24:28].ravel().view(dtype = '<f2').reshape((vCount, 2))
		uvData_[:,1:2] *= -1
		uvData_[:,1:2] += 1
		uvData = tuple(map(tuple, uvData_))
		u = zip(*uvData)[0]
		v = zip(*uvData)[1]
		U1.copy(u)
		V1.copy(v)
	if uv_count > 2:
		uvData_ = vi[:,28:32].ravel().view(dtype = '<f2').reshape((vCount, 2))
		uvData_[:,1:2] *= -1
		uvData_[:,1:2] += 1
		uvData = tuple(map(tuple, uvData_))
		u = zip(*uvData)[0]
		v = zip(*uvData)[1]
		U2.copy(u)
		V2.copy(v)
	if uv_count > 3:
		uvData_ = vi[:,32:36].ravel().view(dtype = '<f2').reshape((vCount, 2))
		uvData_[:,1:2] *= -1
		uvData_[:,1:2] += 1
		uvData = tuple(map(tuple, uvData_))
		u = zip(*uvData)[0]
		v = zip(*uvData)[1]
		U3.copy(u)
		V3.copy(v)
	if uv_count > 4:
		uvData_ = vi[:,36:40].ravel().view(dtype = '<f2').reshape((vCount, 2))
		uvData_[:,1:2] *= -1
		uvData_[:,1:2] += 1
		uvData = tuple(map(tuple, uvData_))
		u = zip(*uvData)[0]
		v = zip(*uvData)[1]
		U4.copy(u)
		V4.copy(v)




	mesh = om2.MFnMesh()
	ShapeMesh = cmds.group(em=True)
	parentOwner = get_mobject(ShapeMesh)
	meshMObj = mesh.create(VA, pCounts, faces, uValues=U0, vValues=V0, parent=parentOwner)
	
	
	cmds.sets( ShapeMesh, e=True,forceElement='initialShadingGroup')
	
	
	cmds.polyUVSet(rename=True, newUVSet='map_0', uvSet=mesh.currentUVSetName(-1))
	mesh.setUVs (U0, V0, 'map_0')
	mesh.assignUVs (pCounts, faces, 'map_0')
	
	
	cmds.rename(meshName)
	
	s1 = cmds.ls(sl=1)
	s2 = s1[0]
	shapeName = s2.encode('ascii','ignore')
	
	
	
	
	if uv_count > 1:
		mesh.createUVSet('map_1')
		mesh.setUVs (U1, V1, 'map_1')
		mesh.assignUVs (pCounts, faces, 'map_1')
	if uv_count > 2:
		mesh.createUVSet('map_2')
		mesh.setUVs (U2, V2, 'map_2')
		mesh.assignUVs (pCounts, faces, 'map_2')
	if uv_count > 3:
		mesh.createUVSet('map_3')
		mesh.setUVs (U3, V3, 'map_3')
		mesh.assignUVs (pCounts, faces, 'map_3')
	if uv_count > 4:
		mesh.createUVSet('map_4')
		mesh.setUVs (U4, V4, 'map_4')
		mesh.assignUVs (pCounts, faces, 'map_4')
	
	
	
	
	unkS = struct.unpack("<H",md.read(2))[0]
	extraBoneWeights = struct.unpack("<L",md.read(4))[0]
	wCount = struct.unpack("<L",md.read(4))[0]
	stride = struct.unpack("<L",md.read(4))[0]
	wCount2 = struct.unpack("<L",md.read(4))[0]
	
	subStride = int(stride / 2)
	
	clusterName = shapeName + '_' + 'skinCluster'
	pm.skinCluster(boneArray[:], shapeName, sm=1, mi=8, omi=1, n=clusterName)
	
	skin = mm.eval('findRelatedSkinCluster "'+s2+'"')
	
	sel = om.MSelectionList();
	sel.add(shapeName)
	meshMObject = om.MObject()
	sel.getDependNode(0,meshMObject)
	
	sel2 = om.MSelectionList();
	sel2.add(skin)
	skinMObject = om.MObject()
	sel2.getDependNode(0,skinMObject)
	
	FnSkin = oma.MFnSkinCluster(skinMObject)
	dag_path, skinMObject = get_skin_dag_path_and_mobject(FnSkin)
	weights = om.MDoubleArray()
	influence_paths = om.MDagPathArray()
	influence_count = FnSkin.influenceObjects(influence_paths)
	components_per_influence = weights.length() / influence_count
	
	# influences
	unused_influences = list()
	influences = [influence_paths[inf_count].partialPathName() for inf_count in xrange(influence_paths.length())]
	
	wSize = vCount*influence_count
	weights = om.MDoubleArray(wSize,0.0)
	
	
	w_byteCount = wCount * stride
	wi = np.fromfile(md, dtype = 'B', count = w_byteCount).reshape((wCount, stride))
	wi_b = wi[:,:subStride].ravel().view().reshape((wCount, subStride))
	wi_w = wi[:,subStride:stride].ravel().view().reshape((wCount, subStride)).astype(np.float64)
	wi_w /= 255.0
	
	def do_stuff(n):
		fg = influences.index(L[n])
		idx = fg + (j * influence_count)
		weights[idx] = W[n]
	
	
	for h in xrange(len(vertexGroups)):
		crnt_grp = vertexGroups[h]
		g_names = crnt_grp["names"]
		g_range = crnt_grp["range"]
		for j in g_range:
			Wt = np.trim_zeros(wi_w[j], 'b')
			W = tuple(Wt)
			a = Wt.shape[0]
			ids = wi_b[j,:a]
			L = tuple(g_names[0,ids])
			
			map(do_stuff, range(len(L)))
	influence_array = om.MIntArray(influence_count)
	m_util.createIntArrayFromList(range(influence_count),influence_array)
	FnSkin.setWeights(dag_path, skinMObject, influence_array, weights, False)
	
	
	
	
	createMaterials(files, vertexGroups, materials, shapeName)
	
	pm.select(shapeName)
	cmds.viewFit()
	
	elapsed = time.time() - t1
	return elapsed
	
	md.close()
	ua.close()