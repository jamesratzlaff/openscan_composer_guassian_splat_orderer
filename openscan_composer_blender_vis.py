import importlib.util
import bpy
import bmesh
import importlib
import math
import numpy as np
import sys
from pathlib import Path
import os

osc_vis_dir=os.path.join(Path.home(),"git","openscan_composer_guassian_splat_orderer") #change this to wherever the openscan_composer_blender_vis.py exists

sys.path.insert(1, osc_vis_dir)
import rotor_and_turntable_angle_capture_resolver as cap_resolver

importlib.reload(cap_resolver)


collection_name="new_collection"
object_name="new_object"
mesh_name="new_mesh"

def get_collection(name=collection_name):
    if name not in bpy.data.collections:
        coll=bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return bpy.data.collections[name]

def get_mesh(name=mesh_name):
    if name not in bpy.data.meshes:
        bpy.data.meshes.new(name)
    return bpy.data.meshes[name]        

def get_object(name=object_name,m_name=mesh_name,coll_name=collection_name):
    if name not in bpy.data.objects:
        obj=bpy.data.objects.new(name, get_mesh(m_name))
        get_collection(coll_name).objects.link(obj)
    return bpy.data.objects[name]

def do_setup_and_return_mesh(name=mesh_name,obj_name=object_name,coll_name=collection_name):
    bpy.ops.object.mode_set(mode = 'OBJECT')
    coll=get_collection(coll_name)
    mesh=get_mesh(name)
    obj=get_object(obj_name,mesh.name,coll.name)
    return mesh

def update_geom(verts=[],edges=[],faces=[],name=mesh_name):
    mesh=do_setup_and_return_mesh(name)
    if verts is None or len(verts) == 0:
        verts=np.asarray(map(lambda v:v.co,mesh.vertices))
    mesh.clear_geometry()
    mesh.from_pydata(verts, edges, faces)
    mesh.update()

def select_vertices(vertices=[],name=mesh_name):
    bpy.ops.object.mode_set(mode = 'OBJECT')
    obj = get_object(name)
    bpy.ops.object.mode_set(mode = 'EDIT') 
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')
    for v in vertices:
        obj.data.vertices[v].select = True    
    bpy.ops.object.mode_set(mode = 'EDIT') 
    

def select_bmesh_vertices(name,vertex_nos):
    context = bpy.context
    ob = get_object(name)
    me = ob.data
    bpy.ops.object.mode_set(mode = 'EDIT')
    bm = bmesh.from_edit_mesh(me)
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bm.verts.ensure_lookup_table()
    for i in vertex_nos:
        bm.verts[i].select_set(True)
    bm.select_mode |= {'VERT'}
    bm.select_flush_mode()
    bmesh.update_edit_mesh(me)

mapped_coords=[]

def draw_mapped_coords(m_coords=mapped_coords,name=mesh_name):
    l=np.asarray(list(map(lambda mc:mc.as_vector_coord(),m_coords)))
    update_geom(l,[],[],name)
    return mapped_coords

def draw_capture_points(min_angle,max_angle,num_captures,name=mesh_name):
    mapped_coords=cap_resolver.capture_number_to_turntable_and_rotor_angle(min_angle,max_angle,num_captures)
    draw_mapped_coords(mapped_coords,name)
    return mapped_coords
