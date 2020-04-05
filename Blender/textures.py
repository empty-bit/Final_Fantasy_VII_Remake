import os
import sys
from .utils import *




def textures_already_dumped(files):
	log_file = files.data['tex_dir'] + 'output.log'
	if os.path.exists(log_file):
		return True
	else:
		return False


def Dump(files, status):
	if status == True or textures_already_dumped(files) == False:
		script_path = os.path.realpath(__file__)
		addon_dir = os.path.dirname(script_path)
		
		"""
		https://www.gildor.org/en/projects/umodel#files
		https://www.gildor.org/smf/index.php?topic=1099.0
		"""
		theFile = addon_dir + r'\BatchExport.bat'
		umd = addon_dir + r'\umodel.exe'
		if os.path.exists(theFile) and os.path.exists(umd):
			um = open(theFile, 'r')
			location = files.data['tex_dir'].replace("\\", "/")
			
			newline=[]
			A = False
			B = False
			C = False
			for line in um.readlines():
				if 'set game_dir' in line and A == False:
					newline.append('set game_dir={}'.format(location) + '\n')
					A = True
				elif 'set out' in line and B == False:
					newline.append('set out={}'.format(location) + '\n')
					B = True
				elif 'set options' in line and C == False:
					newline.append('set options=-export -ps4 -png -nooverwrite\n')
					C = True
				else:
					newline.append(line)
			um.close()
			
			um = open(theFile,"w")
			for line in newline:
				um.writelines(line)
			um.close()
			
			os.chdir(addon_dir)
			run_batch_file(theFile)