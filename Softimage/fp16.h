/*
**  This program is free software; you can redistribute it and/or modify it under
**  the terms of the GNU Lesser General Public License, as published by the Free 
**  Software Foundation; either version 2 of the License, or (at your option) any
**  later version.
*/
#ifndef FP16_H
#define FP16_H

#include <stdio.h>
#include <stdint.h>

typedef uint16_t HALF;

float HALFToFloat(HALF);
uint32_t static halfToFloatI(HALF);
HALF floatToHALF(float);
HALF static floatToHalfI(uint32_t);
#endif