//*****************************************************************************
/*!	\file importmesh_command.cpp
	\brief Implementation of the DemoImportMesh command, which imports 
	mesh geometry into Softimage.

	Copyright 2008 Autodesk, Inc.  All rights reserved.  
	Use of this software is subject to the terms of the Autodesk license agreement 
	provided at the time of installation or download, or which otherwise accompanies 
	this software in either electronic or hard copy form.   

*/
//*****************************************************************************

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
#include <xsi_ppglayout.h>
#include <xsi_meshbuilder.h>
#include <xsi_progressbar.h>
#include <xsi_uitoolkit.h>
#include <xsi_clusterpropertybuilder.h>
#include <xsi_comapihandler.h>
#include <xsi_value.h>
#include <xsi_project.h>
#include <xsi_argument.h>
#include <xsi_menu.h>

#include <string>
#include <iostream>
#include "FileData.h"
#include <memory>
#include "utils.h"
#include "moms_typedefs.h"

extern XSI::CStatus importGeo(XSI::CString md, XSI::CString ua);

using std::unique_ptr;
using std::string;
typedef unsigned char byte;




XSI::CStatus ImportMesh(XSI::CString uexp, XSI::CString uasset)
{
	importGeo(uexp, uasset);
	return XSI::CStatus::OK;
}

XSIPLUGINCALLBACK XSI::CStatus Show_FileBrowser(XSI::CRef& in_ctxt)
{
	XSI::Application app;
	
	XSI::Context ctxt(in_ctxt);
	XSI::Command cmd = ctxt.GetSource();
	XSI::ArgumentArray args = cmd.GetArguments();
	XSI::CRefArray selectedObjects = (XSI::CRefArray)args.GetItem(0).GetValue();
	XSI::CString strFolderAndFileName(args.GetItem(1).GetValue());
	
	
	XSI::CComAPIHandler toolkit;
	toolkit.CreateInstance(L"XSI.UIToolkit");
	XSI::CComAPIHandler filebrowser(toolkit.GetProperty(L"FileBrowser"));
	filebrowser.PutProperty(L"InitialDirectory", XSI::Application().GetActiveProject().GetPath());
	filebrowser.PutProperty(L"Filter", L"FFVII: Remake .uexp files(*.uexp)|*.uexp||");
	XSI::CValue returnVal;
	filebrowser.Call(L"ShowOpen", returnVal);
	XSI::CString filename = filebrowser.GetProperty(L"FilePathName").GetAsText();
	
	XSI::CString s0 = ".uasset";
	int sL = filename.FindString( XSI::CString(".") );
	XSI::CString filename_2 = filename.GetSubString(0, sL);
	filename_2 += s0;
	app.LogMessage(L"substr: " + filename_2);
	
	return ImportMesh(filename, filename_2);
}

XSIPLUGINCALLBACK XSI::CStatus FFVII_R_Init(XSI::CRef& in_ctxt)
{
	XSI::Context ctxt(in_ctxt);
	
	XSI::Menu oMenu;
	XSI::CStatus st;
	
	oMenu = ctxt.GetSource();
	
	XSI::MenuItem oNewItem;
	st = oMenu.AddCallbackItem(L"Import FFVII: Remake .uexp", L"Show_FileBrowser", oNewItem);
	if (st != XSI::CStatus::OK) return st;
	
	return XSI::CStatus::OK;
}