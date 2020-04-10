#ifndef UTILS_H
#define UTILS_H

#include <memory>
#include <vector>
#include <string>
#include <stdio.h>
#include <stdint.h>
#include <xsi_ref.h>
#include <xsi_string.h>
#include <xsi_longarray.h>
#include <xsi_doublearray.h>

using std::unique_ptr;
using std::vector;
using std::string;
using XSI::CString;


struct jd
{
	string name;
	int parent;
	jd(const string x, const int y) : name(x), parent(y) {}
};

struct groups
{
	int start;
	int stop;
	int size;
	vector<int> bones;
	XSI::CLongArray range;
	groups(const int a, const int b, const int c, const vector<int> x, const XSI::CLongArray y)
		: start(a), stop(b), size(c), bones(x), range(y){}
};

struct weight_data
{
	XSI::CRef BN;
	XSI::CDoubleArray weights;
	weight_data(const XSI::CRef x, const XSI::CDoubleArray y)
		: BN(x), weights(y) {}
};


long getFileSize(FILE* file);
vector<int> getBones(const int& idx, vector<groups>& container);
unique_ptr<FileData> openFile(XSI::CString filename);
#endif