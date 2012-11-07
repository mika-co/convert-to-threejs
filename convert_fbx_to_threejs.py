import os
import sys
import math

# #####################################################
# Configuration
# #####################################################

DEFAULTS = {
"bgcolor" : [0, 0, 0],
"bgalpha" : 1.0,

"position" : [0, 0, 0],
"rotation" : [-math.pi/2, 0, 0],
"scale"    : [1, 1, 1],

"camera"  :
    {
        "name" : "default_camera",
        "type" : "perspective",
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
TEMPLATE_GENERATED_BY = "https://github.com/zfedoran/fbx-to-threejs"

TEMPLATE_SCENE_ASCII = """\
{

"metadata" :
{
    "formatVersion" : 3.1,
    "sourceFile"    : %(fname)s,
    "generatedBy"   : "Blender 2.63 Exporter",
    "objects"       : %(nobjects)s,
    "geometries"    : %(ngeometries)s,
    "materials"     : %(nmaterials)s,
    "textures"      : %(ntextures)s,
    "cameras"       : %(ncameras)s,
    "lights"        : %(nlights)s
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

def generate_section(label, content):
    return TEMPLATE_SECTION % (label, content)

def generate_bool_property(property):
    if property:
        return "true"
    return "false"

def generate_string(s):
    return TEMPLATE_STRING % s

def generate_color(rgb):
    color = (int(rgb[0]*255) << 16) + (int(rgb[1]*255) << 8) + int(rgb[2]*255);
    return color
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
      "metadata" : TEMPLATE_MESH_METADATA % metadata,
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

    return TEMPLATE_MESH % mesh

# #####################################################
# Parse - Objects 
# #####################################################
def extract_mesh_object_from_node(node):
    name = node.GetName()
    transform = node.EvaluateGlobalTransform()
    translation = generate_vec3(transform.GetT())
    scale = generate_vec3(transform.GetS())
    rotation = generate_vec3(transform.GetR())
    rotationq = generate_vec4(transform.GetQ())

    object_info = {
      "object_id": name,
      "geometry_id": "geo_" + name,
      "group_id": "",
      "material_id": "",
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
# Parse - Geometries 
# #####################################################
def extract_geometry_from_node(node):
    name = node.GetName()

    geometry_info = {
      "geometry_id": generate_string("geo_" + name),
      "embed_id":  generate_string("emb_" + name),
    }

    return TEMPLATE_GEOMETRY_EMBED % geometry_info

def extract_scene_geometry_list_from_hierarchy(node, scene_geometry_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        lAttributeType = (node.GetNodeAttribute().GetAttributeType())
        if lAttributeType == FbxNodeAttribute.eMesh:
            scene_geometry = extract_geometry_from_node(node)
            scene_geometry_list.append(scene_geometry)
    for i in range(node.GetChildCount()):
        extract_scene_geometry_list_from_hierarchy(node.GetChild(i), scene_geometry_list)

def extract_scene_geometry_list_from_scene(scene):
    scene_geometry_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            extract_scene_geometry_list_from_hierarchy(node.GetChild(i), scene_geometry_list)
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

def extract_scene_embed_list_from_hierarchy(node, scene_embed_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        lAttributeType = (node.GetNodeAttribute().GetAttributeType())
        if lAttributeType == FbxNodeAttribute.eMesh:
            scene_embed = extract_embed_from_node(node)
            scene_embed_list.append(scene_embed)
    for i in range(node.GetChildCount()):
        extract_scene_embed_list_from_hierarchy(node.GetChild(i), scene_embed_list)

def extract_scene_embed_list_from_scene(scene):
    scene_embed_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            extract_scene_embed_list_from_hierarchy(node.GetChild(i), scene_embed_list)
    return scene_embed_list

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
    #   Support light direction
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

def extract_scene_light_list_from_hierarchy(node, scene_light_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        lAttributeType = (node.GetNodeAttribute().GetAttributeType())
        if lAttributeType == FbxNodeAttribute.eLight:
            scene_light = extract_light_from_node(node)
            scene_light_list.append(scene_light)
    for i in range(node.GetChildCount()):
        extract_scene_light_list_from_hierarchy(node.GetChild(i), scene_light_list)

def extract_scene_light_list_from_scene(scene):
    scene_light_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            extract_scene_light_list_from_hierarchy(node.GetChild(i), scene_light_list)
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

def extract_scene_camera_list_from_hierarchy(node, scene_camera_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        lAttributeType = (node.GetNodeAttribute().GetAttributeType())
        if lAttributeType == FbxNodeAttribute.eCamera:
            scene_camera = extract_camera_from_node(node)
            scene_camera_list.append(scene_camera)
    for i in range(node.GetChildCount()):
        extract_scene_camera_list_from_hierarchy(node.GetChild(i), scene_camera_list)

def extract_scene_camera_list_from_scene(scene):
    scene_camera_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            extract_scene_camera_list_from_hierarchy(node.GetChild(i), scene_camera_list)
    return scene_camera_list

# #####################################################
# Parse - Scene 
# #####################################################
def extract_scene(scene, filename):
    objects = extract_scene_object_list_from_scene(scene)
    geometries = extract_scene_geometry_list_from_scene(scene)
    embeds = extract_scene_embed_list_from_scene(scene)
    textures = []
    materials = []
    cameras = extract_scene_camera_list_from_scene(scene)
    lights = extract_scene_light_list_from_scene(scene)

    nobjects = len(objects)
    ngeometries = len(geometries)
    nembeds = len(embeds)
    ntextures = len(textures)
    nmaterials = len(materials)
    ncameras = len(cameras)
    nlights = len(lights)

    basetype = "relativeToScene"

    sections = [
    ["objects",    ",\n".join(objects)],
    ["geometries", ",\n".join(geometries)],
    ["textures",   ",\n".join(textures)],
    ["materials",  ",\n".join(materials)],
    ["cameras",    ",\n".join(cameras)],
    ["lights",     ",\n".join(lights)],
    ["embeds",     ",\n".join(embeds)]
    ]

    chunks = []
    for label, content in sections:
        if content:
            chunks.append(generate_section(label, content))

    sections_string = "\n".join(chunks)

    default_camera = "default_camera"
    
    parameters = {
    "fname": generate_string(filename), 

    "sections"  : sections_string,

    "bgcolor"   : generate_vec3(DEFAULTS["bgcolor"]),
    "bgalpha"   : DEFAULTS["bgalpha"],
    "defcamera" :  generate_string(default_camera),

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
