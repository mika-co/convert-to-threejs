import os
import sys

# #####################################################
# Templates 
# #####################################################
TEMPLATE_GENERATED_BY = "https://github.com/zfedoran/fbx-to-threejs"

TEMPLATE_METADATA = """\
	"metadata" :
	{
		"formatVersion" : 3.1,
    "generatedBy"   : "%(generatedby)s",
		"vertices"      : %(nvertex)d,
		"faces"         : %(nface)d,
		"normals"       : %(nnormal)d,
		"colors"        : %(ncolor)d,
		"uvs"           : [%(nuvs)s],
		"materials"     : %(nmaterial)d,
		"morphTargets"  : %(nmorphTarget)d,
		"bones"         : %(nbone)d
	},
"""

TEMPLATE_MODEL = """\
	"scale" : %(scale)f,
	"materials" : [%(materials)s],
	"vertices" : [%(vertices)s],
	"morphTargets" : [%(morphTargets)s],
	"normals" : [%(normals)s],
	"colors" : [%(colors)s],
	"uvs" : [%(uvs)s],
	"faces" : [%(faces)s],
	"bones" : [%(bones)s],
	"skinIndices" : [%(skinIndices)s],
	"skinWeights" : [%(skinWeights)s],
	"animation" : {%(animation)s}
"""

TEMPLATE_SCENE_ASCII = """\
{

"metadata" :
{
    "formatVersion" : 3,
    "sourceFile"    : "%(fname)s",
    "generatedBy"   : "Blender 2.63 Exporter",
    "objects"       : %(nobjects)s,
    "geometries"    : %(ngeometries)s,
    "materials"     : %(nmaterials)s,
    "textures"      : %(ntextures)s
},

"type" : "scene",
"urlBaseType" : %(basetype)s,

%(sections)s

"transform" :
{
    "position"  : %(position)s,
    "rotation"  : %(rotation)s,
    "scale"     : %(scale)s
},

"defaults" :
{
    "bgcolor" : %(bgcolor)s,
    "bgalpha" : %(bgalpha)f,
    "camera"  : %(defcamera)s
}

}
"""

TEMPLATE_SECTION = """
"%s" :
{
%s
},
"""

TEMPLATE_OBJECT = """\
    "%(object_id)s" : {
        "geometry"  : "%(geometry_id)s",
        "groups"    : [ %(group_id)s ],
        "materials" : [ %(material_id)s ],
        "position"  : %(position)s,
        "rotation"  : %(rotation)s,
        "quaternion": %(quaternion)s,
        "scale"     : %(scale)s,
        "visible"       : %(visible)s,
        "castShadow"    : %(castShadow)s,
        "receiveShadow" : %(receiveShadow)s,
        "doubleSided"   : %(doubleSided)s
    }"""

TEMPLATE_EMPTY = """\
    %(object_id)s : {
        "groups"    : [ %(group_id)s ],
        "position"  : %(position)s,
        "rotation"  : %(rotation)s,
        "quaternion": %(quaternion)s,
        "scale"     : %(scale)s
    }"""

TEMPLATE_GEOMETRY_EMBED = """\
    %(geometry_id)s : {
        "type" : "embedded_mesh",
        "id"  : %(embed_id)s
    }"""

TEMPLATE_TEXTURE = """\
    %(texture_id)s : {
        "url": %(texture_file)s%(extras)s
    }"""

TEMPLATE_MATERIAL_SCENE = """\
    %(material_id)s : {
        "type": %(type)s,
        "parameters": { %(parameters)s }
    }"""

TEMPLATE_CAMERA_PERSPECTIVE = """\
    %(camera_id)s : {
        "type"  : "perspective",
        "fov"   : %(fov)f,
        "aspect": %(aspect)f,
        "near"  : %(near)f,
        "far"   : %(far)f,
        "position": %(position)s,
        "target"  : %(target)s
    }"""

TEMPLATE_CAMERA_ORTHO = """\
    %(camera_id)s: {
        "type"  : "ortho",
        "left"  : %(left)f,
        "right" : %(right)f,
        "top"   : %(top)f,
        "bottom": %(bottom)f,
        "near"  : %(near)f,
        "far"   : %(far)f,
        "position": %(position)s,
        "target"  : %(target)s
    }"""

TEMPLATE_LIGHT_DIRECTIONAL = """\
    %(light_id)s: {
        "type"       : "directional",
        "direction"  : %(direction)s,
        "color"    : %(color)d,
        "intensity"  : %(intensity).2f
    }"""

TEMPLATE_LIGHT_POINT = """\
    %(light_id)s: {
        "type"       : "point",
        "position"   : %(position)s,
        "color"      : %(color)d,
        "intensity"  : %(intensity).3f
    }"""

