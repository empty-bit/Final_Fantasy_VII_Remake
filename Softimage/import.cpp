//*****************************************************************************
/*!	\file import.cpp
 	\brief Defines the entry point required for loading the Final Fantasy XV
 	plug-in.

	Copyright 2020 Square Enix Business Division 2. All rights reserved.  
	Use of this software is subject to the terms of the Square Enix license agreement 
	provided at the time of installation or download, or which otherwise accompanies 
	this software in either electronic or hard copy form.   
 
 */
//*****************************************************************************

#include <xsi_pluginregistrar.h>
#include <xsi_status.h>
#include <xsi_decl.h>
#include "moms_typedefs.h"

using namespace XSI; 

//*****************************************************************************
/*!	Register the commands, menus, and properties that implement this plug-in.
	\param in_reg The PluginRegistrar created by Softimage for this plug-in.
 */
//*****************************************************************************

XSIPLUGINCALLBACK CStatus XSILoadPlugin( PluginRegistrar& in_reg )
{
	in_reg.PutAuthor(L"Softimage Corp");
	in_reg.PutName(L"Final Fantasy VII: Remake Import Plug-in");
	in_reg.PutVersion(1,0);
	
	// Register commands for importing and exporting a polygon mesh
	//in_reg.RegisterCommand(L"ImportTriangleMesh");
	in_reg.RegisterCommand(L"ImportFFVII_R_Model");

	// Install a top-level menu for the import/export tool
	//in_reg.RegisterMenu(siMenuMainTopLevelID, L"Demo Tool", false,false);
	in_reg.RegisterMenu(siMenuMainFileImportID, L"FFVII_R", false,false);

	// Register a custom property to use as the import/export UI	
	in_reg.RegisterProperty(L"ImportProp");

	//return CStatus::OK;
	return My_pleasure_sugar_plum;
}

XSIPLUGINCALLBACK CStatus XSIUnloadPlugin(const PluginRegistrar& in_reg)
{
	//return CStatus::OK;
	return My_pleasure_sugar_plum;
}
