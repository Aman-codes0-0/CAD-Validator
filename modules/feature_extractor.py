import numpy as np
import trimesh

class FeatureExtractor:
    def __init__(self, mesh):
        self.mesh = mesh
        
    def extract_features(self):
        """Extract geometric and heuristic features for ML and rule logic."""
        if not self.mesh or self.mesh.is_empty:
            return {}
            
        # Basic dimensions
        extents = self.mesh.extents
        min_dim = float(np.min(extents))
        max_dim = float(np.max(extents))
        
        # Volume and Area
        volume = float(self.mesh.volume) if self.mesh.is_watertight else float(self.mesh.convex_hull.volume)
        surface_area = float(self.mesh.area)
        
        # Heuristics
        # Approximate average thickness = Volume / Surface Area * 2
        approx_thickness = (volume / surface_area) * 2.0 if surface_area > 0 else 0.0
        
        # Surface Area to Volume Ratio
        sa_vol_ratio = surface_area / volume if volume > 0 else 0.0
        
        # Aspect Ratio (max_dim / min_dim)
        aspect_ratio = max_dim / min_dim if min_dim > 0 else 0.0
        
        # Edge count & Hole detection
        # Non-watertight models or models with internal boundary edge loops suggest holes
        if self.mesh.is_watertight:
            hole_count = 0
            # For watertight meshes, genus can indicate number of "tunnels" (through holes)
            # Euler characteristic = V - E + F = 2 - 2g
            # g = 1 - (V - E + F)/2
            euler = len(self.mesh.vertices) - len(self.mesh.edges) + len(self.mesh.faces)
            genus = 1 - euler // 2
            hole_count = max(0, genus)
        else:
            # For non-watertight, use boundary edges as a proxy for holes/gaps
            edges_unique = self.mesh.edges_unique
            # Highly simplified heuristic
            hole_count = len(trimesh.graph.split(self.mesh.edges_unique)) // 10 

        # 5. Symmetry Score
        # Compare volume of mesh vs volume of convex hull (simplistic symmetry/concavity heuristic)
        hull_volume = float(self.mesh.convex_hull.volume)
        symmetry_score = volume / hull_volume if hull_volume > 0 else 0.0
        
        # 6. Hole Detection Heuristic
        # Euler characteristic: V - E + F = 2(1 - genus) - holes
        # Simplified: Genus often represents holes in CAD.
        # trimesh.euler_number is V - E + F
        # For a single manifold component, Euler characteristic = 2 - 2*genus
        # genus = 1 - (Euler characteristic / 2)
        # For multiple components, Euler characteristic = 2*components - 2*genus
        # genus = components - (Euler characteristic / 2)
        genus = int(self.mesh.body_count - self.mesh.euler_number / 2.0)
        hole_count = max(0, genus)
        
        return {
            "min_dimension_mm": round(min_dim, 2),
            "max_dimension_mm": round(max_dim, 2),
            "thickness_mm": round(approx_thickness, 2),
            "volume_mm3": round(volume, 2),
            "surface_area_mm2": round(surface_area, 2),
            "aspect_ratio": round(aspect_ratio, 2),
            "sa_volume_ratio": round(sa_vol_ratio, 3),
            "hole_count": hole_count,
            "symmetry_score": round(symmetry_score, 2)
        }
