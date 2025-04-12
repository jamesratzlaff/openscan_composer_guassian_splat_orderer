import math
import numpy as np
import typing


class Coordinate:
    def __init__(self, rotor_angle:float,turntable_angle:float):
        self.rotor_angle=rotor_angle
        self.turntable_angle=turntable_angle
        radius = float(5)
        inverse_radians = math.pi / 180.0
        pitch = math.radians(self.rotor_angle)
        yaw = math.radians(self.turntable_angle)
        num5 = math.cos( self.turntable_angle*inverse_radians)
        num6 = math.sin( self.turntable_angle*inverse_radians)
        num7 = math.cos((90.0 - self.rotor_angle*inverse_radians))
        num8 = math.sin((90.0 - self.rotor_angle*inverse_radians))
        x_old=num5*num8*radius
        y_old=num6*num8*radius
        z_old=num7*radius
        x=math.cos(yaw)*math.cos(pitch)*radius#num5*num8*radius
        y=math.sin(yaw)*math.cos(pitch)*radius#num7*radius
        z=math.sin(pitch)*radius#num6*num8*radius
        self.vectorCoords=(x,y,z)
        self.old_vectorCoords=(x_old,y_old,z_old)
    

    def distance(self,other):
        return self.distance_vec(other.vectorCoords)

    def distance_vec(self, vec):
        return math.dist(self.vectorCoords,vec)
    
    def is_clockwise_to(self,other):
        return self.turntable_angle-other.turntable_angle>=0
    
    def is_counter_clockwise_to(self,other):
        return not self.is_clockwise_to(other)

    def _cmp_rotor_angle(self,other):
        if self.rotor_angle == other.rotor_angle:
            return 0
        if self.rotor_angle < other.rotor_angle:
            cmp = -1
        else:
            cmp = 1
        return cmp
    
    def _cmp_turntable_angle(self,other):
        if self.turntable_angle == other.turntable_angle:
            return 0
        if self.turntable_angle < other.turntable_angle:
            return -1
        else:
            return 1
    
    def _cmp(self,other):
        if not isinstance(other, Coordinate):
            return -1
        if self == other:
            return 0
        cmp = self._cmp_rotor_angle(other)
        if cmp == 0:
            cmp = self._cmp_turntable_angle(other)
        return cmp
    
    @staticmethod
    def cmp(me,other):
        return me._cmp(other)
        
    def __lt__(self, other):
        cmp = self._cmp(other)
        return cmp<0
    
    def __gt__(self,other):
        cmp = self._cmp(other)
        return cmp>0
    
    def __le__(self,other):
        cmp = self._cmp(other)
        return cmp<=0
    
    def __ge__(self,other):
        cmp = self._cmp(other)
        return cmp>=0
        
    def __eq__(self, other):
        if isinstance(other, Coordinate):
            return self.rotor_angle == other.rotor_angle and self.turntable_angle == other.turntable_angle
        else:
            return False
        
    def __repr__(self):
        rotar_str = "{:.2f}".format(self.rotor_angle)
        turntable_str = "{:.2f}".format(self.turntable_angle)
        return "{r: "+rotar_str+", t: "+turntable_str+", x,y,z: "+str(self.vectorCoords)+"}"
        
