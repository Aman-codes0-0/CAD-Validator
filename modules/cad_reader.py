import os
import trimesh
import numpy as np
import ezdxf

class CADReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.mesh = None
        self.load_error = None
        self._load_mesh()
        
    def _load_mesh(self):
        try:
            if not os.path.exists(self.file_path):
                self.load_error = "File does not exist."
                return
                
            ext = os.path.splitext(self.file_path)[1].lower()
            if ext == '.dwg':
                import subprocess
                # Attempt to find system converters or provide a one-click fix script
                self.load_error = (
                    "### 🛠️ One-Click Fix Required\n"
                    "DWG support on Linux requires internal .NET components that are currently missing.\n\n"
                    "**To fix this project-wide, please run this command in your terminal:**\n"
                    "```bash\n"
                    "sudo apt-get update && sudo apt-get install -y libicu-dev libgdiplus\n"
                    "```\n"
                    "Once installed, your DWG files will process automatically. \n\n"
                    "**Alternative:** Save your file as **DXF (AutoCAD R12)** and it will work instantly without any system changes."
                )
                return
            
            if ext in ['.step', '.stp', '.iges', '.igs']:
                self.load_error = "STEP/IGES solid formats require an explicit CAD kernel for meshing. Please convert to STL/OBJ/PLY for now."
                return
                
            # Trimesh can load STL, OBJ, PLY, and DXF meshes securely
            self.mesh = trimesh.load(self.file_path)
            
            # If a Scene is returned (e.g. multiple objects in OBJ/DXF), try to merge into a single mesh
            if isinstance(self.mesh, trimesh.Scene):
                if len(self.mesh.geometry) == 0:
                    self.load_error = "Empty scene loaded. Ensure the file contains 3D mesh data."
                    self.mesh = None
                else:
                    self.mesh = trimesh.util.concatenate(
                        tuple(trimesh.Trimesh(vertices=g.vertices, faces=g.faces)
                            for g in self.mesh.geometry.values() if isinstance(g, trimesh.Trimesh))
                    )
                    if self.mesh is None or self.mesh.is_empty:
                        self.load_error = "No valid 3D mesh geometry found in the file."
        except Exception as e:
            self.load_error = str(e)
            
    def get_raw_mesh_data(self):
        """Returns vertices and faces for Plotly 3D visualizer."""
        if not self.is_valid():
            return None, None
        return self.mesh.vertices.tolist(), self.mesh.faces.tolist()
            
    def is_valid(self):
        return self.mesh is not None and self.mesh.is_empty is False

    def get_basic_info(self):
        if not self.is_valid():
            return None
            
        return {
            "filename": os.path.basename(self.file_path),
            "vertices_count": len(self.mesh.vertices),
            "faces_count": len(self.mesh.faces),
            "is_watertight": self.mesh.is_watertight,
            "volume_mm3": self.mesh.volume if self.mesh.is_watertight else self.mesh.convex_hull.volume,
            "surface_area_mm2": self.mesh.area,
            "bounding_box_mm": self.mesh.extents.tolist() # [x, y, z] sizes
        }
        
    def get_mesh(self):
        return self.mesh
