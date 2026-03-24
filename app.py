import streamlit as st
import tempfile
import time
import os

# Fix for Aspose-CAD / .NET Globalization error on Linux
os.environ["DOTNET_SYSTEM_GLOBALIZATION_INVARIANT"] = "1"

import plotly.graph_objects as go
from modules.cad_reader import CADReader
from modules.feature_extractor import FeatureExtractor
from modules.rule_engine import RuleEngine
from modules.ml_model import CADMLModel
from modules.suggestion_engine import SuggestionEngine
from modules.report_generator import ReportGenerator

# Page config
st.set_page_config(
    page_title="AI CAD Validator",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
<style>
    .reportview-container { background: #121212; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #4CAF50; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #45a049; }
    .status-pass { color: #4CAF50; font-weight: bold; font-size: 1.2rem; }
    .status-fail { color: #F44336; font-weight: bold; font-size: 1.2rem; }
    .stMetric { background-color: #1e1e1e; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

st.title("⚙️ AI-Driven CAD Validation System")
st.markdown("Upload your CAD file (STL/OBJ). Our AI will analyze the geometry, detect flaws, and give you real-time Hindi/English suggestions and a downloadable PDF report.")

# Initialize the ML Model
@st.cache_resource
def load_ml_model():
    return CADMLModel()

ml_model = load_ml_model()

# Sidebar for Upload
with st.sidebar:
    st.header("1. Upload Design")
    uploaded_file = st.file_uploader("Choose a CAD file", type=["stl", "obj", "ply", "dxf", "dwg", "step", "iges", "stp", "igs"])
    
    st.markdown("---")
    st.header("⚙️ Settings")
    ai_engine = st.radio("Select AI Engine:", [
        "High Accuracy Enterprise Ensemble (XGBoost + NN + RF)",
        "Neural Network (Deep Learning Proxy)",
        "Random Forest (Fast)"
    ])
    
    st.markdown("---")
    st.markdown("**How it works:**")
    st.markdown("1. Extrudes 3D features")
    st.markdown("2. Checks hard rules (Physics)")
    st.markdown("3. AI model predicts PASS/FAIL")
    st.markdown("4. Generates Suggestions")

if uploaded_file is not None:
    # Save uploaded file to temp dir
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    if st.button("🚀 Analyze Design"):
        # Progress Simulation
        progress_text = "Parsing CAD file..."
        my_bar = st.progress(0, text=progress_text)
        
        try:
            # 1. Read CAD
            reader = CADReader(tmp_path)
            if not reader.is_valid():
                st.error(f"Failed to read CAD file: {reader.load_error}")
                st.stop()
                
            basic_info = reader.get_basic_info()
            my_bar.progress(30, text="Extracting geometric features...")
            time.sleep(0.5)
            
            # 2. Extract Features
            extractor = FeatureExtractor(reader.get_mesh())
            features = extractor.extract_features()
            features.update(basic_info) # merge info
            
            my_bar.progress(60, text="Applying intelligence rules & ML...")
            time.sleep(0.5)
            
            # 3. Rule Engine
            rules = RuleEngine(features)
            rule_results = rules.validate()
            errors = rules.get_errors()
            warnings = rules.get_warnings()
            
            # 4. ML Model
            if 'Ensemble' in ai_engine:
                engine_arg = 'ensemble'
            elif 'Neural' in ai_engine:
                engine_arg = 'nn'
            else:
                engine_arg = 'rf'
                
            ml_result = ml_model.predict(features, engine=engine_arg)
            
            my_bar.progress(85, text="Generating suggestions...")
            time.sleep(0.5)
            
            # 5. Suggestions
            sug_engine = SuggestionEngine(rule_results, ml_result)
            suggestions = sug_engine.generate_suggestions()
            
            # 6. Extract Raw Mesh for Visualization
            vertices, faces = reader.get_raw_mesh_data()
            
            my_bar.progress(100, text="Analysis complete!")
            time.sleep(0.5)
            my_bar.empty()
            # --- Display Results ---
            st.markdown("---")
            st.header("📊 Analysis Report / विश्लेषण रिपोर्ट")
            
            # Show 3D Viewer if mesh is valid
            if vertices and faces:
                with st.expander("👁️ Interactive 3D Viewer / इंटरएक्टिव 3D व्यूअर", expanded=True):
                    x, y, z = zip(*vertices)
                    i, j, k = zip(*faces)
                    
                    fig = go.Figure(data=[
                        go.Mesh3d(
                            x=x, y=y, z=z,
                            i=i, j=j, k=k,
                            color='lightblue',
                            opacity=0.8,
                            lighting=dict(ambient=0.4, diffuse=0.8, fresnel=0.1, specular=1.0, roughness=0.1, facenormalsepsilon=0)
                        )
                    ])
                    fig.update_layout(
                        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='rgb(20, 20, 20)'),
                        margin=dict(r=0, l=0, b=0, t=0), paper_bgcolor='rgba(0,0,0,0)', height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # High-end metric grid
            st.markdown("### 🔍 Geometric Features / ज्यामितीय विशेषताएं")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("Thickness", f"{features.get('thickness_mm', 0)} mm")
            m_col2.metric("Holes", features.get('hole_count', 0))
            m_col3.metric("Volume", f"{int(features.get('volume_mm3', 0)/1000)} cm³")
            m_col4.metric("Symmetry", f"{int(features.get('symmetry_score', 0)*100)}%")

            # AI Verdict Card
            st.markdown("---")
            v_col1, v_col2 = st.columns([1, 2])
            with v_col1:
                 st.markdown("#### AI Verdict")
                 v_color = "#4CAF50" if ml_result['verdict'] == "PASS" else "#F44336"
                 st.markdown(f"<div style='background-color: {v_color}; color: white; padding: 20px; border-radius: 15px; text-align: center; font-size: 2rem; font-weight: bold;'>{ml_result['verdict']}</div>", unsafe_allow_html=True)
                 st.markdown(f"<p style='text-align: center; margin-top: 10px;'>Confidence: <b>{ml_result['confidence']}%</b></p>", unsafe_allow_html=True)
            
            with v_col2:
                 st.markdown("#### Logic Engine Results")
                 for r in rule_results:
                     icon = "✅" if r['severity'] == "PASS" else ("❌" if r['severity'] == "ERROR" else "⚠️")
                     st.write(f"{icon} **{r['rule']}**: {r['message']}")

            # Suggestions Section
            st.markdown("---")
            st.subheader("💡 Manufacturing Suggestions / निर्माण सुझाव")
            for sug in suggestions:
                st.success(f"**{sug['title']}**\n\n{sug['desc']}")
            
            # Manufacturing Checklist
            with st.expander("📝 Final Manufacturing Checklist"):
                st.checkbox("Analyze wall thickness distribution", value=(features['thickness_mm'] >= 2.0))
                st.checkbox("Check for overhangs > 45 degrees", value=True)
                st.checkbox("Verify hole tolerances", value=True)
                st.checkbox("Confirm material compatibility", value=True)

            # Report Generation & Download
            st.markdown("---")
            report_gen = ReportGenerator(uploaded_file.name, output_dir=os.path.dirname(tmp_path))
            pdf_path = report_gen.generate(features, rule_results, ml_result, suggestions)
            
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download Detailed PDF Report (English/Hindi)",
                    data=f,
                    file_name=f"Report_{uploaded_file.name}.pdf",
                    mime="application/pdf"
                )
            
            st.toast("Analysis Complete!", icon="🚀")

        except Exception as e:
            st.error(f"Critical Error: {str(e)}")
            st.exception(e)
            
        finally:
            # Cleanup temp file if needed (Streamlit manages this mostly, but good practice)
            pass

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #888;'>AI-Driven CAD Validation Engine v2.5 | Enterprise Grade XGBoost + NN Ensemble Enabled</p>", unsafe_allow_html=True)