TEMPLATE_VEC4 = '[ %g, %g, %g, %g ]'
TEMPLATE_VEC3 = '[ %g, %g, %g ]'
TEMPLATE_VEC2 = '[ %g, %g ]'
TEMPLATE_STRING = '"%s"'
TEMPLATE_HEX = "0x%06x"

TEMPLATE_VERTEX = "%g,%g,%g"
TEMPLATE_N = "%g,%g,%g"
TEMPLATE_UV = "%g,%g"
TEMPLATE_C = "%d"
TEMPLATE_F = "%d"

# #####################################################
# Generate methods
# #####################################################

def generate_vec2(v):
    return TEMPLATE_VEC2 % (v[0], v[1])

def generate_vec3(v):
    return TEMPLATE_VEC3 % (v[0], v[1], v[2])

def generate_vec4(v):
    return TEMPLATE_VEC4 % (v[0], v[1], v[2], v[3])

def generate_vertex(v):
    return TEMPLATE_VERTEX % (v[0], v[1], v[2])

def generate_normal(n):
    return TEMPLATE_N % (n[0], n[1], n[2])

def generate_uv(uv):
    return TEMPLATE_UV % (uv[0], uv[1])


# #####################################################
# Parse - mesh 
# #####################################################
def setBit(value, position, on):
    if on:
        mask = 1 << position
        return (value | mask)
    else:
        mask = ~(1 << position)
        return (value & mask)

def extract_color(color):
    return [color.mRed, color.mGreen, color.mBlue]
    
def extract_vec2(v):
    return [v[0], v[1]]

def extract_vec3(v):
    return [v[0], v[1], v[2]]

def extract_vertex_positions(mesh):
    control_points_count = mesh.GetControlPointsCount()
    control_points = mesh.GetControlPoints()

    positions = []
    for i in range(control_points_count):
        positions.append(extract_vec3(control_points[i]))

    return positions

def extract_vertex_normals(mesh):
    control_points_count = mesh.GetControlPointsCount()
    control_points = mesh.GetControlPoints()

    normals = []
    for i in range(control_points_count):
        for j in range(mesh.GetLayerCount()):
            mesh_normals = mesh.GetLayer(j).GetNormals()
            if mesh_normals:
                if mesh_normals.GetMappingMode() == FbxLayerElement.eByControlPoint:
                    if mesh_normals.GetReferenceMode() == FbxLayerElement.eDirect:
                        normals.append(extract_vec3(mesh_normals.GetDirectArray().GetAt(i)))
    return normals

def extract_vertex_colors(mesh):
    control_points_count = mesh.GetControlPointsCount()
    control_points = mesh.GetControlPoints()

    colors = []
    for i in range(control_points_count):
        for j in range(mesh.GetLayerCount()):
            mesh_colors = mesh.GetLayer(j).GetUVs()
            if mesh_colors:
                if mesh_colors.GetMappingMode() == FbxLayerElement.eByControlPoint:
                    if mesh_colors.GetReferenceMode() == FbxLayerElement.eDirect:
                        colors.append(extract_color(mesh_colors.GetDirectArray().GetAt(i)))
                    elif mesh_colors.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
                        id = mesh_colors.GetIndexArray().GetAt(i)
                        colors.append(extract_color(mesh_colors.GetDirectArray().GetAt(id)))
                elif mesh_colors.GetMappingMode() ==  FbxLayerElement.eByPolygonVertex:
                    lTextureUVIndex = mesh.GetTextureUVIndex(i, j)
                    if mesh_colors.GetReferenceMode() == FbxLayerElement.eDirect or \
                       mesh_colors.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
                        colors.append(extract_color(mesh_colors.GetDirectArray().GetAt(lTextureUVIndex)))
                elif mesh_colors.GetMappingMode() == FbxLayerElement.eByPolygon or \
                     mesh_colors.GetMappingMode() == FbxLayerElement.eAllSame or \
                     mesh_colors.GetMappingMode() ==  FbxLayerElement.eNone:
                    pass
    return colors

