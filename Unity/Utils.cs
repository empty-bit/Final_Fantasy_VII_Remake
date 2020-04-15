using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using System.Linq;

using UnityEditor;
using UnityEditor.Experimental;
using UnityEditor.Experimental.AssetImporters;
using UnityEngine;




namespace FF7R
{
	public class FF7R_Utilities
	{
		static long GetFileLength(System.IO.FileInfo fi)
		{
			long retval;
			try
			{
				retval = fi.Length;
			}
			catch (System.IO.FileNotFoundException)
			{
				// If a file is no longer present,
				// just add zero bytes to the total.
				retval = 0;
			}
			return retval;
		}


		//https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/linq/how-to-query-for-the-largest-file-or-files-in-a-directory-tree-linq
		public string get_largest_file(string location)
		{
			// Take a snapshot of the file system.
			System.IO.DirectoryInfo dir = new System.IO.DirectoryInfo(location);

			// This method assumes that the application has discovery permissions
			// for all folders under the specified path.
			IEnumerable<System.IO.FileInfo> fileList = dir.GetFiles("*.uexp");

			// Return the FileInfo object for the largest file  
			// by sorting and selecting from beginning of list  
			System.IO.FileInfo longestFile = (from file in fileList let len = GetFileLength(file) where len > 0 orderby len descending select file).First();

			//MonoBehaviour.print("The largest file under {0} is {1} with a length of {2} bytes", location, longestFile.FullName, longestFile.Length);
			return longestFile.FullName;
		}



		public string[] model_files(string location)
		{
			string[] files = new string[4];
			string base_dir_rel = Directory.GetParent(location).ToString();
			string base_dir_abs = System.IO.Path.GetFullPath(base_dir_rel);
			//../Assets\NP0002_00_Jessie_Standard


			string base_dir_name = System.IO.Path.GetFileName(base_dir_abs);
			//"NP0002_00_Jessie_Standard"


			string textures_dir_rel = System.IO.Path.Combine(base_dir_rel, "Texture");
			string textures_dir_abs = System.IO.Path.GetFullPath(textures_dir_rel);
			//../Assets\NP0002_00_Jessie_Standard\Texture

			string materials_dir_rel = System.IO.Path.Combine(base_dir_rel, "Material");
			string materials_dir_abs = System.IO.Path.GetFullPath(materials_dir_rel);
			//../Assets\NP0002_00_Jessie_Standard\Material


			string model_dir_rel = System.IO.Path.Combine(base_dir_rel, "Model");
			string model_dir_abs = System.IO.Path.GetFullPath(model_dir_rel);
			//../Assets\NP0002_00_Jessie_Standard\Model


			char[] charSeparators = new char[] { '_' };
			string[] s0 = base_dir_name.Split(charSeparators);
			string s1 = String.Join("_", s0, 0, 2);
			string sn = String.Join("_", s0, 2, 2);
			string s2 = s1 + ".uexp";
			string s3 = s1 + ".uasset";


			string s4 = System.IO.Path.Combine(model_dir_abs, s2);
			files[0] = s4;
			//../Assets\NP0002_00_Jessie_Standard\Model\NP0002_00.uexp

			string s5 = Path.Combine(model_dir_abs, s3);
			files[1] = s5;
			//../Assets\NP0002_00_Jessie_Standard\Model\NP0002_00.uasset

			files[2] = model_dir_abs;
			files[3] = sn;

			return files;
		}

		public int[] create_array(int start, int stop, int size)
		{
			int c = 0;
			int[] new_array = new int[size];
			for (int i = start; i < stop; ++i)
			{
				new_array[c] = i;
				++c;
			}
			return new_array;
		}
	}
	public struct V_group
	{
		public readonly uint start;
		public readonly uint stop;
		public readonly uint size;
		public readonly int[] bones;
		public readonly string[] boneNames;
		public readonly int triangle_count;
		public readonly int[] triangles;
		
		public V_group(uint start_, uint stop_, uint size_, int[] bones_, string[] names_, int triangle_count_, int[] triangles_)
		{
			this  = new V_group();
			start = start_;
			stop  = stop_;
			size  = size_;
			bones = bones_;
			boneNames = names_;
			triangle_count = triangle_count_;
			triangles = triangles_;
		}
	}
	public struct Joint
	{
		public readonly string name;
		public readonly int parent;

		public Joint(string name_, int parent_)
		{
			this = new Joint();
			name = name_;
			parent = parent_;
		}
	}
}