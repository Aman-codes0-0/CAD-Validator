# ⚙️ AI-Driven CAD Validation System

A professional, AI-powered CAD analysis platform designed to automatically validate 3D designs for manufacturing readiness. This tool combines heuristic engineering rules with a high-accuracy Machine Learning ensemble to detect potential structural failures and provide real-time suggestions.

## 🚀 Key Features

*   **Interactive 3D Visualization**: Built-in Plotly-based mesh viewer for instant model inspection.
*   **Multi-Format Support**: Native parsing for `.stl`, `.obj`, `.ply`, and `.dxf`.
*   **Seamless DWG Integration**: Background auto-conversion of proprietary `.dwg` files to accessible `.dxf` format.
*   **Hybrid AI Classifier**: Enterprise-grade Voting Ensemble combining **XGBoost**, **Random Forest**, and **Neural Networks** (MLP) for reliable PASS/FAIL verdicts.
*   **Advanced Physics Engine**: Validates wall thickness, symmetry, hole density, and aspect ratios.
*   **Actionable Suggestions**: Real-time manufacturing advice in both **English** and **Hindi**.
*   **Professional Reporting**: Generates downloadable PDF reports with full analysis details.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.12+** installed on your system.

### 2. Manual Environment Setup (Linux/macOS)
```bash
# Clone or move into the project directory
cd /home/dell/Desktop/CAD

# Create a virtual environment
python3 -m venv venv

# Activate the environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup (Alternative - .venv)
If you are using the pre-configured `.venv`, simply activate it:
```bash
source .venv/bin/activate
```

---

## 🖥️ How to Run the App

1.  **Activate the Environment**:
    ```bash
    source venv/bin/activate
    ```
2.  **Run the Streamlit Dashboard**:
    ```bash
    streamlit run app.py
    ```
    Once started, the app will be live at `http://localhost:8501`.

---

## 🛠️ Critical System Prerequisites (Linux)

To ensure **DWG files** are processed correctly without errors, you **must** install the following .NET dependencies on your system. Run this once in your terminal:

```bash
sudo apt-get update && sudo apt-get install -y libicu-dev libgdiplus
```

*Without these, DWG conversion will fail, but you can still use DXF, STL, and OBJ formats.*

---

## 📂 Project Structure

*   `app.py`: Main entry point and Streamlit UI.
*   `modules/`:
    *   `cad_reader.py`: Handles file parsing and DWG conversion.
    *   `feature_extractor.py`: Extracts geometric metrics (Volumes, Holes, etc.).
    *   `rule_engine.py`: Applies physics-based validation rules.
    *   `ml_model.py`: Orchestrates the XGBoost/Ensemble AI.
    *   `suggestion_engine.py`: Maps errors to bilingual feedback.
    *   `report_generator.py`: PDF generation logic.
*   `models/`: Stores trained model artifacts (`.pkl`).
*   `sample_files/`: Contains test models (`good_design.stl`, `bad_design.stl`).

---

## 📂 Supported Formats

*   **Primary**: `.stl`, `.obj`, `.ply`, `.dxf` (Full AI Analysis & 3D Viewing).
*   **DWG Users**: Please **'Save As' -> DXF** in your CAD software before uploading. This ensures maximum data integrity and prevents system crashes associated with proprietary binary formats.

---

## 🖥️ How to Run the App
