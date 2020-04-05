#PBR Surface Setup by Ryan Roye
import lwsdk
import os
from tempfile import NamedTemporaryFile

from utils import *




CoordinateList = {
"Color":   "-600 -220",
"Alpha":   "-1280 -740",
"Normal":  "-540 -800",
"Opacity": "-280 -100"
}

UV_count = lwsdk.LWObjectFuncs().numVMaps(lwsdk.LWVMAP_TXUV)
def createMaterial(files, vertexGroups, materials, surf):
	textures = getMaterialTypes(files)
	
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
	
	texture_list = textures[surf]
	
	NodeBuild = []
	NodeBuild.append("{ Surface\n")
	NodeBuild.append("  \"Default\"\n")
	NodeBuild.append("  SmoothingAngle 1.5625\n")
	NodeBuild.append("  CompatibilityVersion 77b\n")
	NodeBuild.append("  { Nodes\n")
	NodeBuild.append("    { Root\n")
	NodeBuild.append("      Location 0 0\n")
	NodeBuild.append("      Zoom 1\n")
	NodeBuild.append("      Disabled 1\n")
	NodeBuild.append("    }\n")
	NodeBuild.append("    Version 1\n")
	NodeBuild.append("    { Nodes\n")
	NodeBuild.append("      Server \"Surface\"\n")
	NodeBuild.append("      { Tag\n")
	NodeBuild.append("        RealName \"Surface\"\n")
	NodeBuild.append("        Name \"Surface\"\n")
	NodeBuild.append("        Coordinates -1890 -561\n")
	NodeBuild.append("        Mode 1\n")
	NodeBuild.append("        Selected 0\n")
	NodeBuild.append("        { Data\n")
	NodeBuild.append("        }\n")
	NodeBuild.append("        Preview \"\"\n")
	NodeBuild.append("      }\n")
	NodeBuild.append("      Server \"Input\"\n")
	NodeBuild.append("      { Tag\n")
	NodeBuild.append("        RealName \"Input\"\n")
	NodeBuild.append("        Name \"Input\"\n")
	NodeBuild.append("        Coordinates 0 -289\n")
	NodeBuild.append("        Mode 0\n")
	NodeBuild.append("        Selected 0\n")
	NodeBuild.append("        { Data\n")
	NodeBuild.append("        }\n")
	NodeBuild.append("        Preview \"Item ID\"\n")
	NodeBuild.append("      }\n")
	
	
	# Add material node
	if 'head' in surf.lower() or 'skin' in surf.lower():
		NodeBuild.append("      Server \"Skin\"\n")
		NodeBuild.append("      { Tag\n")
		NodeBuild.append("        RealName \"Skin\"\n")
		NodeBuild.append("        Name \"Skin (1)\"\n")
		NodeBuild.append("        Coordinates -1260 -480\n")
		'''
		NodeBuild.append("        { Data\n")
		NodeBuild.append("          { Attributes\n")
		NodeBuild.append("            { Metadata\n")
		NodeBuild.append("              Version 1\n")
		NodeBuild.append("              Enumerations 0\n")
		NodeBuild.append("              { AttributeData\n")
		
		#color
		NodeBuild.append("                { Attr\n")
		NodeBuild.append("                  Name \"Epidermis Color\"\n")
		NodeBuild.append("                  Flags 0\n")
		NodeBuild.append("                  Tag \"ENVELOPE\" \"On\"\n")
		NodeBuild.append("                  Tag \"FORMAT\" \"Color\"\n")
		NodeBuild.append("                  Tag \"NodeInputID\" \"\"\n")
		NodeBuild.append("                  { Value\n")
		NodeBuild.append("                    \"vparam3\"\n")
		NodeBuild.append("                    { Value\n")
		NodeBuild.append("                      3\n")
		NodeBuild.append("                      0.9881 0.9098 0.7685\n")
		NodeBuild.append("                    }\n")
		NodeBuild.append("                  }\n")
		NodeBuild.append("                }\n")
		'''
	else:
		NodeBuild.append("      Server \"Principled BSDF\"\n")
		NodeBuild.append("      { Tag\n")
		NodeBuild.append("        RealName \"Principled BSDF\"\n")
		NodeBuild.append("        Name \"Principled BSDF (1)\"\n")
		NodeBuild.append("        Coordinates -894 -393\n")
	
		NodeBuild.append("        { Data\n")
		NodeBuild.append("          { Attributes\n")
		NodeBuild.append("            { Metadata\n")
		NodeBuild.append("              Version 1\n")
		NodeBuild.append("              Enumerations 0\n")
		NodeBuild.append("              { AttributeData\n")
		
		#color
		NodeBuild.append("                { Attr\n")
		NodeBuild.append("                  Name \"Color\"\n")
		NodeBuild.append("                  Flags 0\n")
		NodeBuild.append("                  Tag \"ENVELOPE\" \"On\"\n")
		NodeBuild.append("                  Tag \"FORMAT\" \"Percent\"\n")
		NodeBuild.append("                  Tag \"NodeInputID\" \"\"\n")
		NodeBuild.append("                  { Value\n")
		NodeBuild.append("                    \"vparam3\"\n")
		NodeBuild.append("                    { Value\n")
		NodeBuild.append("                      3\n")
		NodeBuild.append("                      0.5 0.5 0.5\n")
		NodeBuild.append("                    }\n")
		NodeBuild.append("                  }\n")
		NodeBuild.append("                }\n")
		
		#specular
		NodeBuild.append("                { Attr\n")
		NodeBuild.append("                  Name \"Specular\"\n")
		NodeBuild.append("                  Flags 0\n")
		NodeBuild.append("                  Tag \"ENVELOPE\" \"On\"\n")
		NodeBuild.append("                  Tag \"FORMAT\" \"Percent\"\n")
		NodeBuild.append("                  Tag \"NodeInputID\" \"\"\n")
		NodeBuild.append("                  { Value\n")
		NodeBuild.append("                    \"vparam\"\n")
		NodeBuild.append("                    { Value\n")
		NodeBuild.append("                      1\n")
		NodeBuild.append("                      0\n")
		NodeBuild.append("                    }\n")
		NodeBuild.append("                  }\n")
		NodeBuild.append("                }\n")
		
		#roughness
		NodeBuild.append("                { Attr\n")
		NodeBuild.append("                  Name \"Roughness\"\n")
		NodeBuild.append("                  Flags 0\n")
		NodeBuild.append("                  Tag \"ENVELOPE\" \"On\"\n")
		NodeBuild.append("                  Tag \"FORMAT\" \"Percent\"\n")
		NodeBuild.append("                  Tag \"NodeInputID\" \"\"\n")
		NodeBuild.append("                  { Value\n")
		NodeBuild.append("                    \"vparam\"\n")
		NodeBuild.append("                    { Value\n")
		NodeBuild.append("                      1\n")
		NodeBuild.append("                      1\n")
		NodeBuild.append("                    }\n")
		NodeBuild.append("                  }\n")
		NodeBuild.append("                }\n")
	
	#close
	NodeBuild.append("              }\n")
	NodeBuild.append("            }\n")
	NodeBuild.append("          }\n")
	NodeBuild.append("        }\n")
	NodeBuild.append("        Preview \"Material\"\n")
	NodeBuild.append("      }\n")
	
	
	
	
	for t in texture_list:
		loc = (0,0)
		the_file = ""
		UVMap = lwsdk.LWObjectFuncs().vmapName(lwsdk.LWVMAP_TXUV, 0)
		
		if t[-2:] == '_C':
			the_file = files.data['tex_dir'] + "\\" + t + ".png"
			loc = CoordinateList["Color"]
			
			Server = "      Server \"Image\"\n"
			RealName = "        RealName \"Image\"\n"
			Name = "        Name \"Image (1)\"\n"
		
		elif t[-2:] == '_N':
			the_file = files.data['tex_dir'] + "\\"  + t + ".png"
			loc = CoordinateList["Normal"]
			
			Server = "      Server \"NormalMap\"\n"
			RealName = "        RealName \"NormalMap\"\n"
			Name = "        Name \"NormalMap (1)\"\n"
		
		elif t[-2:] == '_A':
			the_file = files.data['tex_dir'] + "\\"  + t + ".png"
			loc = CoordinateList["Alpha"]
			
			Server = "      Server \"Image\"\n"
			RealName = "        RealName \"Image\"\n"
			Name = "        Name \"Image (2)\"\n"
		
		elif t[-2:] == '_O':
			the_file = files.data['tex_dir'] + "\\"  + t + ".png"
			loc = CoordinateList["Opacity"]
			if UV_count > 1:
				UVMap = lwsdk.LWObjectFuncs().vmapName(lwsdk.LWVMAP_TXUV, 1)
			
			Server = "      Server \"Image\"\n"
			RealName = "        RealName \"Image\"\n"
			Name = "        Name \"Image (3)\"\n"
		
		NodeBuild.append(Server)
		NodeBuild.append("      { Tag\n")
		NodeBuild.append(RealName)
		NodeBuild.append(Name)
		NodeBuild.append("        Coordinates " + loc + "\n")
		NodeBuild.append("        { Data\n")
		
		if t[-2:] == '_A':
			NodeBuild.append("          InvertColor 1\n")
		
		NodeBuild.append("          { Image\n")
		
		if os.path.exists(the_file):
			NodeBuild.append("            { Clip\n")
			NodeBuild.append("              { Still\n")
			NodeBuild.append("                \"" + the_file + "\"\n")
			NodeBuild.append("              }\n")
			NodeBuild.append("            }\n")
		
		NodeBuild.append("          }\n")
		NodeBuild.append("          Mapping 5\n")
		NodeBuild.append("          UV \"" + UVMap + "\"\n")
		NodeBuild.append("        }\n")
		NodeBuild.append("      }\n")
	NodeBuild.append("    }\n")
	
	
	
	
	#make them there connections
	NodeBuild.append("    { Connections\n")
	NodeBuild.append("      NodeName \"Surface\"\n")
	NodeBuild.append("      InputName \"Material\"\n")
	if 'head' in surf.lower() or 'skin' in surf.lower():
		NodeBuild.append("      InputNodeName \"Skin (1)\"\n")
	else:
		NodeBuild.append("      InputNodeName \"Principled BSDF (1)\"\n")
	NodeBuild.append("      InputOutputName \"Material\"\n")
	
	
	for t in texture_list:
		if t[-2:] == '_A':
			NodeBuild.append("      NodeName \"Surface\"\n")
			NodeBuild.append("      InputName \"Clip\"\n")
			NodeBuild.append("      InputNodeName \"Image (2)\"\n")
			NodeBuild.append("      InputOutputName \"Color\"\n")
		elif t[-2:] == '_C':
			if 'head' in surf.lower() or 'skin' in surf.lower():
				NodeBuild.append("      NodeName \"Skin (1)\"\n")
				NodeBuild.append("      InputName \"Epidermis Color\"\n")
				NodeBuild.append("      InputNodeName \"Image (1)\"\n")
				NodeBuild.append("      InputOutputName \"Color\"\n")
				
				NodeBuild.append("      NodeName \"Skin (1)\"\n")
				NodeBuild.append("      InputName \"Dermis Color\"\n")
				NodeBuild.append("      InputNodeName \"Image (1)\"\n")
				NodeBuild.append("      InputOutputName \"Color\"\n")
			else:
				NodeBuild.append("      NodeName \"Principled BSDF (1)\"\n")
				NodeBuild.append("      InputName \"Color\"\n")
				NodeBuild.append("      InputNodeName \"Image (1)\"\n")
				NodeBuild.append("      InputOutputName \"Color\"\n")
		elif t[-2:] == '_N':
			if 'head' in surf.lower() or 'skin' in surf.lower():
				NodeBuild.append("      NodeName \"Skin (1)\"\n")
			else:
				NodeBuild.append("      NodeName \"Principled BSDF (1)\"\n")#
			NodeBuild.append("      InputName \"Normal\"\n")
			NodeBuild.append("      InputNodeName \"NormalMap (1)\"\n")
			NodeBuild.append("      InputOutputName \"Normal\"\n")
		elif t[-2:] == '_O':
			NodeBuild.append("      NodeName \"Image (1)\"\n")
			NodeBuild.append("      InputName \"Opacity\"\n")
			NodeBuild.append("      InputNodeName \"Image (3)\"\n")
			NodeBuild.append("      InputOutputName \"Color\"\n")
	
	# End connections segment
	NodeBuild.append("      }\n")
	NodeBuild.append("    }\n")
	NodeBuild.append("}\n")
	
	
	# Complete the node build by putting it together
	NodeBuild = "".join(NodeBuild)
	
	f = NamedTemporaryFile(mode='w+', delete=False)
	f.write(NodeBuild)
	f.close()
	
	lwsdk.command("Surf_LoadText \"" + f.name + "\"")
	os.unlink(f.name) # delete the file

def process_surfaces(files, vertexGroups, materials):
	for k in range(len(vertexGroups)):
		shader = materials[k]['name']
		surface_funcs = lwsdk.LWSurfaceFuncs()
		surface = surface_funcs.first()
		while surface:
			if surface_funcs.name(surface) == shader:
				#print "\r"
				#print surface_funcs.name(surface)
				lwsdk.command('Surf_SetSurf ' + shader)
				createMaterial(files, vertexGroups, materials, shader)
				break
			surface = surface_funcs.next(surface)