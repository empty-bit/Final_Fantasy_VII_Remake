// Ploaj was here
#ifndef FILEDATA_H
#define FILEDATA_H

#include <string>
#include <iostream>
#include <memory>
#include <vector>


typedef unsigned char byte;
using std::unique_ptr;


class FileData
{
	int p;
	public:
		unique_ptr<byte[]> b;
		~FileData();
		static std::string byte_order;
		FileData(unique_ptr<byte[]> b);
		int eof();
		unique_ptr<byte[]> read(const int length);
		int readInt();
		int readThree();
		int readShort();
		float read_FP16();
		int readByte();
		float readFloat();
		static int sign12Bit(int i);
		static int sign10Bit(int i);
		void skip(int i);
		void seek(int i, int j);
		int pos();
		int size();
		std::string readString();
		std::string readString(int size);
		std::string readString2();
		int getStart();
		void align(int i);
};
#endif