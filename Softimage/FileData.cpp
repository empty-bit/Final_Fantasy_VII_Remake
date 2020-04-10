// https://github.com/Ploaj/ModelThingy/blob/master/BFRES/BFRES/FileData.cs
#include "FileData.h"
#include <stdio.h>
#include <iostream>
#include <array>
#include "fp16.h"
#include <memory>
#include <vector>


typedef unsigned char byte;
using std::unique_ptr;

std::string FileData::byte_order = "little";

FileData::FileData(unique_ptr<byte[]> c)
:p(0)
{
	FileData::b = std::move(c);
}

FileData::~FileData()
{
}

int FileData::eof()
{
	return sizeof(b);
}

unique_ptr<byte[]> FileData::read(const int length)
{
	if (length + p > sizeof(b))
		return 0;
	unique_ptr<byte[]> data(new byte[length]);
	for (int i = 0; i < length; i++, p++)
	{
		data[i] = b[p];
	}
	return data;
}

int FileData::readInt()
{
	int temp_i;
	if (byte_order == "little")
	{
		temp_i = (b[p]) | ((b[p+1]) << 8) | ((b[p+2]) << 16) | ((b[p+3]) << 24); p += 4;
	}
	else
	{
		temp_i = ((b[p]) << 24) | ((b[p + 1]) << 16) | ((b[p + 2]) << 8) | (b[p + 3]); p += 4;
	}
	return temp_i;
}

int FileData::readThree()
{
	int temp_th;
	if (byte_order == "little")
	{
		temp_th = (b[p]) | ((b[p + 1]) << 8) | ((b[p + 2]) << 16); p += 3;
	}
	else
	{
		temp_th = ((b[p]) << 16) | ((b[p + 1]) << 8) | (b[p + 2]); p += 3;
	}
	return temp_th;
}

int FileData::readShort()
{
	int temp_s;
	if (byte_order == "little")
	{
		temp_s = (b[p]) | ((b[p+1]) << 8); p += 2;
	}
	else
	{
		temp_s = ((b[p]) << 8) | (b[p + 1]); p += 2;
	}
	return temp_s;
}

float FileData::read_FP16()
{
	int temp_f;
	if (byte_order == "little")
	{
		temp_f = (b[p]) | ((b[p + 1]) << 8);
		p += 2;
	}
	else
	{
		temp_f = ((b[p]) << 8) | (b[p + 1]);
		p += 2;
	}
	return HALFToFloat((short)temp_f);
}

int FileData::readByte()
{
	int temp_b = (b[p]); p++;
	return temp_b;
}

float FileData::readFloat()
{
	union {float f; uint32_t i;} v;
	if (byte_order == "little")
	{
		v.i = (b[p]) | ((b[p+1]) << 8) | ((b[p+2]) << 16) | ((b[p+3]) << 24); p += 4;
	}
	else
	{
		v.i = ((b[p]) << 24) | ((b[p+1]) << 16) | ((b[p+2]) << 8) | (b[p+3]); p += 4;
	}
	return v.f;
}

int FileData::sign12Bit(int i)
{
	if (((i >> 11) & 0x1) == 1)
	{
		i = ~i;
		i = i & 0xFFF;
		i += 1;
		i *= -1;
	}
	
	return i;
}

int FileData::sign10Bit(int i)
{
	if (((i >> 9) & 0x1) == 1)
	{
		i = ~i;
		i = i & 0x3FF;
		i += 1;
		i *= -1;
	}
	
	return i;
}

void FileData::skip(int i)
{
	p += i;
}
void FileData::seek(int i, int j)
{
	if (j == 1)
	{
		p += i;
	}
	else if (j == 2)
	{
		p -= i;
	}
	else
	{
		p = i;
	}
}

int FileData::pos()
{
	return p;
}

int FileData::size()
{
	return sizeof(b);
}

std::string FileData::readString()
{
	std::string s = "";
	while (b[p] != 0x00)
	{
		s += (char)b[p];
		p++;
	}
	return s;
}

