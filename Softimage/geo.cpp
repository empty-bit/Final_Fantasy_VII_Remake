#include <xsi_application.h>
#include <xsi_context.h>
#include <xsi_status.h>
#include <xsi_string.h>
#include <xsi_command.h>
#include <xsi_model.h>
#include <xsi_parameter.h>
#include <xsi_x3dobject.h>
#include <xsi_selection.h>
#include <xsi_primitive.h>
#include <xsi_polygonmesh.h>
#include <xsi_geometryaccessor.h>
#include <xsi_floatarray.h>
#include <xsi_doublearray.h>
#include <xsi_customproperty.h>
#include <xsi_meshbuilder.h>
#include <xsi_progressbar.h>
#include <xsi_uitoolkit.h>
#include <xsi_clusterproperty.h>
#include <xsi_clusterpropertybuilder.h>
#include <xsi_comapihandler.h>
#include <xsi_value.h>
#include <xsi_project.h>
#include <xsi_argument.h>
#include <xsi_menu.h>
#include <xsi_null.h>
#include <xsi_longarray.h>
#include <xsi_vector3f.h>
#include <xsi_triangle.h>
#include <xsi_vector3.h>
#include <xsi_kinematics.h>
#include <xsi_kinematicstate.h>
#include <xsi_envelope.h>

#include <string>
#include <iomanip>
#include <chrono>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <vector>
#include <map>
#include <iostream>
#include <iterator>
#include <numeric>
#include <algorithm>
#include "FileData.h"
#include <memory>
#include "utils.h"
#include "moms_typedefs.h"


using std::vector;
using std::string;
using std::unique_ptr;
using namespace XSI::MATH;




class Vector3_I
{
public:
	int x, y, z;

public:
	Vector3_I(int _x, int _y, int _z)
	: x(_x), y(_y), z(_z)
	{
	
	}
};

struct find_bone
{
	XSI::CRef id;
	find_bone(XSI::CRef id) : id(id) {}
	bool operator () ( const weight_data& m ) const
	{
		return m.BN == id;
	}
};

