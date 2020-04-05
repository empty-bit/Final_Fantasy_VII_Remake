#!/usr/bin/env python
# -*- Mode: Python -*-
# -*- coding: utf-8 -*-


import gc
import os
import re
import io
import sys
import math
import time
import lwsdk
import struct
import numpy as np
from utils import *
from numpy.linalg import inv
from functools import partial
from transforms3d.quaternions import quat2mat

#from Skin import *
#from textures import *
#from materials import *


from lwsdk import ModCommand, Vector
from lwsdk.pris.modeler import init, getpolygons, selpolygon, editbegin, editend, moninit, monstep, monend


if not init(ModCommand()):
	raise Exception('Failed to initialize PRIS')




__author__     = "野村 哲也 Nomura Tetsuya"
__date__       = "1 Mar 2020"
__copyright__  = "Copyright © スクウェア・エニックス・ビジネス・ディビジョン1 Square Enix Business Division 1"
__version__    = "1.0"
__maintainer__ = "北瀬 佳範 Yoshinori Kitase"
__email__      = "..."
__status__     = "Testing"
__lwver__      = "2019"




SKLGNS = True



class import_7R(lwsdk.ICommandSequence):
	def __init__(self, context):
		super(import_7R, self).__init__()
		self._filepath = "*.uexp"
	
	def get_commands(self, mod_command):
		command_list = {}
		for command in ["SETLAYER", "SETLAYERNAME", "NEW","SETOBJECT"]:
			command_list[command] = mod_command.lookup(mod_command.data, command)
		return command_list
	
	def process(self, mod_command):
		ui = lwsdk.LWPanels()
		panel = ui.create('Final Fantasy 7:Remake Import')
		
		controlWidth = 64
		c1 = panel.load_ctl('Select File',controlWidth)
		c1.set_str(self._filepath)
		
		if panel.open(lwsdk.PANF_BLOCKING | lwsdk.PANF_CANCEL) == 0:
			ui.destroy(panel)
			return lwsdk.AFUNC_OK
		
		self.filepath = c1.get_str()
		edit_op_result = lwsdk.EDERR_NONE
		cs_dict = self.get_commands(mod_command)
		
		progress_count = 8
		
		
		
		
		
		cs_test0 = mod_command.lookup(mod_command.data, "cmdseq")
		
		
		
		
		
		t1 = time.time()
		
		files = path_wrangler(self.filepath)
		files.get_files()
		#Dump(files)
		
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
		
		UVs0 = []
		UVs1 = []
		UVs2 = []
		UVs3 = []
		UVs4 = []
		
		faces = []
		
		
		names = readUasset(ua)
		ua.close()
		
		
		mod_command.undoGroupBegin()
		
		
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
		
		progress_count += materialCount
		
		
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
		joint_names = []
		for i in xrange(boneCount):
			string_index = struct.unpack("<L",md.read(4))[0]
			jName = names[string_index]
			unk = struct.unpack("<L",md.read(4))[0]
			parent = struct.unpack("<l",md.read(4))[0]
			
			joint_data[i] = {"name": jName, "parent":parent}
			joint_names.append(jName)
		
		
		
		
		boneCount2 = struct.unpack("<L",md.read(4))[0]
		
		if not moninit(progress_count, "Importing", title='Progress'):
			raise Exception('Hell!')
		
		layerindex = 1
		for i in range(boneCount):
			m1 = struct.unpack("<10f",md.read(40))
		monstep()
		
		
		
		cs_options = lwsdk.marshall_dynavalues(str(layerindex))
		result = mod_command.execute(mod_command.data, cs_dict["SETLAYER"], cs_options, lwsdk.OPSEL_USER)
		cs_options = lwsdk.marshall_dynavalues(meshName)
		result = mod_command.execute(mod_command.data, cs_dict["SETLAYERNAME"], cs_options, lwsdk.OPSEL_USER)
		layerindex += 1
		
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
			vertexGroups[ID]['bones_np'] = np.zeros((boneCount2,), dtype=int)
			bone_names = []
			for bn in xrange(count):
				bid = struct.unpack("<H",md.read(2))[0]
				vertexGroups[ID]['bones_np'][bn] = bid
				vertexGroups[ID]['bones'].append(bid)
				bone_names.append(joint_data[bid]["name"])
			# pragma endregion bone palette
			
			size = struct.unpack("<L",md.read(4))[0]
			stop = start + size
			vertexGroups[ID]['range'] = np.arange(start, stop)
			vertexGroups[ID]["start"] = start
			vertexGroups[ID]["stop"]  = stop
			vertexGroups[ID]["size"]  = size
			vertexGroups[ID]["names"] = bone_names
			
			
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
		fi_0[:,[0,1]] = fi_0[:,[1,0]]
		faces = fi_0.tolist()
		
		
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
		VA = pos.tolist()
		
		
		
		if uv_count > 0:
			uvData_0 = vi[:,20:24].ravel().view(dtype = '<f2').reshape((vCount, 2))
			uvData_0[:,1:2] *= -1
			uvData_0[:,1:2] += 1
			UVs0 = uvData_0.tolist()
		
		if uv_count > 1:
			uvData_1 = vi[:,24:28].ravel().view(dtype = '<f2').reshape((vCount, 2))
			uvData_1[:,1:2] *= -1
			uvData_1[:,1:2] += 1
			UVs1 = uvData_1.tolist()
		
		if uv_count > 2:
			uvData_2 = vi[:,28:32].ravel().view(dtype = '<f2').reshape((vCount, 2))
			uvData_2[:,1:2] *= -1
			uvData_2[:,1:2] += 1
			UVs2 = uvData_2.tolist()
		
		if uv_count > 3:
			uvData_3 = vi[:,32:36].ravel().view(dtype = '<f2').reshape((vCount, 2))
			uvData_3[:,1:2] *= -1
			uvData_3[:,1:2] += 1
			UVs3 = uvData_3.tolist()
		
		if uv_count > 4:
			uvData_4 = vi[:,36:40].ravel().view(dtype = '<f2').reshape((vCount, 2))
			uvData_4[:,1:2] *= -1
			uvData_4[:,1:2] += 1
			UVs4 = uvData_4.tolist()
		monstep()
		
		
		
		mesh_edit_op = mod_command.editBegin(0, 0, lwsdk.OPSEL_USER)
		
		#points
		map(lambda x: v_f(x,vertexArray,mesh_edit_op), VA)
		monstep()
		
		
		#faces
		material_IDs = np.empty([1, fCount], dtype='U32').reshape(fCount//3, 3)
		for g in vertexGroups:
			h = np.in1d(fi_0, vertexGroups[g]['range']).reshape(fi_0.shape)
			m = np.all(h, axis = 1)
			material_IDs[m] = materials[g]['name']
		monstep()
		map(lambda x,y: f_f(x,vertexArray,mesh_edit_op,y), faces,material_IDs)
		monstep()
		
		
		#UVs
		val = 0
		if uv_count > 0:
			map(lambda x,y: uv_f(x,y,val,mesh_edit_op,meshName), vertexArray, UVs0)
			val += 1
		
		if uv_count > 1:
			map(lambda x,y: uv_f(x,y,val,mesh_edit_op,meshName), vertexArray, UVs1)
			val += 1
		
		if uv_count > 2:
			map(lambda x,y: uv_f(x,y,val,mesh_edit_op,meshName), vertexArray, UVs2)
			val += 1
		
		if uv_count > 3:
			map(lambda x,y: uv_f(x,y,val,mesh_edit_op,meshName), vertexArray, UVs3)
			val += 1
		
		if uv_count > 4:
			map(lambda x,y: uv_f(x,y,val,mesh_edit_op,meshName), vertexArray, UVs4)
			val += 1
		monstep()
		
		
		
		
		
		
		
		unkS = struct.unpack("<H",md.read(2))[0]
		extraBoneWeights = struct.unpack("<L",md.read(4))[0]
		wCount = struct.unpack("<L",md.read(4))[0]
		stride = struct.unpack("<L",md.read(4))[0]
		wCount2 = struct.unpack("<L",md.read(4))[0]
		
		subStride = stride // 2
		
		for q in xrange(len(vertexGroups)):
			boneNames = vertexGroups[q]["names"]
			start = vertexGroups[q]["start"]
			stop  = vertexGroups[q]["stop"]
			
			for j in xrange(start,stop):
				b0 = struct.unpack("B",md.read(1))[0]
				b1 = struct.unpack("B",md.read(1))[0]
				b2 = struct.unpack("B",md.read(1))[0]
				b3 = struct.unpack("B",md.read(1))[0]
				b4 = struct.unpack("B",md.read(1))[0]
				b5 = struct.unpack("B",md.read(1))[0]
				b6 = struct.unpack("B",md.read(1))[0]
				b7 = struct.unpack("B",md.read(1))[0]
				
				bn0 = boneNames[b0]
				bn1 = boneNames[b1]
				bn2 = boneNames[b2]
				bn3 = boneNames[b3]
				bn4 = boneNames[b4]
				bn5 = boneNames[b5]
				bn6 = boneNames[b6]
				bn7 = boneNames[b7]
				
				
				w0 = struct.unpack("B",md.read(1))[0] /255.0
				w1 = struct.unpack("B",md.read(1))[0] /255.0
				w2 = struct.unpack("B",md.read(1))[0] /255.0
				w3 = struct.unpack("B",md.read(1))[0] /255.0
				w4 = struct.unpack("B",md.read(1))[0] /255.0
				w5 = struct.unpack("B",md.read(1))[0] /255.0
				w6 = struct.unpack("B",md.read(1))[0] /255.0
				w7 = struct.unpack("B",md.read(1))[0] /255.0
				
				
				mesh_edit_op.pntVMap(mesh_edit_op.state, vertexArray[j], lwsdk.LWVMAP_WGHT, bn0, [w0])
				mesh_edit_op.pntVMap(mesh_edit_op.state, vertexArray[j], lwsdk.LWVMAP_WGHT, bn1, [w1])
				mesh_edit_op.pntVMap(mesh_edit_op.state, vertexArray[j], lwsdk.LWVMAP_WGHT, bn2, [w2])
				mesh_edit_op.pntVMap(mesh_edit_op.state, vertexArray[j], lwsdk.LWVMAP_WGHT, bn3, [w3])
				mesh_edit_op.pntVMap(mesh_edit_op.state, vertexArray[j], lwsdk.LWVMAP_WGHT, bn4, [w4])
				mesh_edit_op.pntVMap(mesh_edit_op.state, vertexArray[j], lwsdk.LWVMAP_WGHT, bn5, [w5])
				mesh_edit_op.pntVMap(mesh_edit_op.state, vertexArray[j], lwsdk.LWVMAP_WGHT, bn6, [w6])
				mesh_edit_op.pntVMap(mesh_edit_op.state, vertexArray[j], lwsdk.LWVMAP_WGHT, bn7, [w7])
			monstep()
		
		
		mesh_edit_op.done(mesh_edit_op.state, edit_op_result, 0)
		monend()
		mod_command.undoGroupEnd()
		
		
		
		elapsed = time.time() - t1
		print "Time: " + str(elapsed)
		
		md.close()
		
		return lwsdk.AFUNC_OK

ServerTagInfo = [ ( "Final Fantasy 7: Remake Model Importer", lwsdk.SRVTAG_USERNAME | lwsdk.LANGID_USENGLISH ), \
( "Import FF7R", lwsdk.SRVTAG_BUTTONNAME | lwsdk.LANGID_USENGLISH ), \
( "Utilities/File", lwsdk.SRVTAG_MENU | lwsdk.LANGID_USENGLISH ) ]

ServerRecord = { lwsdk.CommandSequenceFactory("LW_ImportFF7R", import_7R) : ServerTagInfo }