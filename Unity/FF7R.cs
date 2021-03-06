using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine.Bindings;

using UnityEditor;
using UnityEditor.Experimental;
using UnityEditor.Experimental.AssetImporters;
using UnityEngine;
using Unity.Collections;

namespace FF7R
{
	[ScriptedImporter(4, "uexp")]
	public class FF7R : ScriptedImporter
	{
		Material matSetup(Color col)
		{
			Material mat = new Material(Shader.Find("HDRP/Lit"));
			mat.SetColor("_Color",col);
			return mat;
		}
		
		
		public override void OnImportAsset (AssetImportContext ctx)
		{
			string fileName = System.IO.Path.GetFileNameWithoutExtension(ctx.assetPath);
			string fName_ = System.IO.Path.GetFileName(ctx.assetPath);
			
			string current_dir_rel = System.IO.Path.GetDirectoryName(ctx.assetPath);
			string current_dir_abs = System.IO.Path.GetFullPath(current_dir_rel);  //location
			string fName = Path.Combine(current_dir_abs, fName_);
			
			string dirName = System.IO.Path.GetFileName(current_dir_abs);
			
			
			FF7R_Utilities utils = new FF7R_Utilities();
			string[] the_files = utils.model_files(current_dir_abs);
			string model_dir = the_files[2];
			string file_a = the_files[0];
			string file_b = utils.get_largest_file(model_dir);
			
			
			
			
			if(fName == file_a && fName == file_b)
			{
				string c_name = the_files[3];
				MonoBehaviour.print($"Name: {c_name}");
				//MonoBehaviour.print($"fName : {fName}");
				//MonoBehaviour.Debug.Log($"fName : {fName}");
				//MonoBehaviour.print($"file_a: {file_a}");
				//MonoBehaviour.print($"file_b: {file_b}");
				
				
				byte[] fname = File.ReadAllBytes(fName);
				FileData md = new FileData(fname);
				
				byte[] fname_2 = File.ReadAllBytes(the_files[1]);
				FileData ua = new FileData(fname_2);
				
				var go = new GameObject(fileName);
				ctx.AddObjectToAsset(fileName, go);
				ctx.SetMainObject(go);

				QualitySettings.skinWeights = SkinWeights.Unlimited;

				/*  ???
				ModelImporter.skinWeights = ModelImporterSkinWeights.Custom;
				ModelImporter.maxBonesPerVertex = 8;
				*/




				// uasset
				byte check = (byte)ua.readByte();
				if (check == 193)
				{
					ua.Endian = Endianness.Little;
				}
				else
				{
					ua.Endian = Endianness.Big;
				}

				ua.seek(3,1);
				int version = ua.readInt();
				
				int thing1  = ua.readInt();
				int serialVersion = ua.readInt();
				int unk = ua.readInt();
				
				int headerCount = ua.readInt();
				
				for (int v = 0; v < headerCount; v++)
				{
					int v0 = ua.readInt();
					int v1 = ua.readInt();
					int v2 = ua.readInt();
					int v3 = ua.readInt();
					int unk_a = ua.readInt();
				}
				
				int uassetFileSize = ua.readInt();
				int unk0 = ua.readInt();
				int packageGroup = ua.readInt();
				int packageFlags = ua.readInt();
				int unk1 = ua.readByte();
				int stringCount = ua.readInt();
				int stringOffset = ua.readInt();
				
				ua.seek(stringOffset,0);
				List<string> names = new List<string>();
				for (int y = 0; y < stringCount; y++)
				{
					int size = ua.readInt();
					size -= 1;
					string name = ua.readString(size);
					int null_0 = ua.readByte();
					int unk_b = ua.readInt();
					names.Add(name);
				}



				
				// uexp
				int start = md.getStart();
				
				if (start == 0)
				{
					MonoBehaviour.print("Couldn't find beginning of data\n\n");
					throw new Exception();

				}

				md.seek(start,0);
				MonoBehaviour.print("start: " + start);
				MonoBehaviour.print("\n\n\n\n");
				int materialCount = md.readInt();
				MonoBehaviour.print("materialCount: " + materialCount);
				List<string> materials = new List<string>();
				for (int j = 0; j < materialCount; j++)
				{
					int val0 = md.readInt();
					
					int stringIndex = md.readInt();
					int zero0 = md.readInt();
					int one   = md.readInt();
					int zero1 = md.readInt();
					
					float fm0  = md.readFloat();
					float fm1  = md.readFloat();
					float fm2  = md.readFloat();
					
					int zero2 = md.readInt();
					materials.Add(names[stringIndex]);
				}
				
				
				List<Joint> joint_data = new List<Joint>();
				int boneCount = md.readInt();
				List<string> boneNAMES = new List<string>();
				MonoBehaviour.print("boneCount: " + boneCount);
				MonoBehaviour.print("\n");
				for (int j = 0; j< boneCount; ++j)
				{
					int string_index = md.readInt();
					int unk_c = md.readInt();
					int parent = md.readInt();
					string jointName = names[string_index];
					Joint new_joint = new Joint(jointName, parent);
					joint_data.Add(new_joint);
					boneNAMES.Add(jointName);
				}
				
				
				
				
				int boneCount2 = md.readInt();
				List<string> skl_n = new List<string>();
				Transform[] BNArr = new Transform[boneNAMES.Count];
				Matrix4x4[] bindPoses = new Matrix4x4[boneNAMES.Count];
				for (int k = 0; k < boneCount2; k++)
				{
					float qx = md.readFloat();
					float qy = md.readFloat();
					float qz = md.readFloat();
					float qw = md.readFloat();
					float px = md.readFloat();
					float py = md.readFloat();
					float pz = md.readFloat();
					float sx = md.readFloat();
					float sy = md.readFloat();
					float sz = md.readFloat();
					
					
					string boneName = joint_data[k].name;
					int BNparent = joint_data[k].parent;
					
					skl_n.Add (boneName);
					
					BNArr[k] = new GameObject(boneName).transform;
					
					
					if (BNparent != -1)
					{
						BNArr[k].parent = BNArr[BNparent];
					}
					BNArr[k].localRotation = new Quaternion(qx, qy, qz, qw);
					BNArr[k].localPosition = new Vector3(px, py, pz);
					//BNArr[k].localScale = new Vector3(sx, sy, sz);
					bindPoses[k] = BNArr[k].worldToLocalMatrix;
				}
				
				
				
				
				int boneCount3 = md.readInt();
				md.seek(boneCount3 * 12, 1);
				
				List<V_group> vertexGroups = new List<V_group>();
				int unk10 = md.readInt();
				int unk11 = md.readByte();
				int unk12 = md.readByte();
				uint groupCount = (uint)md.readInt();
				
				for (int m = 0; m <groupCount; ++m)
				{
					int z1 = md.readShort();
					ushort ID = (ushort)md.readShort();
					
					int null_a = md.readInt();
					int tri_count = md.readInt();
					md.seek(16,1);
					
					
					//# pragma region bone palette
					uint start_g = (uint)md.readInt();
					uint count = (uint)md.readInt();
					
					string[] bone_names = new string[count];
					int[] bone_IDs = new int[count];
					for (int bn = 0; bn <count; ++bn)
					{
						int bid = md.readShort();
						bone_IDs[bn] = bid;
						bone_names[bn] = joint_data[bid].name;
					}
					//# pragma endregion bone palette
					
					
					
					
					uint size = (uint)md.readInt();
					uint stop = start_g + size;
					
					md.seek(34,1);
					int FFx4 = md.readInt();
					uint flag = (uint)md.readInt();
					if (flag == 1) // extra data for this group
					{
						uint count_f = (uint)md.readInt();
						md.seek((int)count_f * 16, 1);
					}
					else
					{
						int null_gr = md.readInt();
					}

					int[] tris = new int[tri_count*3];
					V_group new_vgroup = new V_group(start_g, stop, size, bone_IDs, bone_names, tri_count, tris);
					vertexGroups.Add(new_vgroup);
				}
				//groupCount



				int unkByte = md.readByte();
				uint stride  = (uint)md.readInt();
				uint fCount  = (uint)md.readInt();
				
				int[] faces = new int[fCount];

				if (stride == 4)
				{
					foreach (V_group vg in vertexGroups)
					{
						for (int x = 0; x < vg.triangle_count; x++)
						{
							int yt = x * 3;
							int f0 = md.readInt();
							int f1 = md.readInt();
							int f2 = md.readInt();
							faces[yt] = f2;
							faces[yt + 1] = f1;
							faces[yt + 2] = f0;

							vg.triangles[yt] = f2;
							vg.triangles[yt + 1] = f1;
							vg.triangles[yt + 2] = f0;
						}
					}
				}
				else if (stride == 2)
				{
					foreach (V_group vg in vertexGroups)
					{
						for (int x = 0; x < vg.triangle_count; x++)
						{
							int yt = x * 3;
							int f0 = md.readInt();
							int f1 = md.readInt();
							int f2 = md.readInt();
							faces[yt] = f2;
							faces[yt + 1] = f1;
							faces[yt + 2] = f0;

							vg.triangles[yt] = f2;
							vg.triangles[yt + 1] = f1;
							vg.triangles[yt + 2] = f0;
						}
					}
				}
				
				
				
				
				int unkCount = md.readInt();
				md.seek(unkCount * 2, 1);

				int unk25 = md.readInt();
				int vertexCount = md.readInt();
				int boneCount4 = md.readInt();
				md.seek(boneCount4 * 2, 1);

				int null0 = md.readInt();
				int null1 = md.readInt();
				
				int uv_count  = md.readInt();
				int unk3      = md.readShort();
				int uv_count2 = md.readInt();
				
				int null2 = md.readInt();
				
				float unk4  = md.readFloat();
				float unk5  = md.readFloat();
				float unk6  = md.readFloat();
				
				int null3 = md.readInt();
				int null4 = md.readInt();
				int null5 = md.readInt();
				
				int vStride = md.readInt();
				int vCount  = md.readInt();
				
				int vertexCount2 = vCount * 3;
				
				int uvCount = vCount * 3;
				
				
				Vector2[]   UVs0 = new Vector2[vCount];
				Vector2[]   UVs1 = new Vector2[vCount];
				Vector2[]   UVs2 = new Vector2[vCount];
				Vector2[]   UVs3 = new Vector2[vCount];
				Vector3[] vArray = new Vector3[vCount];
				
				
				for (int v = 0; v < vCount; ++v)
				{
					float nt0 = md.readByte() /255.0f;
					float nt1 = md.readByte() /255.0f;
					float nt2 = md.readByte() /255.0f;
					float nt3 = md.readByte() /255.0f;

					float nt4 = md.readByte() /255.0f;
					float nt5 = md.readByte() /255.0f;
					float nt6 = md.readByte() /255.0f;
					float nt7 = md.readByte() /255.0f;
					
					float px = md.readFloat();
					float py = md.readFloat();
					float pz = md.readFloat();
					Vector3 pts = new Vector3(px, py, pz);
					vArray[v] = pts;
					
					if (uv_count > 0)
					{
						float u0 = md.readHalfFloat();
						float v0 = md.readHalfFloat() * -1.0f + 1.0f;
						Vector2 uv_0 = new Vector2(u0, v0);
						UVs0[v] = uv_0;
					}
					if (uv_count > 1)
					{
						float u1 = md.readHalfFloat();
						float v1 = md.readHalfFloat() * -1.0f + 1.0f;
						Vector2 uv_1 = new Vector2(u1, v1);
						UVs1[v] = uv_1;
					}
					if (uv_count > 2)
					{
						float u2 = md.readHalfFloat();
						float v2 = md.readHalfFloat() * -1.0f + 1.0f;
						Vector2 uv_2 = new Vector2(u2, v2);
						UVs2[v] = uv_2;
					}
					if (uv_count > 3)
					{
						float u3 = md.readHalfFloat();
						float v3 = md.readHalfFloat() * -1.0f + 1.0f;
						Vector2 uv_3 = new Vector2(u3, v3);
						UVs3[v] = uv_3;
					}
				}



				


				int unkS = md.readShort();
				int extraBoneWeights = md.readInt();
				int wCount = md.readInt();
				int w_stride = md.readInt();
				int wCount2 = md.readInt();
				
				int subStride = w_stride / 2;
				int bw_count = vCount * subStride;
				
				
				byte[] bonesPerVertex = new byte[wCount];
				for (int wz = 0; wz < wCount; ++wz)
				{
					bonesPerVertex[wz] = (byte)subStride;
				}
				var bonesPerVertexArray = new NativeArray<byte>(bonesPerVertex, Allocator.Temp);
				
				BoneWeight1[] weightsT = new BoneWeight1[bw_count];
				foreach (V_group q in vertexGroups)
				{
					int[] boneIDs = q.bones;
					string[] b_names = q.boneNames;
					int start_ = (int)q.start;
					int stop_  = (int)q.stop;
					
					for (int j = start_; j < stop_; ++j)
					{
						int jd = j * subStride;
						int[] b_temp = new int[subStride];
						for(int wc = 0; wc < subStride; ++wc)
						{
							int b0  = md.readByte();
							b_temp[wc] = boneIDs[b0];
						}
						
						for(int wd = 0; wd < subStride; ++wd)
						{
							float w0 = md.readByte() /255.0f;
							weightsT[jd+wd].boneIndex = b_temp[wd];
							weightsT[jd+wd].weight = w0;
						}
					}
				}



				string meshName = "Test";
				var go2 = new GameObject (meshName);
				go2.AddComponent<Animation> ();
				go2.AddComponent<SkinnedMeshRenderer> ();
				SkinnedMeshRenderer rend = go2.GetComponent<SkinnedMeshRenderer> ();
				
				Mesh ff7r = new Mesh ();
				ff7r.indexFormat = UnityEngine.Rendering.IndexFormat.UInt32;
				ff7r.vertices = vArray;
				//ff7r.triangles = faces;
				ff7r.uv = UVs0;
				ff7r.uv2 = UVs1;
				ff7r.uv3 = UVs2;

				Material[] dumbMaterials = new Material[(int)groupCount];
				
				ff7r.subMeshCount = (int)groupCount;
				for (int v = 0; v < groupCount; ++v)
				{
					ff7r.SetTriangles(vertexGroups[v].triangles, v);
					dumbMaterials[v] = matSetup(new Color(0.4f, 0.4f, 0.4f, 1));
					dumbMaterials[v].name = materials[v];
				}


				ff7r.name = meshName;
				rend.sharedMesh = ff7r;
				rend.sharedMaterials = dumbMaterials;

				var weightsArray = new NativeArray<BoneWeight1>(weightsT, Allocator.Temp);
				ff7r.bindposes = bindPoses;
				ff7r.SetBoneWeights(bonesPerVertexArray, weightsArray);
				rend.bones = BNArr;
				rend.rootBone = BNArr[0];
				rend.rootBone.transform.Rotate(-90.0f, 0.0f, 0.0f, Space.World);

				float t = 0.01f;
				Vector3 s = rend.rootBone.transform.localScale;
				rend.rootBone.transform.localScale = new Vector3(s.x*t, s.y*t, s.z*t);

				rend.updateWhenOffscreen = true;
				
			}
		}
	}
}