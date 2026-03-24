class RuleEngine:
    def __init__(self, features):
        self.features = features
        self.results = []
        
    def validate(self):
        """Apply hardcoded physics/manufacturing rules."""
        if not self.features:
            return self.results
            
        # 1. Minimum Thickness Check
        target_min_thickness = 2.0
        actual_thickness = self.features.get("thickness_mm", 0)
        if actual_thickness < target_min_thickness:
            self.results.append({
                "rule": "Minimum Thickness",
                "severity": "ERROR",
                "message": f"Thickness is {actual_thickness}mm, which is below the minimum required 2.0mm.",
                "value": actual_thickness
            })
        else:
             self.results.append({
                "rule": "Minimum Thickness",
                "severity": "PASS",
                "message": f"Thickness ({actual_thickness}mm) is well within safety margins.",
                "value": actual_thickness
            })
            
        # 2. Structural Symmetry (Proxy)
        sym_score = self.features.get("symmetry_score", 0)
        if sym_score < 0.4:
            self.results.append({
                "rule": "Structural Symmetry",
                "severity": "WARNING",
                "message": "Design is highly asymmetrical, which might lead to structural weakness.",
                "value": sym_score
            })
        else:
            self.results.append({
                "rule": "Structural Symmetry",
                "severity": "PASS",
                "message": "Good symmetrical balance.",
                "value": sym_score
            })

        # 3. Size constraints (e.g., bounding box fit for 3D printer)
        max_limit = 250.0 # e.g. 250mm x 250mm build volume
        max_dim = self.features.get("max_dimension_mm", 0)
        if max_dim > max_limit:
            self.results.append({
                "rule": "Printability Size",
                "severity": "ERROR",
                "message": f"Maximum dimension ({max_dim}mm) exceeds the standard build platform (250mm).",
                "value": max_dim
            })
        else:
            self.results.append({
                "rule": "Printability Size",
                "severity": "PASS",
                "message": "Fits within standard build volumes.",
                "value": max_dim
            })
            
        # 5. Hole Count Check
        hole_count = self.features.get("hole_count", 0)
        if hole_count > 15:
            self.results.append({
                "rule": "Hole Density",
                "severity": "WARNING",
                "message": f"High number of holes detected ({hole_count}). This may complicate manufacturing and reduce strength.",
                "value": hole_count
            })
        else:
            self.results.append({
                "rule": "Hole Density",
                "severity": "PASS",
                "message": f"Design has {hole_count} holes, within safe limits.",
                "value": hole_count
            })
            
        return self.results
        
    def get_errors(self):
        return [r for r in self.results if r["severity"] == "ERROR"]
        
    def get_warnings(self):
         return [r for r in self.results if r["severity"] == "WARNING"]