def extract_vertex_uvs(mesh):
    control_points_count = mesh.GetControlPointsCount()
    control_points = mesh.GetControlPoints()

    uvs = []
    for i in range(control_points_count):
        for j in range(mesh.GetLayerCount()):
            mesh_uvs = mesh.GetLayer(j).GetUVs()
            if mesh_uvs:
                if mesh_uvs.GetMappingMode() == FbxLayerElement.eByControlPoint:
                    if mesh_uvs.GetReferenceMode() == FbxLayerElement.eDirect:
                        uvs.append(extract_vec2(mesh_uvs.GetDirectArray().GetAt(i)))
                    elif mesh_uvs.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
                        id = mesh_uvs.GetIndexArray().GetAt(i)
                        uvs.append(extract_vec2(mesh_uvs.GetDirectArray().GetAt(id)))
                elif mesh_uvs.GetMappingMode() ==  FbxLayerElement.eByPolygonVertex:
                    lTextureUVIndex = mesh.GetTextureUVIndex(i, j)
                    if mesh_uvs.GetReferenceMode() == FbxLayerElement.eDirect or \
                       mesh_uvs.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
                        uvs.append(extract_vec2(mesh_uvs.GetDirectArray().GetAt(lTextureUVIndex)))
                elif mesh_uvs.GetMappingMode() == FbxLayerElement.eByPolygon or \
                     mesh_uvs.GetMappingMode() == FbxLayerElement.eAllSame or \
                     mesh_uvs.GetMappingMode() ==  FbxLayerElement.eNone:
                    pass
    return uvs

def extract_mesh_face(indices, faceIndex, option_normals, option_colors, option_uv_coords, option_materials, vertex_offset, material_offset):
    isTriangle = ( len(indices) == 3 )

    if isTriangle:
        nVertices = 3
    else:
        nVertices = 4

    hasMaterial = option_materials

    hasFaceUvs = False # not supported in Blender
    hasFaceVertexUvs = option_uv_coords

    hasFaceNormals = False # don't export any face normals (as they are computed in engine)
    hasFaceVertexNormals = option_normals

    hasFaceColors = False # not supported in Blender
    hasFaceVertexColors = option_colors

    faceType = 0
    faceType = setBit(faceType, 0, not isTriangle)
    faceType = setBit(faceType, 1, hasMaterial)
    faceType = setBit(faceType, 2, hasFaceUvs)
    faceType = setBit(faceType, 3, hasFaceVertexUvs)
    faceType = setBit(faceType, 4, hasFaceNormals)
    faceType = setBit(faceType, 5, hasFaceVertexNormals)
    faceType = setBit(faceType, 6, hasFaceColors)
    faceType = setBit(faceType, 7, hasFaceVertexColors)

    faceData = []

    # order is important, must match order in JSONLoader

    # face type
    # vertex indices
    # material index
    # face uvs index
    # face vertex uvs indices
    # face color index
    # face vertex colors indices

    faceData.append(faceType)

    # must clamp in case on polygons bigger than quads

    for i in range(nVertices):
        index = indices[i] + vertex_offset
        faceData.append(index)

#    if hasMaterial:
#        index = f.material_index + material_offset
#        faceData.append( index )

    if hasFaceVertexUvs:
        for i in range(nVertices):
            index = indices[i]
            faceData.append(index)

    if hasFaceVertexNormals:
        for i in range(nVertices):
            index = indices[i]
            faceData.append(index)

    if hasFaceVertexColors:
        for i in range(nVertices):
            index = indices[i]
            faceData.append(index)

    return ",".join( map(str, faceData) )

def extract_mesh_faces(mesh, option_normals, option_colors, option_uv_coords, option_materials, vertex_offset, material_offset):
    poly_count = mesh.GetPolygonCount()
    control_points = mesh.GetControlPoints() 

    faces = []
    for i in range(poly_count):
        poly_size = mesh.GetPolygonSize(i)
        face = []
        for j in range(poly_size):
            control_point_index = mesh.GetPolygonVertex(i, j)
            face.append(control_point_index)
        face = extract_mesh_face(face, i, option_normals, option_colors, option_uv_coords, option_materials, vertex_offset, material_offset)
        faces.append(face)
    return faces

def extract_mesh_from_node(node):
    mesh = node.GetNodeAttribute()
    positions = extract_vertex_positions(mesh)
    normals = extract_vertex_normals(mesh)
    uvs = extract_vertex_uvs(mesh)
    colors = []
    materials = []
    option_normals = len(normals) > 0
    option_colors = len(colors) > 0
    option_uv_coords = len(uvs) > 0
    option_materials = len(materials) > 0
    vertex_offset = 0
    material_offset = 0
    faces = extract_mesh_faces(mesh, option_normals, option_colors, option_uv_coords, option_materials, vertex_offset, material_offset)

    metadata = {
      "generatedby"   : TEMPLATE_GENERATED_BY,
      "nvertex"      : len(positions),
      "nface"         : len(faces),
      "nnormal"       : len(normals),
      "ncolor"        : len(colors),
      "nuvs"           : [len(uvs)],
      "nmaterial"     : 0,
      "nmorphTarget"  : 0,
      "nbone"         : 0
    }

    mesh = {
      "scale" : 1,
      "materials" : "",
      "vertices" : ",".join(generate_vertex(v) for v in positions),
      "morphTargets" : "",
      "normals" : ",".join(generate_normal(v) for v in normals),
      "colors" : "",
      "uvs" : ",".join(generate_uv(v) for v in uvs),
      "faces" : ",".join(faces),
      "bones" : "",
      "skinIndices" : "",
      "skinWeights" : "",
      "animation" : ""
    }

    print(len(positions))
    print(len(normals))
    print(len(uvs))
    print(len(faces))

    mesh_output = ""
    mesh_output += TEMPLATE_METADATA % metadata
    mesh_output += TEMPLATE_MODEL % mesh
    return mesh_output

