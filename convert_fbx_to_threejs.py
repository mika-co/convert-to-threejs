import os
import sys
import math

# #####################################################
# Templates
# #####################################################
def Vector2String(v):
    return '[ %g, %g ]' % (v[0], v[1])

def Vector3String(v):
    return '[ %g, %g, %g ]' % (v[0], v[1], v[2])

def ColorString(c):
    return '[ %g, %g, %g ]' % (c[0], c[1], c[2])

def LabelString(s):
    return '"%s"' % s

def ArrayString(s):
    return '[ %s ]' % s

def PaddingString(n):
    output = ""
    for i in range(n):
        output += "\t"
    return output
        
def BoolString(value):
    if value:
        return "true"
    return "false"

# #####################################################
# Helpers
# #####################################################
def getObjectName(o): 
    if not o:
        return ""  
    return "Object_" + o.GetName()
      
def getGeometryName(g):
    return "Geometry_" + g.GetName()

def getEmbedName(e):
    return "Embed_" + e.GetName()

def getMaterialName(m):
    return "Material_" + m.GetName()

def getTextureName(t):
    texture_file = t.GetFileName()
    texture_id = os.path.splitext(os.path.basename(texture_file))[0]
    return "Texture_" + texture_id

def getFogName(f):
    return "Fog_" + f.GetName()

def getObjectVisible(n):
    return BoolString(True)
    
def getRadians(v):
    return (v[0]/180, v[1]/180, v[2]/180)

def getHex(c):
    color = (int(c[0]*255) << 16) + (int(c[1]*255) << 8) + int(c[2]*255)
    return color

def generateMultiLineString(lines, separator, padding):
    cleanLines = []
    for i in range(len(lines)):
        line = lines[i]
        line = PaddingString(padding) + line
        cleanLines.append(line)
    return separator.join(cleanLines)
		
# #####################################################
# Generate - Material String 
# #####################################################
def generate_texture_bindings(material_property, texture_list):
    binding_types = {
    "DiffuseColor": "map", "DiffuseFactor": "diffuseFactor", "EmissiveColor": "emissiveMap", 
    "EmissiveFactor": "emissiveFactor", "AmbientColor": "ambientMap", "AmbientFactor": "ambientFactor", 
    "SpecularColor": "specularMap", "SpecularFactor": "specularFactor", "ShininessExponent": "shininessExponent",
    "NormalMap": "normalMap", "Bump": "bumpMap", "TransparentColor": "transparentMap", 
    "TransparencyFactor": "transparentFactor", "ReflectionColor": "reflectionMap", 
    "ReflectionFactor": "reflectionFactor", "DisplacementColor": "displacementMap", 
    "VectorDisplacementColor": "vectorDisplacementMap"
    }

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
                        texture_id = getTextureName(texture) 
                        texture_binding = '		"%s": "%s",' % (binding_types[str(material_property.GetName())], texture_id)
                        texture_list.append(texture_binding)
        else:
            # no layered texture simply get on the property
            texture_count = material_property.GetSrcObjectCount(FbxTexture.ClassId)
            for j in range(texture_count):
                texture = material_property.GetSrcObject(FbxTexture.ClassId,j)
                if texture:
                    texture_id = getTextureName(texture) 
                    texture_binding = '		"%s": "%s",' % (binding_types[str(material_property.GetName())], texture_id)
                    texture_list.append(texture_binding)

