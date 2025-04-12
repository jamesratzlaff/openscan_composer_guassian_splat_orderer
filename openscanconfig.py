import xml.etree.cElementTree as ET

class openscan_config:
    def __init__(self,filepath=None):
        self.filepath=filepath
        self.__load_from_filepath()
        

    def __load_from_filepath(self):
        if self.filepath is not None:
            eltree=ET.parse(self.filepath)
            
            scan_profile_node=eltree.find("ScanProfile")
            if scan_profile_node is not None:
                self.NumPhotos=int(scan_profile_node.find("NumPhotos").text)
                self.MinAngle=float(scan_profile_node.find("MinAngle").text)
                self.MaxAngle=float(scan_profile_node.find("MaxAngle").text)
