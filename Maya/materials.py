import os
import io
import sys
import string
import struct
from arnold import *
import pymel.core as pm
import maya.cmds as cmds

from utils import *


#old
'''
def createImage(_image, _material, _input):
	# no connected file texture, so make a new one
	newFile = cmds.shadingNode('file',asTexture=1)
	newPlacer = cmds.shadingNode('place2dTexture',asUtility=1)
	
	# make common connections between place2dTexture and file texture
	connections = ['rotateUV','offset','noiseUV','vertexCameraOne','vertexUvThree','vertexUvTwo','vertexUvOne','repeatUV','wrapV','wrapU','stagger','mirrorU','mirrorV','rotateFrame','translateFrame','coverage']
	
	cmds.connectAttr(newPlacer+'.outUV',newFile+'.uvCoord')
	cmds.connectAttr(newPlacer+'.outUvFilterSize',newFile+'.uvFilterSize')
	for i in connections:
		cmds.connectAttr(newPlacer+'.'+i,newFile+'.'+i)
	
	# now connect the file texture output to the material input
	cmds.connectAttr(newFile+'.outColor',_material+'.'+_input,f=1)
		
	# now set attributes on the file node.
	cmds.setAttr(newFile+'.fileTextureName',_image,type='string')
	cmds.setAttr(newFile+'.filterType',0)
'''

#Arnold
def createImage(_image, _material, _input, uv_map):
	ai_T = cmds.shadingNode('aiImage', asShader=True)
	cmds.setAttr(ai_T +'.filename', _image, type="string")
	cmds.setAttr(ai_T +'.uvset', uv_map, type="string")
	cmds.connectAttr(ai_T+'.outColor',_material+'.'+_input,f=1)
	return ai_T

def createShader(in_node, in_conn, out_node, out_conn):
	new_node = cmds.shadingNode(in_node, asShader=True)
	cmds.connectAttr(new_node + '.' + in_conn, out_node + '.' + out_conn, f=1)
	return new_node


def check():
	shapesInSel = cmds.ls(dag=1,o=1,s=1,sl=1)
	shadingGrps = cmds.listConnections(shapesInSel,type='shadingEngine')
	return cmds.ls(cmds.listConnections(shadingGrps),materials=1)



def createMaterials(files_, vertexGroups_, materials_, shapeName_):
	textures = getMaterialTypes(files_)
	
	for k in range(len(vertexGroups_)):
		mat_name = materials_[k]['name']
		texture_list = textures[mat_name]
		start = vertexGroups_[k]["start"]
		stop  = vertexGroups_[k]["stop"]
		
		#print "Material name: " + mat_name
		#print "Start: " + str(start)
		#print "Stop: " + str(stop)
		
		
		
		if cmds.objExists(mat_name):
			pm.select('%s.f[%d:%d]'%(shapeName_,start,stop))
			cmds.hyperShade(a=mat_name, assign=True)
			cmds.select(clear=True)
		else:
			matSG = mat_name + "__aiSSG"
			aiShader = cmds.shadingNode('aiStandardSurface', asShader=True, n=mat_name)
			shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=matSG)
			cmds.connectAttr('%s.outColor' %aiShader ,'%s.surfaceShader' %shading_group)
			
			cmds.setAttr(aiShader +'.specular', 0.1)
			cmds.setAttr(aiShader +'.specularRoughness', 0.9)
			
			pm.select('%s.vtx[%d:%d]'%(shapeName_,start,stop))
			face_selection = cmds.polyListComponentConversion(fv=True, tf=True)
			cmds.select(clear=True)
			for p in face_selection:
				pm.select(p, add = True)
			
			cmds.hyperShade(a=aiShader, assign=True)
			
			cmds.select(clear=True)
			color_node = None
			occlusion_node = None
			print '\n\n'
			
			for t in texture_list:
				if t == 'A':
					alpha_file = files_.data['tex_dir'] + texture_list[t] + ".png"
					if os.path.exists(alpha_file):
						createImage(alpha_file, aiShader, 'opacity', 'map_0')
						cmds.select(clear=True)
				if t == 'C':
					color_file = files_.data['tex_dir'] + texture_list[t] + ".png"
					if os.path.exists(color_file) and occlusion_node == None:
						color_node = createImage(color_file, aiShader, 'baseColor', 'map_0')
						cmds.select(clear=True)
				if t == 'N':
					normal_file = files_.data['tex_dir'] + texture_list[t] + ".png"
					if os.path.exists(normal_file):
						ai_N = cmds.shadingNode('aiNormalMap', asShader=True)
						createImage(normal_file, ai_N, 'input', 'map_0')
						cmds.connectAttr(ai_N + '.outValue',aiShader + '.normalCamera', f=1)
						cmds.setAttr(ai_N +'.strength', 0.7)
						cmds.select(clear=True)
				if t == 'O':
					occlusion_file = files_.data['tex_dir'] + texture_list[t] + ".png"
					
					ai_multiply = createShader('aiMultiply', 'outColor', aiShader, 'baseColor')
					ai_colorCorrect = createShader('aiColorCorrect', 'outColor', ai_multiply, 'input2')
					cmds.setAttr(ai_colorCorrect +'.gamma', 1.1)
					
					occlusion_node = createImage(occlusion_file, ai_multiply, 'input1', 'map_1')
					if not color_node:
						color_file = files_.data['tex_dir'] + texture_list['C'] + ".png"
						color_node = createImage(color_file, ai_colorCorrect, 'input', 'map_0')
					
					cmds.connectAttr(color_node + '.' + 'outColor', ai_colorCorrect + '.' + 'input', f=1)
					
					cmds.select(clear=True)