def generate_material_string(material):
    #Get the implementation to see if it's a hardware shader.
    implementation = GetImplementation(material, "ImplementationHLSL")
    implementation_type = "HLSL"
    if not implementation:
        implementation = GetImplementation(material, "ImplementationCGFX")
        implementation_type = "CGFX"

    output = []

    if implementation:
        # This material is a hardware shader, skip it
        print("Shader materials are not supported")
        return ''
        
    elif material.GetClassId().Is(FbxSurfaceLambert.ClassId):

        ambient   = str(getHex(material.Ambient.Get()))
        diffuse   = str(getHex(material.Diffuse.Get()))
        emissive  = str(getHex(material.Emissive.Get()))
        opacity   = str(1.0 - material.TransparencyFactor.Get())
        transparent = BoolString(False)
        reflectivity = "1"

        output = [

        '\t' + LabelString( getMaterialName( material ) ) + ': {',
        '	"type"    : "MeshLambertMaterial",',
        '	"parameters"  : {',
        '		"color"  : ' 	  + diffuse + ',',
        '		"ambient"  : ' 	+ ambient + ',',
        '		"emissive"  : ' + emissive + ',',
        '		"reflectivity"  : ' + reflectivity + ',',
        '		"transparent" : '   + transparent + ',',
        '		"opacity" : ' 	    + opacity + ',',

        ]

    elif material.GetClassId().Is(FbxSurfacePhong.ClassId):

        ambient   = str(getHex(material.Ambient.Get()))
        diffuse   = str(getHex(material.Diffuse.Get()))
        emissive  = str(getHex(material.Emissive.Get()))
        specular  = str(getHex(material.Specular.Get()))
        opacity   = str(1.0 - material.TransparencyFactor.Get())
        shininess = str(material.Shininess.Get())
        transparent = BoolString(False)
        reflectivity = "1"
        bumpScale = "1"

        output = [

        '\t' + LabelString( getMaterialName( material ) ) + ': {',
        '	"type"    : "MeshPhongMaterial",',
        '	"parameters"  : {',
        '		"color"  : ' 	  + diffuse + ',',
        '		"ambient"  : ' 	+ ambient + ',',
        '		"emissive"  : ' + emissive + ',',
        '		"specular"  : ' + specular + ',',
        '		"shininess" : ' + shininess + ',',
        '		"bumpScale"  : '    + bumpScale + ',',
        '		"reflectivity"  : ' + reflectivity + ',',
        '		"transparent" : '   + transparent + ',',
        '		"opacity" : ' 	+ opacity + ',',

        ]

    else:
      print("Unknown type of Material")
      return ''

    texture_list = []
    texture_count = FbxLayerElement.sTypeTextureCount()
    for texture_index in range(texture_count):
        material_property = material.FindProperty(FbxLayerElement.sTextureChannelNames(texture_index))
        generate_texture_bindings(material_property, texture_list)

    output += texture_list

    wireframe = BoolString(False)
    wireframeLinewidth = "1"

    output.append('		"wireframe" : ' + wireframe + ',')
    output.append('		"wireframeLinewidth" : ' + wireframeLinewidth)
    output.append('	}')
    output.append('}')

    return generateMultiLineString( output, '\n\t\t', 0 )

# #####################################################
# Parse - Materials 
# #####################################################
def extract_materials_from_node(node, material_list):
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
                material_list.append(scene_material)

