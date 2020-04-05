#!/usr/bin/env python
# -*- Mode: Python -*-
# -*- coding: utf-8 -*-


import os
import re
import io
import sys
import math
import time
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
from transforms3d.euler import euler2mat, mat2euler, quat2euler
from lwsdk.pris.layout.cs import itemiconscale, bonemayastyledraw

#from Skin import *
#from textures import *
from materials import *


from lwsdk import Vector
from lwsdk.pris.layout import moninit, monstep, monend




__author__     = "野村 哲也 Nomura Tetsuya"
__date__       = "1 Apr 2020"
__copyright__  = "Copyright © スクウェア・エニックス・ビジネス・ディビジョン1 Square Enix Business Division 1"
__version__    = "1.0"
__maintainer__ = "北瀬 佳範 Yoshinori Kitase"
__email__      = "..."
__status__     = "Testing"
__lwver__      = "2019"




class import_7R_SKEL(lwsdk.IGeneric):
	def __init__(self, context):
		super(import_7R_SKEL, self).__init__()
		self._filepath = "*.uexp"
	
	def process(self, ga):
		ui = lwsdk.LWPanels()
		panel = ui.create('Final Fantasy 7:Remake  Import')
		
		controlWidth = 64
		c1 = panel.load_ctl('Select File',controlWidth)
		c1.set_str(self._filepath)
		
		if panel.open(lwsdk.PANF_BLOCKING | lwsdk.PANF_CANCEL) == 0:
			ui.destroy(panel)
			return lwsdk.AFUNC_OK
		
		self.filepath = c1.get_str()
		progress_count = 8
		
		
		t1 = time.time()
		
		
		interface_info = lwsdk.LWInterfaceInfo()
		if not (interface_info.generalFlags & lwsdk.LWGENF_PARENTINPLACE):
			ga.evaluate(ga.data, "ParentInPlace")
		
		#set bind pose at frame -10
		ga.evaluate(ga.data, "GoToFrame -10")
		
		interface_info = lwsdk.LWInterfaceInfo()
		selected_items = interface_info.selected_items()
		
		
		
		#if a mesh not selected create a parent null for the bones
		if not selected_items:
			result = ga.evaluate(ga.data, "AddNull Root")
			interface_info = lwsdk.LWInterfaceInfo()
			selected_items = interface_info.selected_items()
			buildItemID = selected_items[0]
		else:
			item_info = lwsdk.LWItemInfo()
			mytype = item_info.type(selected_items[0])
			if mytype==lwsdk.LWI_OBJECT:
				buildItemID = selected_items[0]
			else:
				result = ga.evaluate(ga.data, "AddNull Root")
				interface_info = lwsdk.LWInterfaceInfo()
				selected_items = interface_info.selected_items()
				buildItemID = selected_items[0]
		
		#get weightmap count
		object_functions = lwsdk.LWObjectFuncs()
		numWeights = object_functions.numVMaps(lwsdk.LWVMAP_WGHT)
		
		
		
		
		
		
		
		files = path_wrangler(self.filepath)
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
		
		UVs0 = []
		UVs1 = []
		UVs2 = []
		UVs3 = []
		UVs4 = []
		
		faces = []
		
		
		names = readUasset(ua)
		ua.close()
		
		
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
		joint_names = []
		for i in xrange(boneCount):
			string_index = struct.unpack("<L",md.read(4))[0]
			jName = names[string_index]
			unk = struct.unpack("<L",md.read(4))[0]
			parent = struct.unpack("<l",md.read(4))[0]
			
			joint_data[i] = {"name": jName, "parent":parent}
		
		
		
		
		boneCount2 = struct.unpack("<L",md.read(4))[0]
		
		progress_count += boneCount2
		if not moninit(progress_count, "Importing", title='Progress'):
			raise Exception('Hell!')
		
		
		
		
		
		
		
		
		boneArray = []
		psn = {}
		IDs = []
		for bn in range(boneCount2):
			boneName = joint_data[bn]["name"]
			BNparent = joint_data[bn]["parent"]
			
			m1 = struct.unpack("<10f",md.read(40))
			
			ps0 = (m1[4],m1[5],m1[6])
			#BNps = np.asarray(ps0)
			
			rt0_ = (m1[3],m1[0],m1[1],m1[2])
			rt0 = quat2mat(rt0_)
			
			
			if BNparent == -1:
				BNparent = 0
			
			#BNps = [mi[3,1], mi[3,2], mi[3,0]]
			BNps = ps0
			psn[bn] = BNps
			
			#BNrt = mat2euler(mi, axes='ryxz')
			
			
			
			ga.evaluate(ga.data, "SelectItem %s" % lwsdk.itemid_to_str(buildItemID))
			layoutCommand = "AddBone " + boneName
			result = ga.evaluate(ga.data, layoutCommand)
			
			# no influence except for weight maps
			result = ga.evaluate(ga.data, 'BoneStrength 0')
			interface_info = lwsdk.LWInterfaceInfo()
			selected_items = interface_info.selected_items()
			itemID = selected_items[0]
			IDs.append(itemID)
			
			
			#UpdateMotion needed for parent in place
			if bn != 0:
				ga.evaluate(ga.data, 'UpdateMotion')
				ga.evaluate(ga.data, "ParentItem %s" % lwsdk.itemid_to_str(IDs[BNparent]))
			
			layoutCommand = "Position " + str(BNps[0]) + " " + str(BNps[1]) + " " + str(BNps[2])
			result = ga.evaluate(ga.data, layoutCommand)
			
			if bn == 0:
				result = ga.evaluate(ga.data, "BoneRestLength 0.5")
			else:
				lenX = psn[BNparent][0] - BNps[0]
				lenY = psn[BNparent][1] - BNps[1]
				lenZ = psn[BNparent][2] - BNps[2]
				
				#dont use full bone length....dummy
				boneLength = math.sqrt(lenX*lenX + lenY*lenY + lenZ*lenZ)*0.6
				result = ga.evaluate(ga.data, "BoneRestLength "+str(boneLength))
			
			#BNrt = quat2euler(rt0_, axes='szyx')
			BNrt = quat2euler(rt0_, axes='ryxz')
			rotx = (180.0/math.pi) * BNrt[0]
			roty = (180.0/math.pi) * BNrt[1]
			rotz = (180.0/math.pi) * BNrt[2]
			
			
			layoutCommand = "Rotation " + str(rotx) + " " + str(roty) + " " + str(rotz)
			result = ga.evaluate(ga.data, layoutCommand)
			
			if bn == 0:
				layoutCommand = "Rotation " + str(180.0) + " " + str(180.0) + " " + str(0.0)
				result = ga.evaluate(ga.data, layoutCommand)
			
			
			# if 'autokey' is not turned on, we need to explicitly
			# create keys for the object at the current time offset
			if not (interface_info.generalFlags & lwsdk.LWGENF_AUTOKEY):
				ga.evaluate(ga.data, "CreateKey %f" % interface_info.curTime)
			
			#keys created at frame -10 so delete any at frame 0
			ga.evaluate(ga.data, 'DeleteKey 0')
			
			
			if(numWeights > 0):
				if bn != 0:
					for b in range(numWeights):
						weightName = object_functions.vmapName(lwsdk.LWVMAP_WGHT, b)
						if weightName == boneName:
							layoutCommand = 'BoneWeightMapName ' + boneName
							result = ga.evaluate(ga.data, layoutCommand)
							result = ga.evaluate(ga.data, 'BoneWeightMapOnly')
			ga.evaluate(ga.data, 'RecordRestPosition')
			
			monstep()
		
		
		
		
		#-----------------------------------------------------------#
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
		
		process_surfaces(files, vertexGroups, materials)
		#-----------------------------------------------------------#
		
		
		
		
		ga.evaluate(ga.data, 'SelectAllBones')
		#ga.evaluate(ga.data, 'RecordRestPosition')
		bonemayastyledraw()
		itemiconscale(0.2)
		
		monend()
		
		elapsed = time.time() - t1
		print "Time: " + str(elapsed)
		
		md.close()
		
		return lwsdk.AFUNC_OK

ServerTagInfo = [ ( "Final Fantasy 7: Remake  Skeleton Importer", lwsdk.SRVTAG_USERNAME | lwsdk.LANGID_USENGLISH ), \
( "Import FF7R Skeleton", lwsdk.SRVTAG_BUTTONNAME | lwsdk.LANGID_USENGLISH ), \
( "model/import", lwsdk.SRVTAG_MENU | lwsdk.LANGID_USENGLISH ) ]
#( "Utilities/File", lwsdk.SRVTAG_MENU | lwsdk.LANGID_USENGLISH ) ]

ServerRecord = { lwsdk.GenericFactory("LW_ImportFF7R_SKEL", import_7R_SKEL) : ServerTagInfo }