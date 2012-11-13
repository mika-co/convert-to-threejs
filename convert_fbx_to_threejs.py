import os
import sys
import math

# #####################################################
# Configuration
# #####################################################

DEFAULTS = {
"bgcolor" : [0.667,0.667,0.667],
"bgalpha" : 1.0,

"position" : [0, 0, 0],
"rotation" : [-math.pi/2, 0, 0],
"scale"    : [1, 1, 1],

"camera"  :
    {
        "name" : "default_camera",
        "type" : "PerspectiveCamera",
        "near" : 1,
        "far"  : 10000,
        "fov"  : 60,
        "aspect": 1.333,
        "position" : [0, 0, 10],
        "target"   : [0, 0, 0]
    },

"light" :
 {
    "name"       : "default_light",
    "type"       : "directional",
    "direction"  : [0, 1, 1],
    "color"      : [1, 1, 1],
    "intensity"  : 0.8
 }
}

# default colors for debugging (each material gets one distinct color):
# white, red, green, blue, yellow, cyan, magenta
COLORS = [0xeeeeee, 0xee0000, 0x00ee00, 0x0000ee, 0xeeee00, 0x00eeee, 0xee00ee]


# skinning
MAX_INFLUENCES = 2


# #####################################################
# Templates 
# #####################################################
TEMPLATE_SCENE_ASCII = """\
{

"metadata" :
{
    "formatVersion" : 3.1,
    "sourceFile"    : %(fname)s,
    "generatedBy"   : "https://github.com/zfedoran/fbx-to-threejs",
    "objects"       : %(nobjects)s,
    "geometries"    : %(ngeometries)s,
    "materials"     : %(nmaterials)s,
    "textures"      : %(ntextures)s,
    "cameras"       : %(ncameras)s,
    "lights"        : %(nlights)s,
    "type"          : "scene"
},

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
    "camera"  : %(defcamera)s,
    "fog"     : %(fog)s
}

}
"""

TEMPLATE_SECTION = """
"%s" :
{
%s
},
"""

