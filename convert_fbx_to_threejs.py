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

TEMPLATE_VERTEX = "%g,%g,%g"
TEMPLATE_N = "%g,%g,%g"
TEMPLATE_UV = "%g,%g"
TEMPLATE_C = "%d"
TEMPLATE_F = "%d"

# #####################################################
# Generate methods
# #####################################################
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

def extract_mesh(node):
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

    print(TEMPLATE_METADATA % metadata)
    print(TEMPLATE_MODEL % mesh)
    print(faces)

    print(len(positions))
    print(len(normals))
    print(len(uvs))
    print(len(faces))


# #####################################################
# Parse - hierarchy 
# #####################################################
def parse_scene_hierarchy(scene):
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            parse_node_hierarchy(node.GetChild(i))

def parse_node_hierarchy(node):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        lAttributeType = (node.GetNodeAttribute().GetAttributeType())

        if lAttributeType == FbxNodeAttribute.eMesh:
            extract_mesh(node)

    for i in range(node.GetChildCount()):
        parse_node_hierarchy(node.GetChild(i))


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
    if len(sys.argv) > 1:
        print("\n\nFile: %s\n" % sys.argv[1])
        result = LoadScene(sdk_manager, scene, sys.argv[1])
    else:
        result = False

        print("\n\nUsage: convert_fbx_to_threejs <FBX file name>\n")

    if not result:
        print("\n\nAn error occurred while loading the file...")
    else:
        parse_scene_hierarchy(scene)

    # Destroy all objects created by the FBX SDK.
    sdk_manager.Destroy()
    sys.exit(0)