std::string FileData::readString(int size)
{
	std::string s = "";
	for(int i = 0; i < size; i++)
	{
		s += (char)b[p];
		p++;
	}
	return s;
}

std::string FileData::readString2()
{
	std::string s = "";
	while (b[p] != 0x00)
	{
		s += (char)b[p];
		p++;
	}
	p++;
	return s;
}




//00 00 00 00 00 00 00 00 01 00  60 F8 FA BF 00 00 00 00  EE05F642 2DB42542 B76CF742 3CF00343 A98C3943
// X  X  X  X  X  X  X  X  X  X   X  X  X  X  X  X  X  X
// 0  0  0  0  0  0  0  0  1  0   0  0  0  0  0  0  0  0
// 1  1  1  1  1  1  1  1  1  1   0  0  0  0  0  0  0  0
int FileData::getStart()
{
	int goldStars = 0;
	for (int h = 0; h < 16000; ++h)
	{
		int    c_0 = readShort();
		float  c_1 = readFloat();
		float  c_2 = readFloat();
		float  c_3 = readFloat();
		float  c_4 = readFloat();
		float  c_5 = readFloat();
		float  c_6 = readFloat();
		float  c_7 = readFloat();
		int    c_8 = readByte();
		int    c_9 = readByte();
		int   c_10 = readByte();
		int   c_11 = readByte();
		
		if (c_0 == 1)    {goldStars++;}
		if (c_1 > 0.001) {goldStars++;}
		if (c_2 > 0.001) {goldStars++;}
		if (c_3 > 0.001) {goldStars++;}
		if (c_4 > 0.001) {goldStars++;}
		if (c_5 > 0.001) {goldStars++;}
		if (c_6 > 0.001) {goldStars++;}
		if (c_7 > 0.001) {goldStars++;}
		if (c_8  != 0)   {goldStars++;}
		if (c_9  == 0)   {goldStars++;}
		if (c_10 == 0)   {goldStars++;}
		if (c_11 == 0)   {goldStars++;}
		
		if (goldStars > 8)
		{
			p -= 4;
			return p;
		}
		else
		{
			goldStars = 0;
			p -= 33;
		}
	}
	/*
	static const int arr[] = {0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0};
	static const int arr2[] = {0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0};
	//vector<int> theVector (arr, arr + sizeof(arr) / sizeof(arr[0]) );
	//std::vector <int> pattern = { 0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0 };
	//std::vector <int> mask = { 1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0 };
	std::vector <int> pattern(arr, arr + sizeof(arr) / sizeof(arr[0]));
	std::vector <int> mask(arr2, arr2 + sizeof(arr2) / sizeof(arr2[0]));
	int search_size = 16000;
	int c;
	size_t back_ = pattern.size() - 1;
	std::vector<int> check;
	for (unsigned __int32 i = 0; i < pattern.size(); ++i)
	{
		if (mask[i])
		{
			check.emplace_back(pattern[i]);
		}
	}
	
	std::vector<int> temp;
	for (int h = 0; h < search_size; ++h)
	{
		for (unsigned __int32 j = 0; j < pattern.size(); ++j)
		{
			c = readByte();
			if (mask[j])
			{
				temp.emplace_back(c);
			}
		}
		if (temp == check)
		{
			int c0 = readInt();
			int c1 = readInt();
			int c2 = readInt();
			int c3 = readInt();
			int c4 = readInt();
			
			if (c0 && c1 && c2 && c3 && c4 > 1000000000)
			{
				return p;
			}
			else
			{
				p -= 20;
			}
		}
		temp.clear();
		if ( back_ > INT_MAX )
		{
		   throw std::overflow_error("data is larger than INT_MAX");
		}
		int back = static_cast<int>(back_);
		p -= back;
	}
	*/
	return 0;
}

void FileData::align(int i)
{
	while (p % i != 0)
		p++;
}