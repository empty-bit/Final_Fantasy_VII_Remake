# -*- coding: utf-8 -*-
from arnold import *
from mtoa.core import createOptions
createOptions()

import maya.cmds as cmds
import read
reload(read)

fname = cmds.fileDialog2(fm=1, ff='FFVII: Remake .uexp (*.uexp);;')[0]
time = read.readFile(fname)
print "\n\n" + 'Import Time: ' + str(time) + ' seconds' + "\n\n"

cmds.setAttr("defaultArnoldRenderOptions.renderDevice", 1)
cmds.setAttr("defaultArnoldRenderOptions.AASamples", 10)
cmds.setAttr("defaultArnoldRenderOptions.GIDiffuseDepth", 2)
cmds.setAttr("defaultArnoldRenderOptions.GITotalDepth", 16)
cmds.setAttr("defaultArnoldRenderOptions.autoTransparencyDepth", 32)