TEMPLATE_MESH = """\
%(metadata)s
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

TEMPLATE_MESH_METADATA = """\
"metadata" : {
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

TEMPLATE_MESH_EMBED = """\
    "%(embed_id)s" : {
        %(embed)s
    }"""

TEMPLATE_OBJECT = """\
    "%(object_id)s" : {
        "geometry"  : "%(geometry_id)s",
        "groups"    : [ %(group_id)s ],
        "materials" : [ %(materials)s ],
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
        "type" : "embedded",
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
        "type"  : "PerspectiveCamera",
        "fov"   : %(fov)f,
        "aspect": %(aspect)f,
        "near"  : %(near)f,
        "far"   : %(far)f,
        "position": %(position)s,
        "target"  : %(target)s
    }"""

TEMPLATE_CAMERA_ORTHO = """\
    %(camera_id)s: {
        "type"  : "OrthographicCamera",
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
        "type"       : "DirectionalLight",
        "direction"  : %(direction)s,
        "color"    : %(color)d,
        "intensity"  : %(intensity).2f
    }"""

TEMPLATE_LIGHT_POINT = """\
    %(light_id)s: {
        "type"       : "PointLight",
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

def generate_uvs(uv_layers):
    layers = []
    for uvs in uv_layers:
        layer = ",".join(generate_uv(n) for n in uvs)
        layers.append(layer)

    return ",".join("[%s]" % n for n in layers)

def generate_section(label, content):
    return TEMPLATE_SECTION % (label, content)

def generate_bool_property(property):
    if property:
        return "true"
    return "false"

def generate_string(s):
    return TEMPLATE_STRING % s

def generate_color(rgb):
    color = (int(rgb[0]*255) << 16) + (int(rgb[1]*255) << 8) + int(rgb[2]*255)
    return color
    
def generate_rotation(v):
    return TEMPLATE_VEC3 % (v[0]/180, v[1]/180, v[2]/180)

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
#   eNone             The mapping is undetermined.
#   eByControlPoint   There will be one mapping coordinate for each surface control point/vertex.
#   eByPolygonVertex  There will be one mapping coordinate for each vertex, for every polygon of which it is a part. This means that a vertex will have as many mapping coordinates as polygons of which it is a part.
#   eByPolygon        There can be only one mapping coordinate for the whole polygon.
#   eByEdge           There will be one mapping coordinate for each unique edge in the mesh. This is meant to be used with smoothing layer elements.
#   eAllSame          There can be only one mapping coordinate for the whole surface.

    layered_normal_indices = []
    layered_normal_values = []

    poly_count = mesh.GetPolygonCount()
    control_points = mesh.GetControlPoints() 

    for l in range(mesh.GetLayerCount()):
        mesh_normals = mesh.GetLayer(l).GetNormals()
        if not mesh_normals:
            continue
          
        normals_array = mesh_normals.GetDirectArray()
        normals_count = normals_array.GetCount()
  
        if normals_count == 0:
            continue

        normal_indices = []
        normal_values = []

        # values
        for i in range(normals_count):
            normal = extract_vec3(normals_array.GetAt(i))
            normal_values.append(normal)

        # indices
        vertexId = 0
        for p in range(poly_count):
            poly_size = mesh.GetPolygonSize(p)
            poly_normals = []

            for v in range(poly_size):
                control_point_index = mesh.GetPolygonVertex(p, v)

                if mesh_normals.GetMappingMode() == FbxLayerElement.eByControlPoint:
                    if mesh_normals.GetReferenceMode() == FbxLayerElement.eDirect:
                        poly_normals.append(control_point_index)
                    elif mesh_normals.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
                        index = mesh_normals.GetIndexArray().GetAt(control_point_index)
                        poly_normals.append(index)
                elif mesh_normals.GetMappingMode() == FbxLayerElement.eByPolygonVertex:
                    if mesh_normals.GetReferenceMode() == FbxLayerElement.eDirect:
                        poly_normals.append(vertexId)
                    elif mesh_normals.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
                        index = mesh_normals.GetIndexArray().GetAt(vertexId)
                        poly_normals.append(index)
                elif mesh_normals.GetMappingMode() == FbxLayerElement.eByPolygon or \
                     mesh_normals.GetMappingMode() ==  FbxLayerElement.eAllSame or \
                     mesh_normals.GetMappingMode() ==  FbxLayerElement.eNone:       
                    print("unsupported normal mapping mode for polygon vertex")

                vertexId += 1
            normal_indices.append(poly_normals)

        layered_normal_values.append(normal_values)
        layered_normal_indices.append(normal_indices)

    return layered_normal_values, layered_normal_indices

def extract_vertex_colors(mesh):
#   eNone             The mapping is undetermined.
#   eByControlPoint   There will be one mapping coordinate for each surface control point/vertex.
#   eByPolygonVertex  There will be one mapping coordinate for each vertex, for every polygon of which it is a part. This means that a vertex will have as many mapping coordinates as polygons of which it is a part.
#   eByPolygon        There can be only one mapping coordinate for the whole polygon.
#   eByEdge           There will be one mapping coordinate for each unique edge in the mesh. This is meant to be used with smoothing layer elements.
#   eAllSame          There can be only one mapping coordinate for the whole surface.

    layered_color_indices = []
    layered_color_values = []

    poly_count = mesh.GetPolygonCount()
    control_points = mesh.GetControlPoints() 

    for l in range(mesh.GetLayerCount()):
        mesh_colors = mesh.GetLayer(l).GetVertexColors()
        if not mesh_colors:
            continue
          
        colors_array = mesh_colors.GetDirectArray()
        colors_count = colors_array.GetCount()
  
        if colors_count == 0:
            continue

        color_indices = []
        color_values = []

        # values
        for i in range(colors_count):
            color = extract_color(colors_array.GetAt(i))
            color_values.append(color)

        # indices
        vertexId = 0
        for p in range(poly_count):
            poly_size = mesh.GetPolygonSize(p)
            poly_colors = []

            for v in range(poly_size):
                control_point_index = mesh.GetPolygonVertex(p, v)

                if mesh_colors.GetMappingMode() == FbxLayerElement.eByControlPoint:
                    if mesh_colors.GetReferenceMode() == FbxLayerElement.eDirect:
                        poly_colors.append(control_point_index)
                    elif mesh_colors.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
                        index = mesh_colors.GetIndexArray().GetAt(control_point_index)
                        poly_colors.append(index)
                elif mesh_colors.GetMappingMode() == FbxLayerElement.eByPolygonVertex:
                    if mesh_colors.GetReferenceMode() == FbxLayerElement.eDirect:
                        poly_colors.append(vertexId)
                    elif mesh_colors.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
                        index = mesh_colors.GetIndexArray().GetAt(vertexId)
                        poly_colors.append(index)
                elif mesh_colors.GetMappingMode() == FbxLayerElement.eByPolygon or \
                     mesh_colors.GetMappingMode() ==  FbxLayerElement.eAllSame or \
                     mesh_colors.GetMappingMode() ==  FbxLayerElement.eNone:       
                    print("unsupported color mapping mode for polygon vertex")

                vertexId += 1
            color_indices.append(poly_colors)

        layered_color_values.append(color_values)
        layered_color_indices.append(color_indices)

    return layered_color_values, layered_color_indices

def extract_vertex_uvs(mesh):
#   eNone             The mapping is undetermined.
#   eByControlPoint   There will be one mapping coordinate for each surface control point/vertex.
#   eByPolygonVertex  There will be one mapping coordinate for each vertex, for every polygon of which it is a part. This means that a vertex will have as many mapping coordinates as polygons of which it is a part.
#   eByPolygon        There can be only one mapping coordinate for the whole polygon.
#   eByEdge           There will be one mapping coordinate for each unique edge in the mesh. This is meant to be used with smoothing layer elements.
#   eAllSame          There can be only one mapping coordinate for the whole surface.

    layered_uv_indices = []
    layered_uv_values = []

    poly_count = mesh.GetPolygonCount()
    control_points = mesh.GetControlPoints() 

    for l in range(mesh.GetLayerCount()):
        mesh_uvs = mesh.GetLayer(l).GetUVs()
        if not mesh_uvs:
            continue
          
        uvs_array = mesh_uvs.GetDirectArray()
        uvs_count = uvs_array.GetCount()
  
        if uvs_count == 0:
            continue

        uv_indices = []
        uv_values = []

        # values
        for i in range(uvs_count):
            uv = extract_vec2(uvs_array.GetAt(i))
            uv_values.append(uv)

        # indices
        vertexId = 0
        for p in range(poly_count):
            poly_size = mesh.GetPolygonSize(p)
            poly_uvs = []

            for v in range(poly_size):
                control_point_index = mesh.GetPolygonVertex(p, v)

                if mesh_uvs.GetMappingMode() == FbxLayerElement.eByControlPoint:
                    if mesh_uvs.GetReferenceMode() == FbxLayerElement.eDirect:
                        poly_uvs.append(control_point_index)
                    elif mesh_uvs.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
                        index = mesh_uvs.GetIndexArray().GetAt(control_point_index)
                        poly_uvs.append(index)
                elif mesh_uvs.GetMappingMode() == FbxLayerElement.eByPolygonVertex:
                    uv_texture_index = mesh.GetTextureUVIndex(p, v)
                    if mesh_uvs.GetReferenceMode() == FbxLayerElement.eDirect or \
                       mesh_uvs.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
                        poly_uvs.append(uv_texture_index)
                elif mesh_uvs.GetMappingMode() == FbxLayerElement.eByPolygon or \
                     mesh_uvs.GetMappingMode() ==  FbxLayerElement.eAllSame or \
                     mesh_uvs.GetMappingMode() ==  FbxLayerElement.eNone:       
                    print("unsupported uv mapping mode for polygon vertex")

                vertexId += 1
            uv_indices.append(poly_uvs)

        layered_uv_values.append(uv_values)
        layered_uv_indices.append(uv_indices)

    return layered_uv_values, layered_uv_indices

def generate_mesh_face(vertex_indices, polygon_index, normals, colors, uv_layers, materials):
  
    isTriangle = ( len(vertex_indices) == 3 )
    nVertices = 3 if isTriangle else 4

    hasMaterial = len(materials) > 0
    hasFaceUvs = False
    hasFaceVertexUvs = len(uv_layers) > 0
    hasFaceNormals = False # don't export any face normals (as they are computed in engine)
    hasFaceVertexNormals = len(normals) > 0
    hasFaceColors = False 
    hasFaceVertexColors = len(colors) > 0

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
        index = vertex_indices[i]
        faceData.append(index)

    if hasMaterial:
        #TODO: get the correct material index
        faceData.append( 0 )

    if hasFaceVertexUvs:
        for layer_index, uvs in enumerate(uv_layers):
            polygon_uvs = uvs[polygon_index]
            for i in range(nVertices):
                index = polygon_uvs[i]
                faceData.append(index)

    if hasFaceVertexNormals:
        polygon_normals = normals[polygon_index]
        for i in range(nVertices):
            index = polygon_normals[i]
            faceData.append(index)

    if hasFaceVertexColors:
        polygon_colors = colors[polygon_index]
        for i in range(nVertices):
            index = polygon_colors[i]
            faceData.append(index)

    return ",".join( map(str, faceData) )

def generate_mesh_faces(mesh, normals, colors, uv_layers, materials):
    poly_count = mesh.GetPolygonCount()
    control_points = mesh.GetControlPoints() 

    faces = []
    for p in range(poly_count):
        poly_size = mesh.GetPolygonSize(p)
        vertex_indices = []
        for v in range(poly_size):
            control_point_index = mesh.GetPolygonVertex(p, v)
            vertex_indices.append(control_point_index)
        face = generate_mesh_face(vertex_indices, p, normals, colors, uv_layers, materials)
        faces.append(face)
    return faces

def extract_mesh_materials(mesh):
    material_list = []
    node = None
    if mesh:
        node = mesh.GetNode()
        if node:
            material_count = node.GetMaterialCount()

    for l in range(mesh.GetLayerCount()):
        materials = mesh.GetLayer(l).GetMaterials()
        if materials:
            if materials.GetReferenceMode() == FbxLayerElement.eIndex:
                #Materials are in an undefined external table
                continue
            for i in range(material_count):
                material = node.GetMaterial(i)
                material_list.append(material.GetName())

    return material_list

def extract_mesh_from_node(node):
    mesh = node.GetNodeAttribute()
    vertices = extract_vertex_positions(mesh)
    materials = extract_mesh_materials(mesh)

    normal_values, normal_indices = extract_vertex_normals(mesh)
    color_values, color_indices = extract_vertex_colors(mesh)
    uv_values, uv_indices = extract_vertex_uvs(mesh)

    # Three.js only supports one layer of normals
    if len(normal_values) > 0:
        normal_values = normal_values[0]
        normal_indices = normal_indices[0]

    # Three.js only supports one layer of colors
    if len(color_values) > 0:
        color_values = color_values[0]
        color_indices = color_indices[0]

    faces = generate_mesh_faces(mesh, normal_indices, color_indices, uv_indices, materials)

    nuvs = []
    for layer_index, uvs in enumerate(uv_values):
        nuvs.append(str(len(uvs)))

    metadata = {
      "nvertex"      : len(vertices),
      "nface"         : len(faces),
      "nnormal"       : len(normal_values),
      "ncolor"        : len(color_values),
      "nuvs"          : ",".join(nuvs),
      "nmaterial"     : len(materials),
      "nmorphTarget"  : 0,
      "nbone"         : 0
    }

    mesh = {
      "metadata" : TEMPLATE_MESH_METADATA % metadata,
      "scale" : 1,
      "materials" : "",
      "vertices" : ",".join(generate_vertex(v) for v in vertices),
      "morphTargets" : "",
      "normals" : ",".join(generate_normal(v) for v in normal_values),
      "colors" : ",".join(generate_vec3(v) for v in color_values),
      "uvs" : generate_uvs(uv_values),
      "faces" : ",".join(faces),
      "bones" : "",
      "skinIndices" : "",
      "skinWeights" : "",
      "animation" : ""
    }

    return TEMPLATE_MESH % mesh

# #####################################################
# Parse - Objects 
# #####################################################
def extract_mesh_object_from_node(node):
    name = node.GetName()
    mesh = node.GetNodeAttribute()

    transform = node.EvaluateGlobalTransform()
    translation = generate_vec3(transform.GetT())
    scale = generate_vec3(transform.GetS())
    rotation = generate_rotation(transform.GetR())
    rotationq = generate_vec4(transform.GetQ())
    materials = extract_mesh_materials(mesh)

    object_info = {
      "object_id": name,
      "geometry_id": "geo_" + name,
      "group_id": "",
      "materials": ",".join(generate_string(m) for m in materials),
      "position": translation,
      "rotation": rotation,
      "quaternion": rotationq,
      "scale": scale,
      "visible": generate_bool_property(True),
      "castShadow": generate_bool_property(False),
      "receiveShadow": generate_bool_property(False),
      "doubleSided": generate_bool_property(False),
    }

    return TEMPLATE_OBJECT % object_info

def generate_scene_object_list_from_hierarchy(node, scene_object_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        attribute_type = (node.GetNodeAttribute().GetAttributeType())
        if attribute_type == FbxNodeAttribute.eMesh:
            scene_object = extract_mesh_object_from_node(node)
            scene_object_list.append(scene_object)
    for i in range(node.GetChildCount()):
        generate_scene_object_list_from_hierarchy(node.GetChild(i), scene_object_list)

def generate_scene_object_list(scene):
    scene_object_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            generate_scene_object_list_from_hierarchy(node.GetChild(i), scene_object_list)
    return scene_object_list

# #####################################################
# Parse - Geometries 
# #####################################################
def extract_geometry_from_node(node):
    name = node.GetName()

    geometry_info = {
      "geometry_id": generate_string("geo_" + name),
      "embed_id":  generate_string("emb_" + name),
    }

    return TEMPLATE_GEOMETRY_EMBED % geometry_info

def generate_scene_geometry_list_from_hierarchy(node, scene_geometry_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        attribute_type = (node.GetNodeAttribute().GetAttributeType())
        if attribute_type == FbxNodeAttribute.eMesh:
            scene_geometry = extract_geometry_from_node(node)
            scene_geometry_list.append(scene_geometry)
    for i in range(node.GetChildCount()):
        generate_scene_geometry_list_from_hierarchy(node.GetChild(i), scene_geometry_list)

def generate_scene_geometry_list(scene):
    scene_geometry_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            generate_scene_geometry_list_from_hierarchy(node.GetChild(i), scene_geometry_list)
    return scene_geometry_list

# #####################################################
# Parse - Embeds 
# #####################################################
def extract_embed_from_node(node):
    mesh = extract_mesh_from_node(node)
    name = node.GetName()

    embed_info = {
      "embed_id": "emb_" + name,
      "embed": mesh
    }

    return TEMPLATE_MESH_EMBED % embed_info

def generate_scene_embed_list_from_hierarchy(node, scene_embed_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        attribute_type = (node.GetNodeAttribute().GetAttributeType())
        if attribute_type == FbxNodeAttribute.eMesh:
            scene_embed = extract_embed_from_node(node)
            scene_embed_list.append(scene_embed)
    for i in range(node.GetChildCount()):
        generate_scene_embed_list_from_hierarchy(node.GetChild(i), scene_embed_list)

def generate_scene_embed_list(scene):
    scene_embed_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            generate_scene_embed_list_from_hierarchy(node.GetChild(i), scene_embed_list)
    return scene_embed_list

# #####################################################
# Parse - Material 
# #####################################################
def generate_material_string(material):
    material_id = material.GetName()

    type_map = {
    "Lambert"   : "MeshLambertMaterial",
    "Phong"     : "MeshPhongMaterial"
    }

    fbxColor = FbxColor()

    #Get the implementation to see if it's a hardware shader.
    implementation = GetImplementation(material, "ImplementationHLSL")
    implementation_type = "HLSL"
    if not implementation:
        implementation = GetImplementation(material, "ImplementationCGFX")
        implementation_type = "CGFX"

    if implementation:
        # This material is a hardware shader, skip it
        material_info["hardware_shader_type"] = implementation_type.Buffer()

    elif (material.GetClassId().Is(FbxSurfacePhong.ClassId)):
        # We found a Phong material.  
        material_type = "Phong"
        ambient   = generate_color(material.Ambient.Get())
        diffuse   = generate_color(material.Diffuse.Get())
        specular  = generate_color(material.Specular.Get())
        emissive  = generate_color(material.Emissive.Get())
        transparency = 1.0 - material.TransparencyFactor.Get()
        shininess = material.Shininess.Get()
        reflectivity = generate_vec3(material.Reflection.Get())
        
        parameters = '"color": %d' % diffuse
        parameters += ', "opacity": %.2g' % transparency
        parameters += ', "ambient": %d' % ambient
        parameters += ', "specular": %d' % specular
        parameters += ', "shininess": %.1g' % shininess

    elif material.GetClassId().Is(FbxSurfaceLambert.ClassId):
        # We found a Lambert material. Display its properties.
        material_type = "Lambert"
        ambient   = generate_color(material.Ambient.Get())
        diffuse   = generate_color(material.Diffuse.Get())
        emissive  = generate_color(material.Emissive.Get())
        transparency = 1.0 - material.TransparencyFactor.Get()
        
        parameters = '"color": %d' % diffuse
        parameters += ', "opacity": %.2g' % transparency
        parameters += ', "ambient": %d' % ambient

    else: 
        print("Unknown type of Material")
        return ""

    parameters += ', "wireframe": false'
    parameters += ', "wireframeLinewidth": 1'

    material_info = {
    "material_id" : generate_string(material_id),
    "type"        : generate_string(type_map[material_type]),
    "parameters"  : parameters
    }

    return TEMPLATE_MATERIAL_SCENE % material_info

def extract_materials_from_node(node, scene_material_list):
    name = node.GetName()
    mesh = node.GetNodeAttribute()

    node = None
    if mesh:
        node = mesh.GetNode()
        if node:
            material_count = node.GetMaterialCount()

    for l in range(mesh.GetLayerCount()):
        materials = mesh.GetLayer(l).GetMaterials()
        if materials:
            if materials.GetReferenceMode() == FbxLayerElement.eIndex:
                #Materials are in an undefined external table
                continue
            for i in range(material_count):
                material = node.GetMaterial(i)
                scene_material = generate_material_string(material)
                scene_material_list.append(scene_material)

def generate_scene_material_list_from_hierarchy(node, scene_material_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        attribute_type = (node.GetNodeAttribute().GetAttributeType())
        if attribute_type == FbxNodeAttribute.eMesh:
            extract_materials_from_node(node, scene_material_list)
    for i in range(node.GetChildCount()):
        generate_scene_material_list_from_hierarchy(node.GetChild(i), scene_material_list)

def generate_scene_material_list(scene):
    scene_material_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            generate_scene_material_list_from_hierarchy(node.GetChild(i), scene_material_list)
    return scene_material_list

# #####################################################
# Parse - Textures 
# #####################################################
def extract_material_textures(material_property, material_index, scene_texture_list):
    if material_property.IsValid():
        #Here we have to check if it's layeredtextures, or just textures:
        layered_texture_count = material_property.GetSrcObjectCount(FbxLayeredTexture.ClassId)
        if layered_texture_count > 0:
            for j in range(layered_texture_count):
                layered_texture = material_property.GetSrcObject(FbxLayeredTexture.ClassId, j)
                texture_count = layered_texture.GetSrcObjectCount(FbxTexture.ClassId)
                for k in range(texture_count):
                    texture = layered_texture.GetSrcObject(FbxTexture.ClassId,k)
                    if texture:
                        # NOTE the blend mode is ALWAYS on the LayeredTexture and NOT the one on the texture.
                        # Why is that?  because one texture can be shared on different layered textures and might
                        # have different blend modes.

                        texture_file = texture.GetFileName()
                        texture_id = os.path.splitext(os.path.basename(texture_file))[0]
                        wrap_u = texture.GetWrapModeU()
                        wrap_v = texture.GetWrapModeV()
                        offset = texture.GetUVTranslation()
                        
                        #TODO: read extra values from the actual textures
                        extras = ""
                        extras += ',\n        "repeat": [%d, %d]' % (1, 1)
                        extras += ',\n        "offset": [%d, %d]' % (0, 0)
                        extras += ',\n        "magFilter": "%s"' % "LinearFilter"
                        extras += ',\n        "minFilter": "%s"' % "LinearMipMapLinearFilter"
                        extras += ',\n        "anisotropy": %d' % 1

                        texture_string = TEMPLATE_TEXTURE % {
                        "texture_id"   : generate_string(texture_id),
                        "texture_file" : generate_string(texture_file),
                        "extras"       : extras
                        }

                        scene_texture_list.append(texture_string)
        else:
            # no layered texture simply get on the property
            texture_count = material_property.GetSrcObjectCount(FbxTexture.ClassId)
            for j in range(texture_count):
                texture = material_property.GetSrcObject(FbxTexture.ClassId,j)
                if texture:
                    texture_file = texture.GetFileName()
                    texture_id = os.path.splitext(os.path.basename(texture_file))[0]
                    wrap_u = texture.GetWrapModeU()
                    wrap_v = texture.GetWrapModeV()
                    offset = texture.GetUVTranslation()
                    
                    #TODO: read extra values from the actual textures
                    extras = ""
                    extras += ',\n        "repeat": [%d, %d]' % (1, 1)
                    extras += ',\n        "offset": [%d, %d]' % (0, 0)
                    extras += ',\n        "magFilter": "%s"' % "LinearFilter"
                    extras += ',\n        "minFilter": "%s"' % "LinearMipMapLinearFilter"
                    extras += ',\n        "anisotropy": %d' % 1

                    texture_string = TEMPLATE_TEXTURE % {
                    "texture_id"   : generate_string(texture_id),
                    "texture_file" : generate_string(texture_file),
                    "extras"       : extras
                    }

                    scene_texture_list.append(texture_string)
                    
def extract_textures_from_node(node, scene_texture_list):
    name = node.GetName()
    mesh = node.GetNodeAttribute()
    
    #for all materials attached to this mesh
    material_count = mesh.GetNode().GetSrcObjectCount(FbxSurfaceMaterial.ClassId)
    for material_index in range(material_count):
        material = mesh.GetNode().GetSrcObject(FbxSurfaceMaterial.ClassId, material_index)

        #go through all the possible textures types
        if material:            
            texture_count = FbxLayerElement.sTypeTextureCount()
            for texture_index in range(texture_count):
                material_property = material.FindProperty(FbxLayerElement.sTextureChannelNames(texture_index))
                extract_material_textures(material_property, material_index, scene_texture_list)

def generate_scene_texture_list_from_hierarchy(node, scene_texture_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        attribute_type = (node.GetNodeAttribute().GetAttributeType())
        if attribute_type == FbxNodeAttribute.eMesh:
            extract_textures_from_node(node, scene_texture_list)
    for i in range(node.GetChildCount()):
        generate_scene_texture_list_from_hierarchy(node.GetChild(i), scene_texture_list)

def generate_scene_texture_list(scene):
    scene_texture_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            generate_scene_texture_list_from_hierarchy(node.GetChild(i), scene_texture_list)
    return scene_texture_list

# #####################################################
# Parse - Lights 
# #####################################################
def extract_light_from_node(node):
    name = node.GetName()
    light = node.GetNodeAttribute()
    light_types = ["point", "directional", "spot", "area", "volume"]
    light_type = light_types[light.LightType.Get()]

    transform = node.EvaluateGlobalTransform()
    position = transform.GetT()

    # TODO:
    #   Add support for light direction
    #   Add support for light target
    light_string = ""
    if light_type == "directional":
        light_string = TEMPLATE_LIGHT_DIRECTIONAL % {
        "light_id"      : generate_string(name),
        "direction"     : generate_vec3([0, 0, 0]),
        "color"         : generate_color(light.Color.Get()),
        "intensity"     : light.Intensity.Get() / 100
        }

    elif light_type == "point":
        light_string = TEMPLATE_LIGHT_POINT % {
        "light_id"      : generate_string(name),
        "position"      : generate_vec3(position),
        "color"         : generate_color(light.Color.Get()),
        "intensity"     : light.Intensity.Get() / 100
        }

    return light_string

def generate_scene_light_list_from_hierarchy(node, scene_light_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        attribute_type = (node.GetNodeAttribute().GetAttributeType())
        if attribute_type == FbxNodeAttribute.eLight:
            scene_light = extract_light_from_node(node)
            scene_light_list.append(scene_light)
    for i in range(node.GetChildCount()):
        generate_scene_light_list_from_hierarchy(node.GetChild(i), scene_light_list)

def generate_scene_light_list(scene):
    scene_light_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            generate_scene_light_list_from_hierarchy(node.GetChild(i), scene_light_list)
    return scene_light_list

# #####################################################
# Parse - Cameras 
# #####################################################
def extract_camera_from_node(node):
    name = node.GetName()
    camera = node.GetNodeAttribute()

    target_node = node.GetTarget()
    target = ""
    if target_node:
        transform = target.EvaluateGlobalTransform()
        target = generate_vec3(transform.GetT())
    else:
        target = generate_vec3(camera.InterestPosition.Get())

    position = generate_vec3(camera.Position.Get())
    aspect = camera.PixelAspectRatio.Get()
    near = camera.NearPlane.Get()
    far = camera.FarPlane.Get()
    fov = camera.FieldOfView.Get()
  
    projection_types = [ "perspective", "orthogonal" ]
    projection = projection_types[camera.ProjectionType.Get()]

    # TODO:
    #   Support more than perspective camera
    #   Get correct fov
    camera_string = ""
    if projection == "perspective":
        camera_string = TEMPLATE_CAMERA_PERSPECTIVE % {
        "camera_id" : generate_string(name),
        "fov"       : fov,
        "aspect"    : aspect,
        "near"      : near,
        "far"       : far,
        "position"  : position,
        "target"    : target
        }
    else:
        camera = DEFAULTS["camera"]
        camera_string = TEMPLATE_CAMERA_ORTHO % {
        "camera_id" : generate_string(camera["name"]),
        "left"      : camera["left"],
        "right"     : camera["right"],
        "top"       : camera["top"],
        "bottom"    : camera["bottom"],
        "near"      : camera["near"],
        "far"       : camera["far"],
        "position"  : generate_vec3(camera["position"]),
        "target"    : generate_vec3(camera["target"])
        }

    return camera_string

def generate_scene_camera_list_from_hierarchy(node, scene_camera_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        attribute_type = (node.GetNodeAttribute().GetAttributeType())
        if attribute_type == FbxNodeAttribute.eCamera:
            scene_camera = extract_camera_from_node(node)
            scene_camera_list.append(scene_camera)
    for i in range(node.GetChildCount()):
        generate_scene_camera_list_from_hierarchy(node.GetChild(i), scene_camera_list)

def generate_scene_camera_list(scene):
    scene_camera_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            generate_scene_camera_list_from_hierarchy(node.GetChild(i), scene_camera_list)
    return scene_camera_list

# #####################################################
# Parse - Default Camera 
# #####################################################
def generate_default_camera():
    camera = DEFAULTS["camera"]
    camera_string = TEMPLATE_CAMERA_PERSPECTIVE % {
    "camera_id" : generate_string(camera["name"]),
    "fov"       : camera["fov"],
    "aspect"    : camera["aspect"],
    "near"      : camera["near"],
    "far"       : camera["far"],
    "position"  : camera["position"],
    "target"    : camera["target"]
    }

    return camera_string

def generate_scene_camera_name_list_from_hierarchy(node, scene_camera_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        attribute_type = (node.GetNodeAttribute().GetAttributeType())
        if attribute_type == FbxNodeAttribute.eCamera:
            scene_camera_list.append(node.GetName())
    for i in range(node.GetChildCount()):
        generate_scene_camera_name_list_from_hierarchy(node.GetChild(i), scene_camera_list)

def generate_scene_camera_name_list(scene):
    scene_camera_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            generate_scene_camera_name_list_from_hierarchy(node.GetChild(i), scene_camera_list)
    return scene_camera_list

# #####################################################
# Parse - Scene 
# #####################################################
def extract_scene(scene, filename):
    geometries = generate_scene_geometry_list(scene)
    embeds = generate_scene_embed_list(scene)
    textures = generate_scene_texture_list(scene)
    materials = generate_scene_material_list(scene)
    objects = generate_scene_object_list(scene)
    cameras = generate_scene_camera_list(scene)
    lights = generate_scene_light_list(scene)
    fogs = []

    camera_names = generate_scene_camera_name_list(scene)
    default_camera = camera_names[0] if len(camera_names) > 0 else "default_camera"
    if len(cameras) <= 0:
        cameras = [generate_default_camera()]

    nobjects = len(objects)
    ngeometries = len(geometries)
    nembeds = len(embeds)
    ntextures = len(textures)
    nmaterials = len(materials)
    ncameras = len(cameras)
    nlights = len(lights)

    basetype = "relativeToScene"

    sections = [
    ["objects",    ",\n".join(objects + cameras + lights)],
    ["geometries", ",\n".join(geometries)],
    ["textures",   ",\n".join(textures)],
    ["fogs",       ",\n".join(fogs)],
    ["materials",  ",\n".join(materials)],
    ["embeds",     ",\n".join(embeds)]
    ]

    chunks = []
    for label, content in sections:
        if content:
            chunks.append(generate_section(label, content))

    sections_string = "\n".join(chunks)

    parameters = {
    "fname": generate_string(filename), 

    "sections"  : sections_string,

    "bgcolor"   : generate_vec3(DEFAULTS["bgcolor"]),
    "bgalpha"   : DEFAULTS["bgalpha"],
    "defcamera" : generate_string(default_camera),
    "fog"    : generate_string(""),

    "nobjects"      : nobjects,
    "ngeometries"   : ngeometries,
    "ntextures"     : ntextures,
    "nmaterials"    : nmaterials,
    "ncameras"      : ncameras,
    "nlights"       : nlights,

    "basetype"      : generate_string(basetype),

    "position"      : generate_vec3(DEFAULTS["position"]),
    "rotation"      : generate_vec3(DEFAULTS["rotation"]),
    "scale"         : generate_vec3(DEFAULTS["scale"])
    }

    text = TEMPLATE_SCENE_ASCII % parameters
    
    return text

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
        print("\n\nLoading file: %s\n" % sys.argv[1])
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
        print("\nExported Three.js file to:\n%s\n" % output_path)

    # Destroy all objects created by the FBX SDK.
    sdk_manager.Destroy()
    sys.exit(0)