using namespace std::chrono;
XSI::CStatus importGeo(XSI::CString uexp, XSI::CString uasset)
{
	auto t1 = high_resolution_clock::now();

	unique_ptr<FileData> md = openFile(uexp);
	unique_ptr<FileData> ua = openFile(uasset);
	md->byte_order = "little";
	ua->byte_order = "little";
	
	
	XSI::Application app;
	XSI::Model root = app.GetActiveSceneRoot();
	
	XSI::X3DObject xobj;
	XSI::CMeshBuilder meshBuilder;
	root.AddPolygonMesh(L"theMesh", xobj, meshBuilder);
	
	
	

	int check = ua->readInt();
	int version = ua->readInt();
	int thing1  = ua->readInt();
	int serialVersion = ua->readInt();
	int unk = ua->readInt();
	
	int headerCount = ua->readInt();
	for (int v = 0; v < headerCount; v++)
	{
		int v0 = ua->readInt();
		int v1 = ua->readInt();
		int v2 = ua->readInt();
		int v3 = ua->readInt();
		int unk = ua->readInt();
	}
	
	int uassetFileSize = ua->readInt();
	int unk0 = ua->readInt();
	int packageGroup = ua->readInt();
	int packageFlags = ua->readInt();
	int unk1 = ua->readByte();
	const int stringCount = ua->readInt();
	int stringOffset = ua->readInt();
	
	ua->seek(stringOffset,0);
	vector<string> names;
	names.reserve(stringCount);
	for (int y = 0; y < stringCount; y++)
	{
		int size = ua->readInt();
		size -= 1;
		string name = ua->readString(size);
		int null = ua->readByte();
		int unk = ua->readInt();
		names.push_back(name);
	}
	ua.reset();
	
	
	
	int start = md->getStart();
	assert(start != 0);
	//std::cout << "\nstart: " << start << "\n\n" << std::endl;
	
	md->seek(start,0);
	int materialCount = md->readInt();
	
	//md->seek(materialCount * 36,1);
	vector<string> materials;
	materials.reserve(materialCount);
	for (int j = 0; j < materialCount; j++)
	{
		int32_t val0 = md->readInt();
		
		int stringIndex = md->readInt();
		int zero0 = md->readInt();
		int one   = md->readInt();
		int zero1 = md->readInt();
		
		float f0 = md->readFloat();
		float f1 = md->readFloat();
		float f2 = md->readFloat();
		
		int zero2 = md->readInt();
		materials.push_back(names[stringIndex]);
	}
	
	
	vector<jd> joint_data;
	int boneCount = md->readInt();
	joint_data.reserve(boneCount);
	for (int j = 0; j < boneCount; j++)
	{
		int string_index = md->readInt();
		int unk = md->readInt();
		int parent = md->readInt();
		string jointName = names[string_index];
		joint_data.emplace_back(jointName, parent);
	}
	
	
	
	
	

	XSI::CValue retVal;
	XSI::CValueArray args(2);

	//si.SetValue("preferences.General.undo", 0, "")
	args[0] = XSI::CValue(L"preferences.General.undo");
	args[1] = 0;
	app.ExecuteCommand( L"SetValue", args, retVal );

	//si.SetValue("preferences.scripting.cmdlog", False, "")
	args[0] = XSI::CValue(L"preferences.scripting.cmdlog");
	args[1] = XSI::CValue(L"False");
	app.ExecuteCommand( L"SetValue", args, retVal );
	
	int boneCount2 = md->readInt();
	XSI::CRefArray deformers(boneCount2);
	for (int k = 0; k < boneCount2; k++)
	{
		const double qx = md->readFloat();
		const double qy = md->readFloat();
		const double qz = md->readFloat();
		const double qw = md->readFloat();
		const double px = md->readFloat();
		const double py = md->readFloat();
		const double pz = md->readFloat();
		const double sx = md->readFloat();
		const double sy = md->readFloat();
		const double sz = md->readFloat();
		
		
		CQuaternion q(qw, qy, qz, qx);
		CTransformation Trans;
		CRotation r;
		
		CMatrix4 Mat4(  1.0, 0.0, 0.0, 0.0,
						0.0, 1.0, 0.0, 0.0,
						0.0, 0.0, 1.0, 0.0,
						 py,  pz,  px, 1.0);
		
		
		string boneName = joint_data[k].name;
		int BNparent = joint_data[k].parent;
		
		XSI::Null mrJoint;
		root.AddNull(boneName.c_str(), mrJoint);
		XSI::Parameter n_size = mrJoint.GetParameter("size");
		n_size.PutValue(1.1);
		//XSI::Parameter n_icon = mrJoint.GetParameter("primary_icon");
		//n_icon.PutValue(8); //pyramid
		
		
		r.SetFromQuaternion(q);
		Trans.SetMatrix4(Mat4);
		Trans.SetRotation(r);

		if (BNparent != -1)
		{
			string parentName = joint_data[BNparent].name;
			args[0] = XSI::CValue(parentName.c_str());
			args[1] = XSI::CValue(boneName.c_str());
			app.ExecuteCommand( L"ParentObj", args, retVal );
		}
		XSI::KinematicState kin(mrJoint.GetKinematics().GetLocal());
		kin.PutTransform(Trans);
		deformers[k] = mrJoint;
	}
	//
	args[0] = XSI::CValue(L"Camera");
	args[1] = XSI::CValue(L"shaded");
	app.ExecuteCommand( L"SetDisplayMode", args, retVal );
	
	//Application.SetValue("Camera.camdisp.headlight", True, "")
	args[0] = XSI::CValue(L"Camera.camdisp.headlight");
	args[1] = XSI::CValue(L"True");
	app.ExecuteCommand( L"SetValue", args, retVal );

	//Application.SetValue("Camera.camdisp.xrayshaded", True, "")
	args[0] = XSI::CValue(L"Camera.camdisp.xrayshaded");
	app.ExecuteCommand( L"SetValue", args, retVal );
	
	
	
	
	int boneCount3 = md->readInt();
	md->seek(boneCount3 * 12, 1);
	
	
	vector<groups> vertexGroups;
	
	int unk10 = md->readInt();
	int unk11 = md->readByte();
	int unk12 = md->readByte();
	int groupCount = md->readInt();
	for (int m = 0; m < groupCount; m++)
	{
		int z1 = md->readShort();
		int ID = md->readShort();
		
		md->seek(24,1);
		
		# pragma region bone group
		start = md->readInt();
		const int count = md->readInt();
		vector<int> bones;
		bones.reserve(count);
		for (int bn = 0; bn < count; bn++)
		{
			int bid = md->readShort();
			bones.push_back(bid);
		}
		# pragma endregion bone group
		
		int size = md->readInt();
		int stop = start + size;
		XSI::CLongArray range(size);
		int ct = 0;
		for (int r = start; r < stop; ++r)
		{
			range[ct] = r;
			++ct;
		}
		
		vertexGroups.emplace_back(start, stop, size, bones, range);
		
		md->seek(34,1);
		int FFx4 = md->readInt();
		int flag = md->readInt();
		if (flag) // extra data for this group
		{
			int count = md->readInt();
			md->seek(count * 16, 1);
		}
		else
		{
			int null = md->readInt();
		}
	}
	
	
	
	
	int unkByte = md->readByte();
	int stride = md->readInt();
	int fCount = md->readInt();
	
	vector<long> pCounts;
	pCounts.reserve(fCount);
	int faceCount2 = fCount * 3;
	vector<long> faces;
	faces.reserve(faceCount2);
	
	
	vector<Vector3_I> faces_test;
	for (int f=0; f<fCount; f++) {pCounts.push_back(3);}
	if (stride == 4)
	{
		for (int x = 0; x < fCount/3; x++)
		{
			int f0 = md->readInt();
			int f1 = md->readInt();
			int f2 = md->readInt();
			faces.push_back(f0);
			faces.push_back(f2);
			faces.push_back(f1);
			Vector3_I test(f0, f2, f1);
			faces_test.push_back(test);
		}
	}
	else if (stride == 2)
	{
		for (int x = 0; x < fCount/3; x++)
		{
			int f0 = md->readShort();
			int f1 = md->readShort();
			int f2 = md->readShort();
			faces.push_back(f0);
			faces.push_back(f1);
			faces.push_back(f2);
			
		}
	}
	
	
	
	int unkCount = md->readInt();
	md->seek(unkCount * 2, 1);

	int unk25 = md->readInt();
	int vertexCount = md->readInt();
	int boneCount4 = md->readInt();
	md->seek(boneCount4 * 2, 1);

	int null0 = md->readInt();
	int null1 = md->readInt();
	
	int uv_count  = md->readInt();
	int unk3      = md->readShort();
	int uv_count2 = md->readInt();
	
	int null2 = md->readInt();
	
	float unk4  = md->readFloat();
	float unk5  = md->readFloat();
	float unk6  = md->readFloat();
	
	int null3 = md->readInt();
	int null4 = md->readInt();
	int null5 = md->readInt();
	
	int vStride = md->readInt();
	int vCount  = md->readInt();
	
	int vertexCount2 = vCount * 3;
	
	int uvCount = vCount * 3;
	
	vector<float> UVs0;
	vector<float> UVs1;
	vector<float> UVs2;
	vector<float> UVs3;
	vector<float> UVs4;
	vector<float> UVs5;
	vector<CVector3f> UVs9;

	vector<double> points;
	points.reserve(vertexCount2);
	vector<float> n_array;
	n_array.reserve(vertexCount2);
	
	for (int v = 0; v < vCount; v++)
	{
		float nt0 = md->readByte() /255.0f;
		float nt1 = md->readByte() /255.0f;
		float nt2 = md->readByte() /255.0f;
		float nt3 = md->readByte() /255.0f;

		float nt4 = md->readByte() /255.0f;
		float nt5 = md->readByte() /255.0f;
		float nt6 = md->readByte() /255.0f;
		float nt7 = md->readByte() /255.0f;
		
		
		float px = md->readFloat();
		float py = md->readFloat();
		float pz = md->readFloat();
		points.push_back(py);
		points.push_back(pz);
		points.push_back(px);
		
		if (uv_count > 0)
		{
			float u0 = md->read_FP16();
			float v0 = md->read_FP16() * -1.0f + 1.0f;
			UVs0.push_back(u0);
			UVs0.push_back(v0);
			UVs0.push_back(0.0);
			CVector3f test(u0, v0, 0.0);
			UVs9.push_back(test);
		}
		if (uv_count > 1)
		{
			float u1 = md->read_FP16();
			float v1 = md->read_FP16() * -1.0f + 1.0f;
			UVs1.push_back(u1);
			UVs1.push_back(v1);
			UVs1.push_back(0.0);
		}
		if (uv_count > 2)
		{
			float u2 = md->read_FP16();
			float v2 = md->read_FP16() * -1.0f + 1.0f;
			UVs2.push_back(u2);
			UVs2.push_back(v2);
			UVs2.push_back(0.0);
		}
		if (uv_count > 3)
		{
			float u3 = md->read_FP16();
			float v3 = md->read_FP16() * -1.0f + 1.0f;
			UVs3.push_back(u3);
			UVs3.push_back(v3);
			UVs3.push_back(0.0);
		}
		if (uv_count > 4)
		{
			float u4 = md->read_FP16();
			float v4 = md->read_FP16() * -1.0f + 1.0f;
			UVs4.push_back(u4);
			UVs4.push_back(v4);
			UVs4.push_back(0.0);
		}
	}
	
	XSI::CStatus check0 = meshBuilder.AddVertices(vCount, &points[0]);
	app.LogMessage(L"AddVertices: " + check0.GetDescription());
	
	XSI::CStatus check2 = meshBuilder.AddTriangles(fCount, &faces[0]);
	app.LogMessage(L"AddPolygons: " + check2.GetDescription());
	
	
	// Generate the new mesh with undo disabled
	XSI::CMeshBuilder::CErrorDescriptor err = meshBuilder.Build(false);
	if (err.GetCode() == XSI::CStatus::Fail)
	{
		app.LogMessage(L"Error generating the mesh: " + err.GetDescription());
	}
	
	XSI::PolygonMesh mesh = xobj.GetActivePrimitive().GetGeometry();
	XSI::CClusterPropertyBuilder cpBuilder = mesh.GetClusterPropertyBuilder();
	
	
	vector<float> UV_Test;
	UV_Test.reserve(faceCount2);
	for (int t = 0; t < faces.size(); ++t)
	{
		int vertex_id = faces[t];
		float u = UVs9[vertex_id].GetX();
		float v = UVs9[vertex_id].GetY();
		UV_Test.push_back(u);
		UV_Test.push_back(v);
		UV_Test.push_back(0.0);
	}
	
	size_t size_temp = UV_Test.size();
	if ( UV_Test.size() > INT_MAX )
	{
		throw std::overflow_error("UV data is larger than INT_MAX");
	}
	
	int UV_TestSize = static_cast<int>(size_temp) / 3;
	if (uv_count > 0)
	{
		XSI::ClusterProperty uvs_0 = cpBuilder.AddUV();
		uvs_0.SetValues(&UV_Test[0], UV_TestSize);
	}
	


	/*
	if (uv_count > 0)
	{
		XSI::ClusterProperty uvs_0 = cpBuilder.AddUV();
		uvs_0.SetValues(&UVs0[0], vCount);
	}
	if (uv_count > 1)
	{
		XSI::ClusterProperty uvs_1 = cpBuilder.AddUV();
		uvs_1.SetValues(&UVs1[0], vCount);
	}
	if (uv_count > 2)
	{
		XSI::ClusterProperty uvs_2 = cpBuilder.AddUV();
		uvs_2.SetValues(&UVs2[0], vCount);
	}
	if (uv_count > 3)
	{
		XSI::ClusterProperty uvs_3 = cpBuilder.AddUV();
		uvs_3.SetValues(&UVs3[0], vCount);
	}
	if (uv_count > 4)
	{
		XSI::ClusterProperty uvs_4 = cpBuilder.AddUV();
		uvs_4.SetValues(&UVs4[0], vCount);
	}
	*/


	//XSI::ClusterProperty normals = cpBuilder.AddUserNormal();
	//XSI::CStatus check1 = normals.SetValues(n_array.get(), vCount);
	//app.LogMessage(L"normals.SetValues: " + check1.GetDescription());
	
	//std::cout << "Length of normals array = " << (sizeof(n_array)/sizeof(*n_array)) << std::endl;
	//std::ptrdiff_t d = std::distance(std::begin(n_array), std::end(n_array));
	//std::cout << "Length of normals array = " << d << std::endl;
	//std::cout << "ClusterProperty size: " << normals.GetValueSize() << std::endl;
	



	// material clusters
	
	int c2 = 0;
	for (auto g: vertexGroups)
	{
		int p_start  = g.start;
		int p_stop  = g.stop;
		int p_size  = g.size;
		XSI::CLongArray p_range;
		XSI::CTriangleRefArray triarray = mesh.GetTriangles();
		int cb = 0;
		for (int v = 0; v < triarray.GetCount(); ++v)
		{
			Vector3_I pf = faces_test[v];
			XSI::Triangle tri = triarray.GetItem(v);
			long this_tri = tri.GetPolygonIndex();
			if (pf.x >= p_start && pf.x < p_stop && pf.y >= p_start && pf.y < p_stop && pf.z >= p_start && pf.z < p_stop)
			{
				p_range.Add(this_tri);
				++cb;
			}
		}
		XSI::CString p0(c2);
		XSI::CString p1 = "mat_" + p0;
		XSI::Cluster myCls;
		mesh.AddCluster(XSI::siPolygonCluster, p1, p_range, myCls);
		++c2;
	}
	
	
	
	
	int unkS = md->readShort();
	int extraBoneWeights = md->readInt();
	int wCount  = md->readInt();
	int strideW  = md->readInt();
	int wCount2 = md->readInt();
	
	int subRange = strideW / 2;
	
	
	
	
	XSI::Envelope newEnvelope;
	
	LONG wCount_all = wCount * boneCount2;
	xobj.ApplyEnvelope(deformers, XSI::siUnspecified, XSI::siUnspecified, newEnvelope);
	
	
	double** wd3;
	double* temp;

	wd3 = (double**)malloc(boneCount2 * sizeof(*wd3));
	temp = (double*)malloc(boneCount2 * wCount * sizeof(wd3[0]));
	for (int i = 0; i < boneCount2; i++)
	{
	  wd3[i] = temp + (i * wCount);
	}
	

	
	for (int g = 0; g < vertexGroups.size(); ++g)
	{
		groups current_group = vertexGroups[g];
		vector<int> bones = current_group.bones;
		for (int h = current_group.start; h < current_group.stop; ++h)
		{
			if (strideW == 16)
			{
				int b_0 = md->readByte();
				int b_1 = md->readByte();
				int b_2 = md->readByte();
				int b_3 = md->readByte();
				int b_4 = md->readByte();
				int b_5 = md->readByte();
				int b_6 = md->readByte();
				int b_7 = md->readByte();

				int b_id_0 = bones[b_0];
				int b_id_1 = bones[b_1];
				int b_id_2 = bones[b_2];
				int b_id_3 = bones[b_3];
				int b_id_4 = bones[b_4];
				int b_id_5 = bones[b_5];
				int b_id_6 = bones[b_6];
				int b_id_7 = bones[b_7];


				float weight_0 = md->readByte() /2.55f;
				float weight_1 = md->readByte() /2.55f;
				float weight_2 = md->readByte() /2.55f;
				float weight_3 = md->readByte() /2.55f;
				float weight_4 = md->readByte() /2.55f;
				float weight_5 = md->readByte() /2.55f;
				float weight_6 = md->readByte() /2.55f;
				float weight_7 = md->readByte() /2.55f;
				
				wd3[b_id_0][h] = weight_0;
				wd3[b_id_1][h] = weight_1;
				wd3[b_id_2][h] = weight_2;
				wd3[b_id_3][h] = weight_3;
				wd3[b_id_4][h] = weight_4;
				wd3[b_id_5][h] = weight_5;
				wd3[b_id_6][h] = weight_6;
				wd3[b_id_7][h] = weight_7;
			}
			else if (strideW == 8)
			{
				int b_0 = md->readByte();
				int b_1 = md->readByte();
				int b_2 = md->readByte();
				int b_3 = md->readByte();

				int b_id_0 = bones[b_0];
				int b_id_1 = bones[b_1];
				int b_id_2 = bones[b_2];
				int b_id_3 = bones[b_3];


				float weight_0 = md->readByte() /2.55f;
				float weight_1 = md->readByte() /2.55f;
				float weight_2 = md->readByte() /2.55f;
				float weight_3 = md->readByte() /2.55f;
				
				wd3[b_id_0][h] = weight_0;
				wd3[b_id_1][h] = weight_1;
				wd3[b_id_2][h] = weight_2;
				wd3[b_id_3][h] = weight_3;
			}
			else if (strideW == 4)
			{
				int b_0 = md->readByte();
				int b_1 = md->readByte();

				int b_id_0 = bones[b_0];
				int b_id_1 = bones[b_1];


				float weight_0 = md->readByte() /2.55f;
				float weight_1 = md->readByte() /2.55f;
				
				wd3[b_id_0][h] = weight_0;
				wd3[b_id_1][h] = weight_1;
			}
		}
	}
	

	/*
	for (int b = 0; b < deformers.GetCount(); ++b)
	{
		XSI::X3DObject siobj(deformers[b]);
		XSI::CDoubleArray t;
		t.Attach(wd3[b], wCount);
		newEnvelope.SetDeformerWeights2(siobj, t);
	}
	*/
	free(temp);
	free(wd3);



	
	auto t2 = std::chrono::high_resolution_clock::now();
	duration<double> time_span = duration_cast<duration<double>>(t2 - t1);
	std::cout << "Time: " << time_span.count() << " seconds." << std::endl;
	
	return XSI::CStatus::OK;
}