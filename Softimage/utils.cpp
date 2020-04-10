#include <stdio.h>
#include <stdint.h>
#include <memory>
#include <vector>
#include <string>
#include <xsi_string.h>
#include "FileData.h"
#include "utils.h"

using std::unique_ptr;
using std::vector;
using std::string;




long getFileSize(FILE* file)
{

	long lCurPos, lEndPos;
	lCurPos = ftell(file);
	fseek(file, 0, 2);
	lEndPos = ftell(file);
	fseek(file, lCurPos, 0);
	return lEndPos;
}


vector<int> getBones(const int& idx, vector<groups>& container)
{
	vector<int> temp;
	for(auto d: container)
	{
		int start = d.start;
		int stop = d.stop;
		if (idx >= d.start && idx < d.stop)
		{
			return d.bones;
		}
	}
	return temp;
}


unique_ptr<FileData> openFile(XSI::CString filename)
{
	FILE* fh;
	errno_t my_dumb_error_code = fopen_s(&fh, filename.GetAsciiString(), "rb");
	long fileSize = getFileSize(fh);
	unique_ptr<byte[]> fileBuf(new byte[fileSize]);
	if (!my_dumb_error_code && fh != NULL)
	{
		fread(fileBuf.get(), fileSize, 1, fh);
		fclose(fh);
	}
	unique_ptr<FileData> fuzz(new FileData(std::move(fileBuf)));
	return fuzz;
}