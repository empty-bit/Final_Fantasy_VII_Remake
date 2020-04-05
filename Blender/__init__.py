# -*- coding: utf-8 -*-
import os
import re
import bpy
import sys
import math
import struct
import codecs
import time
import numpy as np
import bmesh as bmesh
import mathutils as mu
from random import randint

from rna_prop_ui import rna_idprop_ui_prop_get as prop
from bpy_extras.io_utils import unpack_list, unpack_face_list

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from numpy.linalg import inv
import bpy.utils.previews

from .utils import *
from .read import *

bl_info = {
	"name" : "FFVIIR",
	"description" : "Import models from Final Fantasy VII Remake.",
	"author" : "野村 哲也 Nomura Tetsuya",
	"copyright" : "Copyright © スクウェア・エニックス・ビジネス・ディビジョン1 Square Enix Business Division 1",
	"version" : (1, 0, 0),
	"blender" : (2, 82, 0),
	"location" : "File > Import > Final Fantasy VII Remake (.uexp)",
	"warning" : "",
	"support": "TESTING",
	"category" : "Import"
}




class Import_FF7R(Operator, ImportHelper):
	"""This appears in the tooltip of the operator and in the generated docs"""
	bl_idname = "square_enix.ff_7r"
	bl_label  = "Import UEXP"
	
	filename_ext = ".uexp"
	
	
	filter_glob: StringProperty(
			default="*.uexp",
			options={'HIDDEN'},
	)
	
	dump_textures: BoolProperty(
		name="Dump Textures",
		description="Create PNG files",
		default = False
	)
	
	def execute(self, context):
		time = readFile(self.filepath, self.dump_textures)
		for k,v in time.items():
			self.report({'INFO'}, 'Time for ' + k + ': ' + str(v) + ' seconds.')
		return {'FINISHED'}



def menu_func_import(self, context):
	self.layout.operator(Import_FF7R.bl_idname, text="FFVIIR (.uexp)")

def addToAddMeshMenu(self, context):
	ico = preview_collections["main"]["custom_icon"]
	self.layout.operator(Import_FF7R.bl_idname, text="FFVIIR", icon_value=ico.icon_id)


preview_collections = {}


def register():
	bpy.utils.register_class(Import_FF7R)
	bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
	bpy.types.VIEW3D_MT_mesh_add.append(addToAddMeshMenu)
	
	
	fileList = []
	script_path = os.path.realpath(__file__)
	icons_dir = os.path.join(os.path.dirname(script_path), "icons")
	
	for i in os.listdir(icons_dir):
		if os.path.isdir(icons_dir + i):
			continue
		else:
			fileList.append(i)
	
	numFiles = len(fileList) - 1
	rVal = randint(0,numFiles)
	random_icon = os.path.join(icons_dir, fileList[rVal])
	
	
	custom_icon = bpy.utils.previews.new()
	custom_icon.load("custom_icon", os.path.join(icons_dir, random_icon), 'IMAGE')
	preview_collections["main"] = custom_icon


def unregister():
	bpy.utils.unregister_class(Import_FF7R)
	bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
	bpy.types.VIEW3D_MT_mesh_add.remove(addToAddMeshMenu)
	
	for pcoll in preview_collections.values():
		bpy.utils.previews.remove(pcoll)
	preview_collections.clear()