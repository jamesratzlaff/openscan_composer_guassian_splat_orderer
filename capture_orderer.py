import pathlib
import array
import os
import rotor_and_turntable_angle_capture_resolver as cap_resolver
import re
import argparse
from openscanconfig import openscan_config
from typing import List
from shutil import copy2

class numbered_file:
    def __init__(self,in_dir,match:re.match):
        self.dir=in_dir
        self.basename=os.path.basename(match.group(0))
        self.capture_num=int(match.group(1))
    
    def path(self)->str:
         return os.path.join(self.dir,self.basename)

    def __repr__(self):
         return str(self.capture_num)+"=>"+str(self.path())

class numbered_files:
    def __init__(self,numbered_files:List[numbered_file]):
        self.numbered_files=numbered_files
        max=-1
        for numbered_file in self.numbered_files:
            if numbered_file.capture_num>max:
                max=numbered_file.capture_num
        self.indexed_files=[None]*(max+1)
        for numbered_file in self.numbered_files:
            self.indexed_files[numbered_file.capture_num]=numbered_file
    
    def get(self,capture_num:int)->numbered_file|None:
       if capture_num<0 or capture_num>len(self.indexed_files):
           return None
       return self.indexed_files[capture_num]

class orderer:
    def __init__(self,out_dir,numberd_files,config:openscan_config):
          self.numbered_files=numbered_files(numberd_files)
          self.mapped_coordinates=None
          self.config=config
          self.out_dir=out_dir
          self.get_mapped_coordinates(False)
          
    
    def get_mapped_coordinates(self, prompt=True)->List[cap_resolver.mapped_coordinate]:
        if self.mapped_coordinates is None:
            if self.validate_config(prompt):
                self.mapped_coordinates=cap_resolver.capture_number_to_turntable_and_rotor_angle(self.config.MinAngle,self.config.MaxAngle,self.config.NumPhotos)
        return self.mapped_coordinates
    
    def get_copy_plan(self,segments:int=5,prompt=True)->List[numbered_file]:
        mapped_coords=self.get_mapped_coordinates(prompt)
        arcpaths = cap_resolver.mapped_coordinate.select_every_x_item_all(mapped_coords,segments)
        reso=[]
        for apth in arcpaths:
            cnum=apth.capture_num
            numd_file=self.numbered_files.get(cnum)
            if numd_file is not None:
                reso.append(numd_file)
        return reso
    
    def process_copy_plan(self,copy_plan=None,segments:int=5,prompt=True)->None:
        if copy_plan is None:
            copy_plan=self.get_copy_plan(segments,prompt)
        if len(copy_plan) > 0:
            os.makedirs(self.out_dir,exist_ok=True)
            for i in range(len(copy_plan)):
                numbered_file=copy_plan[i]
                file_ext=os.path.splitext(numbered_file.basename)[1]
                output_file=os.path.join(self.out_dir,str(i)+file_ext)
                input_file=numbered_file.path()
                print("Copying "+input_file+" to "+output_file)
                copy2(input_file,output_file)

    def validate_config(self,prompt=False):
        isValid=self.config is not None
        min=False
        max=False
        num=False
        if isValid:
            min=self.config.MinAngle is not None
            max=self.config.MaxAngle is not None
            num=self.config.NumPhotos is not None
        if prompt:
            conf=self.config
            if not min:
                conf.MinAngle=float(input("MinAngle?"))
            if not max:
                conf.MaxAngle=float(input("MaxAngle?"))
            if not num:
                conf.NumPhotos=int(input("NumPhotos?"))
        return isValid
           
    
    

capture_re_pattern_str="(?:stack-)?([0-9]+)(?:_[x1]+).*$"
capture_re_pattern=re.compile(capture_re_pattern_str)

def do_the_thing(in_dir,out_dir):
    numbered_files=__get_numbered_files(in_dir)
    settingsFilePath = __try_to_get_project_config(in_dir)
    config=None
    if settingsFilePath is not None:
        config=openscan_config(settingsFilePath)
    ordrr=orderer(out_dir,numbered_files,config)
    ordrr.process_copy_plan()




def __scandirs_for_settings_file(in_dir,wildCard=False,number_of_parent_dirs=1):
    reso=None
    p=pathlib.Path(in_dir)
    for i in range(number_of_parent_dirs+1):
        prefix=p.name
        if wildCard:
             prefix="*"
        filtered=list(filter(pathlib.Path.is_file,list(p.glob(prefix+".osc"))))
        if(len(filtered)>0):
             reso=filtered[0]
             break
        p=p.parent
    if reso is not None:
         reso=reso.absolute()
    return reso
    

def __try_to_get_project_config(in_dir:str):
    settingsFile = __scandirs_for_settings_file(in_dir)
    if settingsFile is None:
         settingsFile=__scandirs_for_settings_file(in_dir,wildCard=True)
    return settingsFile
     
     

def __get_numbered_files(in_dir):
    in_dir=os.path.abspath(in_dir)
    files = [f for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir,f))]
    numbered_files=[]
    for file in files:
        mtch = capture_re_pattern.search(os.path.basename(file))
        if mtch is not None:
             numbered_files.append(numbered_file(in_dir,mtch))
    return numbered_files
             

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_dir", help="the input directory containing captures", default=os.getcwd())
    args=parser.parse_args()
    parser.add_argument("--out_dir", help="the output directory where the ordered captures will be contained", default=os.path.join(args.in_dir,"guassian_ordered"))
    args=parser.parse_args()
    print(args)
    do_the_thing(args.in_dir,args.out_dir)

if __name__ == "__main__":
         main()
         