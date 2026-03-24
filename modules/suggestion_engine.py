class SuggestionEngine:
    def __init__(self, rule_results, ml_result):
        self.rule_results = rule_results
        self.ml_result = ml_result
        self.suggestions = []
        
    def generate_suggestions(self):
        # 1. Check Rule Violations
        for res in self.rule_results:
            if res["severity"] == "ERROR":
                if res["rule"] == "Minimum Thickness":
                    self.suggestions.append({
                        "id": "S1",
                        "title": "Increase Wall Thickness / दीवार की मोटाई बढ़ाएं",
                        "desc": f"Your current thickness is {res['value']}mm. Please increase it to at least 2.0mm to prevent structural failure. (डिज़ाइन कमज़ोर है, मोटाई 2mm से ज़्यादा करें)"
                    })
                elif res["rule"] == "Printability Size":
                    self.suggestions.append({
                        "id": "S2",
                        "title": "Scale Down Design / डिज़ाइन का आकार छोटा करें",
                        "desc": f"The maximum dimension {res['value']}mm is too large for standard manufacturing. Scale it down below 250mm. (आकार बहुत बड़ा है, 250mm के अंदर लाएं)"
                    })
                    
            elif res["severity"] == "WARNING":
                if res["rule"] == "Structural Symmetry":
                    self.suggestions.append({
                        "id": "S3",
                        "title": "Improve Structural Balance / डिज़ाइन का संतुलन सुधारें",
                        "desc": "The design is asymmetrical (score: {:.2f}). Consider adding supports or making it more symmetrical to distribute weight evenly. (डिज़ाइन एक तरफ झुका है, संतुलन सही करें)".format(res['value'])
                    })
                elif res["rule"] == "Aspect Ratio":
                    self.suggestions.append({
                        "id": "S4",
                        "title": "Reduce Aspect Ratio / अनुपात (Aspect Ratio) कम करें",
                        "desc": "The model is too tall and thin. Consider widening the base to prevent it from snapping. (डिज़ाइन बहुत लंबा और पतला है, बेस चौड़ा करें)"
                    })
                elif res["rule"] == "Hole Density":
                    self.suggestions.append({
                        "id": "S6",
                        "title": "Reduce Hole Complexity / छेदों की संख्या कम करें",
                        "desc": "Too many holes ({}) might make the part fragile during 3D printing or CNC. Merge tiny holes if possible. (छेदों की संख्या बहुत ज़्यादा है, इसे कम करें जिससे डिज़ाइन मज़बूत रहे)".format(res['value'])
                    })
                    
        # 2. Add General ML suggestion if failed but no critical rules caught
        if self.ml_result["verdict"] == "FAIL" and not any(r["severity"] == "ERROR" for r in self.rule_results):
            self.suggestions.append({
                "id": "S5",
                "title": "Overall Design Weakness / डिज़ाइन में कमज़ोरी है",
                "desc": f"Our AI model predicts failure with {self.ml_result['confidence']}% confidence based on past design patterns. Review the surface area to volume ratio. (AI मॉडल के अनुसार यह डिज़ाइन फेल हो सकता है, कृपया दोबारा चेक करें)"
            })
            
        if not self.suggestions and self.ml_result["verdict"] == "PASS":
             self.suggestions.append({
                "id": "S0",
                "title": "Design Looks Great! / डिज़ाइन एकदम सही है!",
                "desc": "No issues found. It is ready for manufacturing. (कोई गलती नहीं मिली, डिज़ाइन तैयार है)"
            })
            
        return self.suggestions
