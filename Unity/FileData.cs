using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
// Ploaj was here
// https://github.com/Ploaj/ModelThingy/blob/master/BFRES/BFRES/FileData.cs


namespace FF7R
{
	public class FileData
	{
		public byte[] b;
		private int p = 0;
		public Endianness Endian = Endianness.Little;
		public string fname = "";
		public string Magic = "";

		public FileData(String f)
		{
			b = File.ReadAllBytes(f);
			fname = Path.GetFileName(f);
			readMagic();
		}

		public FileData(byte[] b)
		{
			this.b = b;
			readMagic();
		}

		public FileData(byte[] b, string f)
		{
			this.b = b;
			fname = f;
			readMagic();
		}

		public void readMagic()
		{
			Magic = readString(0, 4);
		}

		public int eof()
		{
			return b.Length;
		}

		public byte[] read(int length)
		{
			if (length + p > b.Length)
				throw new IndexOutOfRangeException();

			var data = new byte[length];
			for (int i = 0; i < length; i++, p++)
			{
				data[i] = b[p];
			}
			return data;
		}
		public int readInt()
		{
			if (Endian == Endianness.Little)
			{
				return (b[p++] & 0xFF) | ((b[p++] & 0xFF) << 8) | ((b[p++] & 0xFF) << 16) | ((b[p++] & 0xFF) << 24);
			}
			else
				return ((b[p++] & 0xFF) << 24) | ((b[p++] & 0xFF) << 16) | ((b[p++] & 0xFF) << 8) | (b[p++] & 0xFF);
		}
		public int readThree()
		{
			if (Endian == Endianness.Little)
			{
				return (b[p++] & 0xFF) | ((b[p++] & 0xFF) << 8) | ((b[p++] & 0xFF) << 16);
			}
			else
				return ((b[p++] & 0xFF) << 16) | ((b[p++] & 0xFF) << 8) | (b[p++] & 0xFF);
		}

		public int readShort()
		{
			if (Endian == Endianness.Little)
			{
				return (b[p++] & 0xFF) | ((b[p++] & 0xFF) << 8);
			}
			else
				return ((b[p++] & 0xFF) << 8) | (b[p++] & 0xFF);
		}

		public int readByte()
		{
			return (b[p++] & 0xFF);
		}

		public float readFloat()
		{
			byte[] by = new byte[4];
			if (Endian == Endianness.Little)
				by = new byte[4] { b[p], b[p + 1], b[p + 2], b[p + 3] };
			else
				by = new byte[4] { b[p + 3], b[p + 2], b[p + 1], b[p] };
			p += 4;
			return BitConverter.ToSingle(by, 0);
		}

		public float readHalfFloat()
		{
			return toFloat((short)readShort());
		}

		public static float toFloat(int hbits)
		{
			int mant = hbits & 0x03ff;			// 10 bits mantissa
			int exp = hbits & 0x7c00;			// 5 bits exponent
			if (exp == 0x7c00)				   // NaN/Inf
				exp = 0x3fc00;					// -> NaN/Inf
			else if (exp != 0)				   // normalized value
			{
				exp += 0x1c000;				   // exp - 15 + 127
				if (mant == 0 && exp > 0x1c400)  // smooth transition
					return BitConverter.ToSingle(BitConverter.GetBytes((hbits & 0x8000) << 16
						| exp << 13 | 0x3ff), 0);
			}
			else if (mant != 0)				  // && exp==0 -> subnormal
			{
				exp = 0x1c400;					// make it normal
				do
				{
					mant <<= 1;				   // mantissa * 2
					exp -= 0x400;				 // decrease exp by 1
				} while ((mant & 0x400) == 0); // while not normal
				mant &= 0x3ff;					// discard subnormal bit
			}									 // else +/-0 -> +/-0
			return BitConverter.ToSingle(BitConverter.GetBytes(		  // combine all parts
				(hbits & 0x8000) << 16		  // sign  << ( 31 - 15 )
				| (exp | mant) << 13), 0);		 // value << ( 23 - 10 )
		}

		public static int sign12Bit(int i)
		{
			//		System.out.println(Integer.toBinaryString(i));
			if (((i >> 11) & 0x1) == 1)
			{
				//			System.out.println(i);
				i = ~i;
				i = i & 0xFFF;
				//			System.out.println(Integer.toBinaryString(i));
				//			System.out.println(i);
				i += 1;
				i *= -1;
			}

			return i;
		}

		public static int sign10Bit(int i)
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


		public void skip(int i)
		{
			p += i;
		}
		public void seek(int i, int j)
		{
			if (j == 1)
			{
				p += i;
			}
			else
			{
				p = i;
			}
		}

		public int pos()
		{
			return p;
		}

		public int size()
		{
			return b.Length;
		}

		public string readString()
		{
			string s = "";
			while (b[p] != 0x00)
			{
				s += (char)b[p];
				p++;
			}
			return s;
		}
		public string readString2()
		{
			string s = "";
			while (b[p] != 0x00)
			{
				s += (char)b[p];
				p++;
			}
			p++;
			return s;
		}

		public string readString(int size)
		{
			string s = "";
			for(int i = 0; i < size; i++)
			{
				s += (char)b[p];
				p++;
			}
			return s;
		}

		public byte[] getSection(int offset, int size)
		{
			if (size == -1)
				size = b.Length - offset;
			byte[] by = new byte[size];

			Array.Copy(b, offset, by, 0, size);

			return by;
		}

		public string readString(int p, int size)
		{
			if (size == -1)
			{
				String str = "";
				while (p < b.Length)
				{
					if ((b[p] & 0xFF) != 0x00)
						str += (char)(b[p] & 0xFF);
					else
						break;
					p++;
				}
				return str;
			}
			
			string str2 = "";
			for (int i = p; i < p + size; i++)
			{
				if (i >= b.Length)
					return str2;
				if ((b[i] & 0xFF) != 0x00)
					str2 += (char)(b[i] & 0xFF);
			}
			return str2;
		}

		public void align(int i)
		{
			while (p % i != 0)
				p++;
		}

		public int getStart()
		{
			int probability = 0;
			for (int h = 0; h < 20000; ++h)
			{
				int c_0 = readInt();
				int c_1 = readInt();
				int c_2 = readShort();
				p += 8;
				uint c_3 = (uint)readInt();
				uint c_4 = (uint)readInt();
				uint c_5 = (uint)readInt();
				uint c_6 = (uint)readInt();
				uint c_7 = (uint)readInt();
				uint c_8 = (uint)readInt();
				
				if (c_0 == 0) {probability++;}
				if (c_1 == 0) {probability++;}
				if (c_2 == 1) {probability++;}
				if (c_3 > 1000000000) {probability++;}
				if (c_4 > 1000000000) {probability++;}
				if (c_5 > 1000000000) {probability++;}
				if (c_6 > 1000000000) {probability++;}
				if (c_7 > 1000000000) {probability++;}
				if (c_7 < 32) {probability++;}
				
				if (probability > 7)
				{
					p -= 4;
					return p;
				}
				else
				{
					probability = 0;
					p -= 41;
				}
			}
			return 0;
		}
	}
	
	public class Endianness
	{
		public static Endianness Little = new Endianness(), Big = new Endianness() { value = 1};
		public int value = 0;
	}
}