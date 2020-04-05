import os
import sys
import struct
import codecs
import subprocess
from subprocess import Popen




"""
halftofloat - author fpmurphy from
http://forums.devshed.com/python-programming-11
/converting-half-precision-floating-point-numbers-from-hexidecimal-to-decimal-576842.html
""" 
def HalfToFloat(h):
	s = int((h >> 15) & 0x00000001) # sign
	e = int((h >> 10) & 0x0000001f) # exponent
	f = int(h & 0x000003ff)   # fraction

	if e == 0:
		if f == 0:
			return int(s << 31)
		else:
			while not (f & 0x00000400):
				f <<= 1
				e -= 1
			e += 1
			f &= ~0x00000400
			#print (s,e,f)
	elif e == 31:
		if f == 0:
			return int((s << 31) | 0x7f800000)
		else:
			return int((s << 31) | 0x7f800000 | (f << 13))

	e = e + (127 -15)
	f = f << 13
	return int((s << 31) | (e << 23) | f)

def converthalf2float(h):
	id = HalfToFloat(h)
	str = struct.pack('I',id)
	return struct.unpack('f', str)[0]

def BH(n, file_h):
	array = [] 
	for id in range(n): 
		array.append(struct.unpack('<H', file_h.read(2))[0])
	return array

def HBf(n, file_h):
	array = [] 
	for id in range(n):
		array.append(converthalf2float(BH(n, file_h)[0]))
	return array


def uassetFilter(container, lst):
	for x in lst:
		p = x.rfind('.')
		if x[p+1:] == 'uasset':
			container.append(x)


def readUasset(file_h):
	byte_order = ''
	LE = (b'c1832a9e')
	BE = (b'9e2a83c1')
	check = readHexString(file_h, 4)
	if LE == check:
		byte_order = 'Zilog_Z80'
	elif BE == check:
		byte_order = 'Motorola_68000'
	else:
		byte_order = 'Itanic' # satire
	
	
	version = struct.unpack("<l",file_h.read(4))[0]
	thing1  = struct.unpack("<L",file_h.read(4))[0]
	serialVersion = struct.unpack("<L",file_h.read(4))[0]
	unk = struct.unpack("<L",file_h.read(4))[0]
	
	headerCount = struct.unpack("<L",file_h.read(4))[0]
	versionList = []
	for v in range(headerCount):
		v0 = readHexString(file_h, 4)
		v1 = readHexString(file_h, 4)
		v2 = readHexString(file_h, 4)
		v3 = readHexString(file_h, 4)
		unk = struct.unpack("<L",file_h.read(4))[0]
		version = (v0, v1, v2, v3)
		versionList.append(version)
	
	uassetFileSize = struct.unpack("<L",file_h.read(4))[0]
	unk = struct.unpack("<L",file_h.read(4))[0]
	packageGroup = struct.unpack("<L",file_h.read(4))[0]
	packageFlags = struct.unpack("<L",file_h.read(4))[0]
	unk = struct.unpack("B",file_h.read(1))[0]
	stringCount = struct.unpack("<L",file_h.read(4))[0]
	stringOffset = struct.unpack("<L",file_h.read(4))[0]
	
	file_h.seek(stringOffset,0)
	names = []
	for y in range(stringCount):
		size = struct.unpack("<L",file_h.read(4))[0]
		size -= 1
		name = struct.unpack("%ss"%size,file_h.read(size))[0].decode('ascii')
		null = struct.unpack("b",file_h.read(1))[0]
		unk = struct.unpack("<L",file_h.read(4))[0]
		
		names.append(name)
	return names


class path_wrangler():
	def __init__(self, path):
		self.path = path
		self.data = {}
	def get_files(self):
		path_name    = os.path.dirname(self.path)
		last_forward = path_name.rfind('\\')
		base_dir     = path_name[:last_forward]
		
		self.data['mat_dir'] = base_dir + '\\Material\\'
		self.data['mdl_dir'] = base_dir + '\\Model\\'
		self.data['tex_dir'] = base_dir + '\\Texture\\'
		
		md = os.listdir(self.data['mat_dir'])
		td = os.listdir(self.data['tex_dir'])
		
		self.data['mat_file_list'] = []
		self.data['tex_file_list'] = []
		uassetFilter(self.data['mat_file_list'], md)
		uassetFilter(self.data['tex_file_list'], td)
		
		sf = path_name.split("\\")
		
		s1 = self.path.split("\\")[-1].split(".")[0] # 'FA0002_00_Body_C'
		s2 = s1.split("_")    # ['FA0002', '00', 'Body', 'C']
		s3 = "_".join(s2[:2]) # 'FA0002_00'
		s4 = s3 + ".uexp"     # 'FA0002_00.uexp'
		s8 = s3 + ".uasset"   # 'FA0002_00.uasset'
		
		# \FA0002_00_Aerithbasket_Standard\Model\FA0002_00.uexp
		self.data['uexp'] = "\\".join(sf[:-1]) + "\\Model\\" + s4
		
		# \FA0002_00_Aerithbasket_Standard\Model\FA0002_00.uasset
		self.data['uasset'] = "\\".join(sf[:-1]) + "\\Model\\" + s8
		
		fullName = sf[-2].split("_")       # 'FA0002_00_Aerithbasket_Standard'
		self.data['meshName']     = "_".join(fullName[-2:]) # 'Aerithbasket_Standard'
		self.data['submesh_name'] = self.data['meshName'] + "_model"


def getMaterialTypes(f_list):
	textureData = {}
	temp = set()
	matFiles = f_list.data['mat_file_list']
	texFiles = f_list.data['tex_file_list']
	for t in texFiles:
		tl = t.rfind('.')
		tname = t[:tl]
		temp.add(tname)
	for m in matFiles:
		textures = set()
		fname = m[:-7]
		fpath = f_list.data['mat_dir'] + m
		fileH = open(fpath, 'rb')
		theNames = readUasset(fileH)
		fileH.close()
		for j in theNames:
			if j in temp:
				if j[-2:] == '_A':
					textures.add(j)
				elif j[-2:] == '_C':
					textures.add(j)
				elif j[-2:] == '_N':
					textures.add(j)
		textureData[fname] = textures
	return textureData


def readHexString(fh, count):
	c = 0
	while c < count:
		aByte = fh.read(1)
		if c == 0:
			s = aByte
		else:
			s += aByte
		c += 1
	return codecs.encode(s, 'hex')

def getGroup(idx, container):
	for d in container:
		if idx in container[d]['range']:
			return container[d]


def run_batch_file(file_path):
	su = Popen(file_path, creationflags=subprocess.CREATE_NEW_CONSOLE, shell = False)
	su.communicate()