def generate_materials_from_hierarchy(node, material_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        attribute_type = (node.GetNodeAttribute().GetAttributeType())
        if attribute_type == FbxNodeAttribute.eMesh:
            extract_materials_from_node(node, material_list)
    for i in range(node.GetChildCount()):
        generate_materials_from_hierarchy(node.GetChild(i), material_list)

def generate_material_list(scene):
    material_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            generate_materials_from_hierarchy(node.GetChild(i), material_list)
    return material_list

# #####################################################
# Generate - Texture String 
# #####################################################
def generate_texture_string(texture):

    wrap_u = texture.GetWrapModeU()
    wrap_v = texture.GetWrapModeV()
    offset = texture.GetUVTranslation()

    output = [

    '\t' + LabelString( getTextureName( texture ) ) + ': {',
    '	"url"    : "' + texture.GetFileName() + '",',
    '	"repeat" : ' + Vector2String( (1,1) ) + ',',
    '	"offset" : ' + Vector2String( texture.GetUVTranslation() ) + ',',
    '	"magFilter" : ' + LabelString( "LinearFilter" ) + ',',
    '	"minFilter" : ' + LabelString( "LinearMipMapLinearFilter" ) + ',',
    '	"anisotropy" : ' + BoolString( True ),
    '}'

    ]

    return generateMultiLineString( output, '\n\t\t', 0 )

# #####################################################
# Parse - Textures 
# #####################################################
def extract_material_textures(material_property, texture_list):
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
                        texture_string = generate_texture_string(texture)
                        texture_list.append(texture_string)
        else:
            # no layered texture simply get on the property
            texture_count = material_property.GetSrcObjectCount(FbxTexture.ClassId)
            for j in range(texture_count):
                texture = material_property.GetSrcObject(FbxTexture.ClassId,j)
                if texture:
                    texture_string = generate_texture_string(texture)
                    texture_list.append(texture_string)
	
def extract_textures_from_node(node, texture_list):
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
                extract_material_textures(material_property, texture_list)

def generate_textures_from_hierarchy(node, texture_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        attribute_type = (node.GetNodeAttribute().GetAttributeType())
        if attribute_type == FbxNodeAttribute.eMesh:
            extract_textures_from_node(node, texture_list)
    for i in range(node.GetChildCount()):
        generate_textures_from_hierarchy(node.GetChild(i), texture_list)

def generate_texture_list(scene):
    texture_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            generate_textures_from_hierarchy(node.GetChild(i), texture_list)
    return texture_list

# #####################################################
# Generate - Mesh String 
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
    
def join_vec2(v):
    return "%g,%g" % (v[0], v[1])

def join_vec3(v):
    return "%g,%g,%g" % (v[0], v[1], v[2])

def generate_uv(uv):
    return "%g,%g" % (uv[0], uv[1])

def generate_uvs(uv_layers):
    layers = []
    for uvs in uv_layers:
        layer = ",".join(generate_uv(n) for n in uvs)
        layers.append(layer)

    return ",".join("[%s]" % n for n in layers)

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

def generate_mesh_string(node):
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

    nmaterials = len(materials)
    nvertices = len(vertices)
    nnormals = len(normal_values)
    ncolors = len(color_values)
    nfaces = len(faces)
    nuvs = ",".join(nuvs)

    vertices = ",".join(join_vec3(v) for v in vertices)
    normals  = ",".join(join_vec3(v) for v in normal_values)
    colors   = ",".join(join_vec3(v) for v in color_values)
    faces    = ",".join(faces)
    uvs      = generate_uvs(uv_values)

    output = [
    '\t' + LabelString( getEmbedName( node ) ) + ' : {',
    '	"metadata"  : {',
    '		"vertices" : ' + str(nvertices) + ',',
    '		"normals" : ' + str(nnormals) + ',',
    '		"colors" : ' + str(ncolors) + ',',
    '		"faces" : ' + str(nfaces) + ',',
    '		"uvs" : ' + ArrayString(nuvs) + ',',
    '	},',
    '	"scale" : ' + str( 1 ) + ',',   
    '	"vertices" : ' + ArrayString(vertices) + ',',   
    '	"normals" : ' + ArrayString(normals) + ',',   
    '	"colors" : ' + ArrayString(colors) + ',',   
    '	"uvs" : ' + ArrayString(uvs) + ',',   
    '	"faces" : ' + ArrayString(faces),
    '}'
    ]

    return generateMultiLineString( output, '\n\t\t', 0 )

# #####################################################
# Generate - Embeds 
# #####################################################
def generate_embed_list_from_hierarchy(node, embed_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        attribute_type = (node.GetNodeAttribute().GetAttributeType())
        if attribute_type == FbxNodeAttribute.eMesh:
            embed_string = generate_mesh_string(node)
            embed_list.append(embed_string)
    for i in range(node.GetChildCount()):
        generate_embed_list_from_hierarchy(node.GetChild(i), embed_list)

def generate_embed_list(scene):
    embed_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            generate_embed_list_from_hierarchy(node.GetChild(i), embed_list)
    return embed_list

# #####################################################
# Generate - Geometries 
# #####################################################
def generate_geometry_string(node):

    output = [
    '\t' + LabelString( getGeometryName( node ) ) + ' : {',
    '	"type"  : "embedded",',
    '	"id" : ' + LabelString( getEmbedName( node ) ),
    '}'
    ]

    return generateMultiLineString( output, '\n\t\t', 0 )

def generate_geometry_list_from_hierarchy(node, geometry_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        attribute_type = (node.GetNodeAttribute().GetAttributeType())
        if attribute_type == FbxNodeAttribute.eMesh:
            geometry_string = generate_geometry_string(node)
            geometry_list.append(geometry_string)
    for i in range(node.GetChildCount()):
        generate_geometry_list_from_hierarchy(node.GetChild(i), geometry_list)

def generate_geometry_list(scene):
    geometry_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            generate_geometry_list_from_hierarchy(node.GetChild(i), geometry_list)
    return geometry_list

# #####################################################
# Generate - Camera Names
# #####################################################
def generate_camera_name_list_from_hierarchy(node, camera_list):
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        attribute_type = (node.GetNodeAttribute().GetAttributeType())
        if attribute_type == FbxNodeAttribute.eCamera:
            camera_string = getObjectName(node) 
            camera_list.append(camera_string)
    for i in range(node.GetChildCount()):
        generate_camera_name_list_from_hierarchy(node.GetChild(i), camera_list)

def generate_camera_name_list(scene):
    camera_list = []
    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            generate_camera_name_list_from_hierarchy(node.GetChild(i), camera_list)
    return camera_list

# #####################################################
# Generate - Light Object 
# #####################################################
def generate_light_string(node, padding):
    light = node.GetNodeAttribute()
    light_types = ["point", "directional", "spot", "area", "volume"]
    light_type = light_types[light.LightType.Get()]

    transform = node.EvaluateGlobalTransform()
    position = transform.GetT()

    output = []

    if light_type == "directional":

				output = [

				'\t\t' + LabelString( getObjectName( node ) ) + ' : {',
				'	"type"      : "DirectionalLight",',
				'	"color"     : ' + str(getHex(light.Color.Get())) + ',',
				'	"intensity" : ' + str(light.Intensity.Get()) + ',',
				'	"direction" : ' + Vector3String( position ) + ',',
				'	"target"    : ' + LabelString( getObjectName( node.GetTarget() ) ) + ( ',' if node.GetChildCount() > 0 else '' )

				]

    elif light_type == "point":

				output = [

				'\t\t' + LabelString( getObjectName( node ) ) + ' : {',
				'	"type"      : "PointLight",',
				'	"color"     : ' + str(getHex(light.Color.Get())) + ',',
				'	"intensity" : ' + str(light.Intensity.Get()) + ',',
				'	"position"  : ' + Vector3String( position ) + ',',
				'	"distance"  : ' + str(light.FarAttenuationEnd.Get()) + ( ',' if node.GetChildCount() > 0 else '' )

				]

    elif light_type == "spot":

				output = [

				'\t\t' + LabelString( getObjectName( node ) ) + ' : {',
				'	"type"      : "SpotLight",',
				'	"color"     : ' + str(getHex(light.Color.Get())) + ',',
				'	"intensity" : ' + str(light.Intensity.Get()) + ',',
				'	"position"  : ' + Vector3String( position ) + ',',
				'	"distance"  : ' + str(light.FarAttenuationEnd.Get()) + ',',
				'	"angle"     : ' + str(light.OuterAngle.Get()) + ',',
				'	"exponent"  : ' + str(light.DecayType.Get()) + ',',
				'	"target"    : ' + LabelString( getObjectName( node.GetTarget() ) ) + ( ',' if node.GetChildCount() > 0 else '' )

				]

    return generateMultiLineString( output, '\n\t\t', padding )

def generate_ambient_light_string(scene):

    scene_settings = scene.GetGlobalSettings()
    ambient_color = scene_settings.GetAmbientColor()
    ambient_color = (ambient_color.mRed, ambient_color.mGreen, ambient_color.mBlue)

    if ambient_color[0] == 0 and ambient_color[1] == 0 and ambient_color[2] == 0:
        return None

    class AmbientLight:
        def GetName(self):
            return "AmbientLight"

    node = AmbientLight()

    output = [

    '\t\t' + LabelString( getObjectName( node ) ) + ' : {',
    '	"type"  : "AmbientLight",',
    '	"color" : ' + str(getHex(ambient_color)),
    '}'

    ]

    return generateMultiLineString( output, '\n\t\t', 0 )
    
# #####################################################
# Generate - Camera Object 
# #####################################################
def generate_camera_string(node, padding):
    camera = node.GetNodeAttribute()

    target_node = node.GetTarget()
    target = ""
    if target_node:
        transform = target.EvaluateGlobalTransform()
        target = transform.GetT()
    else:
        target = camera.InterestPosition.Get()

    position = camera.Position.Get()
  
    projection_types = [ "perspective", "orthogonal" ]
    projection = projection_types[camera.ProjectionType.Get()]

    near = camera.NearPlane.Get()
    far = camera.FarPlane.Get()

    output = []

    if projection == "perspective":

        aspect = camera.PixelAspectRatio.Get()
        fov = camera.FieldOfView.Get()

        output = [

        '\t\t' + LabelString( getObjectName( node ) ) + ' : {',
        '	"type"     : "PerspectiveCamera",',
        '	"fov"      : ' + str(fov) + ',',
        '	"aspect"   : ' + str(aspect) + ',',
        '	"near"     : ' + str(near) + ',',
        '	"far"      : ' + str(far) + ',',
        '	"position" : ' + Vector3String( position ) + ( ',' if node.GetChildCount() > 0 else '' )

        ]

    elif projection == "orthogonal":

        left = ""
        right = ""
        top = ""
        bottom = ""

        output = [

        '\t\t' + LabelString( getObjectName( node ) ) + ' : {',
        '	"type"     : "OrthographicCamera",',
        '	"left"     : ' + left + ',',
        '	"right"    : ' + right + ',',
        '	"top"      : ' + top + ',',
        '	"bottom"   : ' + bottom + ',',
        '	"near"     : ' + str(near) + ',',
        '	"far"      : ' + str(far) + ',',
        '	"position" : ' + Vector3String( position ) + ( ',' if node.GetChildCount() > 0 else '' )

        ]

    return generateMultiLineString( output, '\n\t\t', padding )

# #####################################################
# Generate - Mesh Object 
# #####################################################
def generate_mesh_object_string(node, padding):
    mesh = node.GetNodeAttribute()
    transform = node.EvaluateGlobalTransform()
    position = transform.GetT()
    scale = transform.GetS()
    rotation = getRadians(transform.GetR())

    output = [

    '\t\t' + LabelString( getObjectName( node ) ) + ' : {',
    '	"geometry" : ' + LabelString( getGeometryName( node ) ) + ',',
    '	"material" : ' + LabelString( getMaterialName( node ) ) + ',',
    '	"position" : ' + Vector3String( position ) + ',',
    '	"rotation" : ' + Vector3String( rotation ) + ',',
    '	"scale"	   : ' + Vector3String( scale ) + ',',
    '	"visible"  : ' + getObjectVisible( node ) + ( ',' if node.GetChildCount() > 0 else '' )

    ]

    return generateMultiLineString( output, '\n\t\t', padding )

# #####################################################
# Generate - Object 
# #####################################################
def generate_object_string(node, padding):
    node_types = ["Unknown", "Null", "Marker", "Skeleton", "Mesh", "Nurbs", "Patch", "Camera", 
    "CameraStereo", "CameraSwitcher", "Light", "OpticalReference", "OpticalMarker", "NurbsCurve", 
    "TrimNurbsSurface", "Boundary", "NurbsSurface", "Shape", "LODGroup", "SubDiv", "CachedEffect", "Line"]

    transform = node.EvaluateGlobalTransform()
    position = transform.GetT()
    scale = transform.GetS()
    rotation = getRadians(transform.GetR())

    output = [

    '\t\t' + LabelString( getObjectName( node ) ) + ' : {',
    '	"fbx_type" : ' + LabelString( node_types[node.GetNodeAttribute().GetAttributeType()] ) + ',',
    '	"position" : ' + Vector3String( position ) + ',',
    '	"rotation" : ' + Vector3String( rotation ) + ',',
    '	"scale"	   : ' + Vector3String( scale ) + ',',
    '	"visible"  : ' + getObjectVisible( node ) + ( ',' if node.GetChildCount() > 0 else '' )

    ]

    return generateMultiLineString( output, '\n\t\t', padding )

# #####################################################
# Parse - Objects 
# #####################################################
def generate_object_hierarchy(node, object_list, pad, siblings_left):
    object_count = 0
    if node.GetNodeAttribute() == None:
        print("NULL Node Attribute\n")
    else:
        attribute_type = (node.GetNodeAttribute().GetAttributeType())
        if attribute_type == FbxNodeAttribute.eMesh:
            object_string = generate_mesh_object_string(node, pad)
            object_list.append(object_string)
            object_count += 1
        elif attribute_type == FbxNodeAttribute.eLight:
            object_string = generate_light_string(node, pad)
            object_list.append(object_string)
            object_count += 1
        elif attribute_type == FbxNodeAttribute.eCamera:
            object_string = generate_camera_string(node, pad)
            object_list.append(object_string)
            object_count += 1
        else:
            object_string = generate_object_string(node, pad)
            object_list.append(object_string)
            object_count += 1

    if node.GetChildCount() > 0:
      object_list.append( PaddingString( pad + 1 ) + '\t\t"children" : {\n' )

      for i in range(node.GetChildCount()):
          object_count += generate_object_hierarchy(node.GetChild(i), object_list, pad + 2, node.GetChildCount() - i - 1)

      object_list.append( PaddingString( pad + 1 ) + '\t\t}' )
    object_list.append( PaddingString( pad ) + '\t\t}' + (',\n' if siblings_left > 0 else ''))

    return object_count

def generate_scene_objects_string(scene):
    object_count = 0
    object_list = []

    ambient_light = generate_ambient_light_string(scene)
    if ambient_light:
        if scene.GetNodeCount() > 0:
            ambient_light += (',\n')
        object_list.append(ambient_light)
        object_count += 1

    node = scene.GetRootNode()
    if node:
        for i in range(node.GetChildCount()):
            object_count += generate_object_hierarchy(node.GetChild(i), object_list, 0, node.GetChildCount() - i - 1)

    return "\n".join(object_list), object_count

# #####################################################
# Parse - Scene 
# #####################################################
def extract_scene(scene, filename):
    objects, nobjects = generate_scene_objects_string(scene)

    textures = generate_texture_list(scene)
    materials = generate_material_list(scene)
    geometries = generate_geometry_list(scene)
    embeds = generate_embed_list(scene)
    fogs = []

    ntextures = len(textures)
    nmaterials = len(materials)
    ngeometries = len(geometries)

    position = Vector3String( (0,0,0) )
    rotation = Vector3String( (0,0,0) )
    scale    = Vector3String( (1,1,1) )

    camera_names = generate_camera_name_list(scene)
    scene_settings = scene.GetGlobalSettings()

    bgcolor = 0
    bgalpha = 0
    defcamera = LabelString(camera_names[0] if len(camera_names) > 0 else "")
    deffog = LabelString("")

    geometries = generateMultiLineString( geometries, ",\n\n\t", 0 )
    materials = generateMultiLineString( materials, ",\n\n\t", 0 )
    textures = generateMultiLineString( textures, ",\n\n\t", 0 )
    embeds = generateMultiLineString( embeds, ",\n\n\t", 0 )
    fogs = generateMultiLineString( fogs, ",\n\n\t", 0 )

    output = [
			'{',
			'	"metadata": {',
			'		"formatVersion" : 3.2,',
			'		"type"		: "scene",',
			'		"generatedBy"	: "https://github.com/zfedoran/fbx-to-threejs",',
			'		"objects"       : ' + str(nobjects) + ',',
			'		"geometries"    : ' + str(ngeometries) + ',',
			'		"materials"     : ' + str(nmaterials) + ',',
			'		"textures"      : ' + str(ntextures),
			'	},',

			'',
			'	"urlBaseType": "relativeToScene",',
			'',

			'	"objects" :',
			'	{',
			objects,
			'	},',
			'',

			'	"geometries" :',
			'	{',
			'\t' + 	geometries,
			'	},',
			'',

			'	"materials" :',
			'	{',
			'\t' + 	materials,
			'	},',
			'',

			'	"textures" :',
			'	{',
			'\t' + 	textures,
			'	},',
			'',

			'	"embeds" :',
			'	{',
			'\t' + 	embeds,
			'	},',
			'',

			'	"fogs" :',
			'	{',
			'\t' + 	fogs,
			'	},',
			'',

			'	"transform" :',
			'	{',
			'		"position"  : ' + position + ',',
			'		"rotation"  : ' + rotation + ',',
			'		"scale"     : ' + scale,
			'	},',
			'',

			'	"defaults" :',
			'	{',
			'		"bgcolor" : ' + str(bgcolor) + ',',
			'		"bgalpha" : ' + str(bgalpha) + ',',
			'		"camera"  : ' + defcamera + ',',
			'		"fog"  	  : ' + deffog,
			'	}',
			'}'
		]

    return "\n".join(output)

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
