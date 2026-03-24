import trimesh
import os

# Create directory if not exists
os.makedirs("sample_files", exist_ok=True)

# 1. Good Design (Thick, symmetrical, standard box)
# create a standard box
good_mesh = trimesh.creation.box(extents=(50, 50, 10)) # 10mm thickness
good_mesh.export("sample_files/good_design.stl")
print("good_design.stl created")

# 2. Bad Design (Too thin, weird aspect ratio)
# create a very thin and tall box
bad_mesh = trimesh.creation.box(extents=(10, 100, 1)) # 1mm thickness, aspect 100/1=100
bad_mesh.export("sample_files/bad_design.stl")
print("bad_design.stl created")