class mapped_coordinate:
    def __init__(self,capture_num:int, r:float|Coordinate,t:float):
        self.capture_num=capture_num
        if not isinstance(r, Coordinate):
            r=Coordinate(r,t)
        self.coordinate = r
        self.visited=False
        self.next=None

    def index(self):
        return self.capture_num-1

    def as_vector_coord(self):
        return self.coordinate.vectorCoords


    def visit(self):
        self.visited=True
        return self

    def __repr__(self):
        strRep= str(self.capture_num)+" => "+repr(self.coordinate)
        if self.next is not None:
            strRep += "->"+str(self.next.capture_num)
        return strRep
    
    def __eq__(self,other):
         if isinstance(other, mapped_coordinate):
             return self.capture_num == other.capture_num and self.coordinate == other.coordinate
         return False
    
    def __lt__(self, other):
        return self.coordinate < other.coordinate
    
    def __gt__(self,other):
        return self.coordinate > other.coordinate
    
    def __le__(self, other):
        return self.coordinate <= other.coordinate
    
    def __ge__(self,other):
        return self.coordinate >= other.coordinate
    
    def distance(self,other):
        return self.coordinate.distance(other.coordinate)
    
    def distance_vec(self,vec):
        return self.coordinate.distance_vec(vec)
    
    def visitNearest(self,others,only_unvisited=True):
        nearest=self.getNearest(others,only_unvisited)
        if nearest is not None:
            self.next=nearest
            nearest.visit()
        return nearest

    def visitAll(self,others,only_unvisited=True, tracker=[]):
        if not self.visited:
            self.visit()
        tracker.append(self)
        n = self.visitNearest(others,only_unvisited)
        if n is not None:
            n.visitAll(others,only_unvisited,tracker)
        return tracker

    def getNearestIdx(self,others,only_unvisited=True):
        if self.next is not None:
            return self.next
        nearest=None
        nearest_dist = None
        nearest_idx=-1
        for other_idx in range(len(others)):
            other = others[other_idx]
            if other == self:
                continue
            if only_unvisited and other.visited:
                continue
            dist = self.distance(other)
            
            if nearest is None:
                nearest_dist=dist
                nearest=other
                nearest_idx=other_idx
                continue
            
            if dist<nearest_dist:
                nearest_dist = dist
                nearest=other
                nearest_idx=other_idx
        return nearest_idx

    def getNearest(self,others,only_unvisited=True):
        nearest=None
        nearest_idx = self.getNearestIdx(others,only_unvisited)
        if nearest_idx > -1:
            nearest=others[nearest_idx]
        return nearest
        # if self.next is not None:
        #     return self.next
        # nearest=None
        # nearest_dist = None
        # for other in others:
        #     if other == self:
        #         continue
        #     if only_unvisited and other.visited:
        #         continue
        #     dist = self.distance(other)
            
        #     if nearest is None:
        #         nearest_dist=dist
        #         nearest=other
        #         continue
            
        #     if dist<nearest_dist:
        #         nearest_dist = dist
        #         nearest=other
        # return nearest

    def is_clockwise_to(self,other):
        return self.coordinate.turntable_angle-other.coordinate.turntable_angle>=0
    
    def is_counter_clockwise_to(self,other):
        return not self.is_clockwise_to(other)
    
    

    @staticmethod
    def cmp(me,other):
        return Coordinate.cmp(me.coordinate,other.coordinate)

    @staticmethod
    def is_clockwise(coll):
        return coll[1].is_clockwise_to(coll[0])

    @staticmethod
    def coord(derp):
        return derp.coordinate
    
    @staticmethod
    def gen_interval_indexes(max,x=1,offset=0):
        indexes=[]
        for i in range(int(max/x)):
            idx=(i*x)+offset
            if idx<max:    
                indexes.append(idx)
        return indexes


    @staticmethod
    def gen_interval_indexes_all(max,x=1,do_flip_flop=True):
        indexes=mapped_coordinate.gen_interval_indexes_segments(max,x,do_flip_flop)
        result=[]
        for i in indexes:
            result.extend(i)
        return result

    @staticmethod
    def gen_interval_indexes_segments(max,x=1,do_flip_flop=True):
        indexes=[]
        
        for i in range(x):
            idxs=mapped_coordinate.gen_interval_indexes(max,x,i)
            if do_flip_flop:
                if reverse:
                    idxs.reverse()
                reverse=not reverse
            indexes.append(idxs)
        return indexes

    @staticmethod
    def __get_ordering_by_startpoint_nearness(segments:list):
        def_order=list(range(len(segments)))
        order=[]
        order.append(def_order.pop(0))
        while(len(def_order)>0):
            if(len(def_order)==1):
                order.append(def_order.pop())
                continue
            last_ordered_segment_idx=order[len(order)-1]
            last_ordered_segment_start=segments[last_ordered_segment_idx][0]
            other_segments=list(map(lambda idx:segments[idx],def_order))
            other_segment_starts=list(map(lambda seg:seg[0],other_segments))
            shortest_idx_pre=last_ordered_segment_start.getNearestIdx(other_segment_starts)
            shortest_idx=def_order.pop(shortest_idx_pre)
            order.append(shortest_idx)
        return order


    @staticmethod
    def __reorder_segments_by_startpoint_nearness(segments:list):
        ordering=mapped_coordinate.__get_ordering_by_startpoint_nearness(segments)
        reordered=[]
        for idx in ordering:
            seg=segments[idx]
            reordered.append(seg)
        return reordered
            

    @staticmethod
    def __do_flip_flopping(segments:list):
        reordered_segments=mapped_coordinate.__reorder_segments_by_startpoint_nearness(segments)
        reverse=False
        for seg in reordered_segments:
            if reverse:
                seg.reverse()
            reverse=not reverse
        return reordered_segments

    @staticmethod
    def select_every_x_item(coll,x=1,offset=0):
        indexes=mapped_coordinate.gen_interval_indexes(len(coll),x,offset)
        return list(map(lambda i:coll[i],indexes))
    
    @staticmethod
    def select_every_x_item_all(coll:typing.List[typing.KT],x=1,do_flip_flop=True)->typing.List[typing.KT]:
        is_mapped_coordinate_coll = len(coll)>1 and isinstance(coll[0],mapped_coordinate)
        do_post_flip_flop = do_flip_flop and is_mapped_coordinate_coll
        do_preemptive_flip_flop=do_flip_flop and not is_mapped_coordinate_coll
        result=[]
        segments=mapped_coordinate.select_every_x_item_segments(coll,x,do_post_flip_flop)
        for seg in segments:
            result.extend(seg)
            
        return result
    
    def select_every_x_item_segments(coll,x=1,do_flip_flop=True):
        is_mapped_coordinate_coll = len(coll)>1 and isinstance(coll[0],mapped_coordinate)
        do_post_flip_flop = do_flip_flop and is_mapped_coordinate_coll
        do_preemptive_flip_flop=do_flip_flop and not is_mapped_coordinate_coll
        result=[]
        segments=[]
        if not do_post_flip_flop:
            segments=mapped_coordinate.gen_interval_indexes_segments(len(coll),x,do_flip_flop)
        else:
            segments=mapped_coordinate.gen_interval_indexes_segments(len(coll),x,False)
        
        
        
        for segment in segments:
            result.append(list(map(lambda i:coll[i],segment)))
        print(len(result))
        if do_post_flip_flop:
            result=mapped_coordinate.__do_flip_flopping(result)
        print(len(result))
        return result

    @staticmethod
    def as_edge_pairs(list_of_mapped_coordinates):
        edges=[]
        for i in range(len(list_of_mapped_coordinates)-1):
            mapped_coord = list_of_mapped_coordinates[i]
            next_coord = list_of_mapped_coordinates[i+1]
            edges.append((mapped_coord.index(),next_coord.index()))
        return edges
    

def capture_number_to_turntable_and_rotor_angle(min_angle:float,max_angle:float, num_captures:int):
    golden_ratio = float(math.pi * (3.0 - math.sqrt(5.0)))
    rotor_angles=(max_angle - min_angle)
    rotor_angle_interval = rotor_angles / float(num_captures)
    print("num1: {}, num2: {}".format(golden_ratio,rotor_angle_interval));
    r = min_angle
    t = 0.0
    mappedAngles=[]
    
    for i in range(num_captures):
        mappedAngles.append(mapped_coordinate(i+1,r,t))
        mod = 360.0
        if r < 0:
            mod=-360
        r =  math.fmod((r + rotor_angle_interval),mod)
        t_radians = t + golden_ratio * 180.0 / math.pi
        t = math.fmod(t_radians,360.0)
    
    return mappedAngles

def print_cols(cap_map):
    sorted = cap_map.copy()
    sorted.sort(key=mapped_coordinate.coord)
    for i in range(len(cap_map)):
        print("{}  {}".format(cap_map[i],sorted[i]))