def extract_mesh_list_from_hierarchy(node, mesh_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        lAttributeType = (node.GetNodeAttribute().GetAttributeType())
        if lAttributeType == FbxNodeAttribute.eMesh:
            mesh = extract_mesh_from_node(node)
            mesh_list.append(mesh)
    for i in range(node.GetChildCount()):
        extract_mesh_list_from_hierarchy(node.GetChild(i), mesh_list)

def extract_mesh_list_from_scene(scene):
    mesh_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            extract_mesh_list_from_hierarchy(node.GetChild(i), mesh_list)
    return mesh_list

# #####################################################
# Parse - Objects 
# #####################################################
def extract_mesh_object_from_node(node):
    transform = node.EvaluateGlobalTransform()
    translation = generate_vec3(transform.GetT())
    scale = generate_vec3(transform.GetS())
    rotation = generate_vec3(transform.GetR())
    rotationq = generate_vec4(transform.GetQ())

    object_info = {
      "object_id": node.GetName(),
      "geometry_id": "",
      "group_id": "",
      "material_id": "",
      "position": translation,
      "rotation": rotation,
      "quaternion": rotationq,
      "scale": scale,
      "visible": "",
      "castShadow": "",
      "receiveShadow": "",
      "doubleSided": ""
    }

    return TEMPLATE_OBJECT % object_info


def extract_scene_object_list_from_hierarchy(node, scene_object_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        lAttributeType = (node.GetNodeAttribute().GetAttributeType())
        if lAttributeType == FbxNodeAttribute.eMesh:
            scene_object = extract_mesh_object_from_node(node)
            scene_object_list.append(scene_object)
    for i in range(node.GetChildCount()):
        extract_scene_object_list_from_hierarchy(node.GetChild(i), scene_object_list)

def extract_scene_object_list_from_scene(scene):
    scene_object_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            extract_scene_object_list_from_hierarchy(node.GetChild(i), scene_object_list)
    return scene_object_list

# #####################################################
# Parse - Scene 
# #####################################################
#(fname)s,
#(nobjects)s,
#(ngeometries)s,
#(nmaterials)s,
#(ntextures)s
#(position)s,
#(rotation)s,
#(scale)s
#(bgcolor)s,
#(bgalpha)f,
#(defcamera)s
#(basetype)s,
#(sections)s
def extract_scene(scene, filename):
    scene_object_list = extract_scene_object_list_from_scene(scene)
    mesh_list = extract_mesh_list_from_scene(scene)
    
    scene_info = {
      "fname": filename, 
      "nobjects": len(scene_object_list),
      
    }

    print(scene_info)
    
    output = ""
    output += "".join(mesh_list)
    return output

# #####################################################
# helpers
# #####################################################
def write_file(fname, content):
    out = open(fname, "w")
    out.write(content)
    out.close()

# #####################################################
# main
# #####################################################
if __name__ == "__main__":
    try:
        from FbxCommon import *
    except ImportError:
        import platform
        msg = 'Could not locate the python FBX SDK!\n'
        msg += 'You need to copy the FBX SDK into your python install folder such as '
        if platform.system() == 'Windows' or platform.system() == 'Microsoft':
            msg += '"Python26/Lib/site-packages"'
        elif platform.system() == 'Linux':
            msg += '"/usr/local/lib/python2.6/site-packages"'
        elif platform.system() == 'Darwin':
            msg += '"/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages"'        
        msg += ' folder.'
        print(msg) 
        sys.exit(1)

    # Prepare the FBX SDK.
    sdk_manager, scene = InitializeSdkObjects()

    # The converter takes an FBX file as an argument.
    if len(sys.argv) > 2:
        print("\n\nFile: %s\n" % sys.argv[1])
        result = LoadScene(sdk_manager, scene, sys.argv[1])
    else:
        result = False
        print("\n\nUsage: convert_fbx_to_threejs [source_file.fbx] [output_file.js]\n")

    if not result:
        print("\n\nAn error occurred while loading the file...")
    else:
        output_content = extract_scene(scene, os.path.basename(sys.argv[1]))
        output_path = os.path.join(os.getcwd(), sys.argv[2])
        write_file(output_path, output_content)
        print("\n\nExported Three.js file to:\n%s\n" % output_path)

    # Destroy all objects created by the FBX SDK.
    sdk_manager.Destroy()
    sys.exit(0)
