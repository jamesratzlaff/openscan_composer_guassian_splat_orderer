import bpy
import bmesh
from pathlib import Path
import os


osc_vis_dir=os.path.join(Path.home(),"git","openscan_composer_guassian_splat_orderer") #change this to wherever the openscan_composer_blender_vis.py exists
fname="openscan_composer_blender_vis.py"
filepath=os.path.join(osc_vis_dir,fname)

exec(compile(open(filepath).read(), filepath, 'exec'))

min_angle=-30
max_angle=120
num_captures=360
interval=5

#example: this draws the vertices that represent a capture point, 

#get the mapped_coordinate objects representing capture positions in openscan_composer and will be shown as vertices in blender
mapped_coords=cap_resolver.capture_number_to_turntable_and_rotor_angle(min_angle,max_angle,num_captures)
#gets every 5th (assigned by the interval variable) capture position/vertex for all vertices in the mapped_coords to be drawn as a "path" represented as a line segment
selecteds = cap_resolver.mapped_coordinate.select_every_x_item_all(mapped_coords,interval)
#gets segmented capture positions so we can visualize how each "path" looks
segments = cap_resolver.mapped_coordinate.select_every_x_item_segments(mapped_coords,interval)
#create all of the edges/paths
edges = cap_resolver.mapped_coordinate.as_edge_pairs(selecteds)
#update the geomentry
update_geom(np.asarray(list(map(lambda mc:mc.as_vector_coord(),mapped_coords))),edges,[])
#highlight the individual path
path_to_visualize=2
select_vertices(list(map(lambda seg:seg.index(),segments[path_to_visualize])))