import streamlit as st
import pandas as pd
from io import BytesIO
import numpy as np
from datetime import datetime

# Conversion constants
mm_to_inches = 1 / 25.4
inches_to_mm = 25.4
sq_inches_to_sq_feet = 1 / 144

# Layout: Title and Logo Side by Side
col1, col2 = st.columns([2, 1])
with col1:
    st.title("IGR CUT")
with col2:
    st.image("ilogo.png", width=100)

# Predefined Profile Data
profiles = {"01401": {"Width": 38, "Height": 7.85}}
profile_01401 = profiles["01401"]
profile_width = profile_01401["Width"]
profile_height = profile_01401["Height"]

# User Input: Project Details
st.subheader("Enter Project Details")
project_name = st.text_input("Project Name")
project_number = st.text_input("Project Number", value="INO-")

# Input for Glass Offset in mm
glass_offset = st.number_input("Enter Glass Offset (mm)", value=4.76, step=0.01)

# Template File
template_path = "IGR_testfile.csv"
st.download_button(
    "Download Template File",
    data=open(template_path, "rb").read(),
    file_name="IGR_testfile.csv"
)

# File Upload
st.subheader("Upload Openings Data")
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    # Load data
    df = pd.read_csv(uploaded_file)
    st.write("**Uploaded Data:**")
    st.dataframe(df)

    # Convert inputs to mm
    df["VGA Width mm"] = df["VGA Width in"] * inches_to_mm
    df["VGA Height mm"] = df["VGA Height in"] * inches_to_mm
    df["Joint Left mm"] = df["Joint Left"] * inches_to_mm
    df["Joint Right mm"] = df["Joint Right"] * inches_to_mm
    df["Joint Top mm"] = df["Joint Top"] * inches_to_mm
    df["Joint Bottom mm"] = df["Joint Bottom"] * inches_to_mm

    # Main Calculations
    df["GS Width mm"] = df["VGA Width mm"] - df["Joint Left mm"] - df["Joint Right mm"]
    df["GS Height mm"] = df["VGA Height mm"] - df["Joint Top mm"] - df["Joint Bottom mm"]
    df["GS Width in"] = df["GS Width mm"] * mm_to_inches
    df["GS Height in"] = df["GS Height mm"] * mm_to_inches

    # SSP Calculations
    df["SSP Top"] = df["GS Width mm"]
    df["SSP Bottom"] = df["GS Width mm"]
    df["SSP Left"] = df["GS Height mm"] - (2 * profile_width)
    df["SSP Right"] = df["SSP Left"]

    # UPP Calculations
    df["UPP Top"] = df["GS Width mm"]
    df["UPP Bottom"] = df["GS Width mm"]
    df["UPP Left"] = df["GS Height mm"]
    df["UPP Right"] = df["UPP Left"]

    # Framed Glass Calculations
    df["Framed G Width mm"] = df["GS Width mm"] - (2 * glass_offset)
    df["Framed G Height mm"] = df["GS Height mm"] - (2 * glass_offset)
    df["Framed G Width in"] = np.round(df["Framed G Width mm"] * mm_to_inches * 16) / 16
    df["Framed G Height in"] = np.round(df["Framed G Height mm"] * mm_to_inches * 16) / 16

    # Profile Length Calculations
    df["L1"] = 12 * inches_to_mm
    df["L2"] = 2 * inches_to_mm
    df["Qty1"] = np.floor((df["SSP Top"] - (2 * 25.4)) / df["L1"]).astype(int)
    df["Qty2"] = np.floor((df["SSP Top"] - (2 * 25.4) - (df["Qty1"] * df["L1"])) / df["L2"]).astype(int)
    df["TL1"] = df["L1"] * df["Qty1"]
    df["TL2"] = df["L2"] * df["Qty2"]

    # ===== Summary File =====
    summary_file = BytesIO()
    with pd.ExcelWriter(summary_file, engine="xlsxwriter") as writer:
        # Summary sheet
        ws = writer.book.add_worksheet("Summary")
        ws.insert_image("A1", "ilogo.png", {"x_scale": 0.2, "y_scale": 0.2})
        ws.write("A5", "Project Name:")
        ws.write("B5", project_name)
        ws.write("A6", "Project Number:")
        ws.write("B6", project_number)
        ws.write("A7", "Date Created:")
        ws.write("B7", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        df.to_excel(writer, sheet_name="Summary", index=False, startrow=10)
        # Parameters sheet
        param_ws = writer.book.add_worksheet("Parameters")
        param_ws.write("A1", "Glass Offset (mm)")
        param_ws.write("B1", glass_offset)

    # ===== Glass File =====
    glass_df = pd.DataFrame({
        "Item": range(1, len(df) + 1),
        "Glass Width in": df["Framed G Width in"],
        "Glass Height in": df["Framed G Height in"],
        "Area Each (ft²)": df["Framed G Width in"] * df["Framed G Height in"] * sq_inches_to_sq_feet,
        "Qty": df["Qty"],
        "Area Total (ft²)": df["Qty"] * df["Framed G Width in"] * df["Framed G Height in"] * sq_inches_to_sq_feet
    })
    def fmt16(v):
        r = round(v * 16)
        n = r % 16
        w = r // 16
        if n == 0:
            return f"{w}"
        return f"{w} {n}/16" if w > 0 else f"{n}/16"
    glass_df["Glass Width (Nearest 1/16 in)"] = glass_df["Glass Width in"].apply(fmt16)
    glass_df["Glass Height (Nearest 1/16 in)"] = glass_df["Glass Height in"].apply(fmt16)
    cols = [
        "Item",
        "Glass Width in",
        "Glass Width (Nearest 1/16 in)",
        "Glass Height in",
        "Glass Height (Nearest 1/16 in)",
        "Area Each (ft²)",
        "Qty",
        "Area Total (ft²)"
    ]
    glass_df = glass_df[cols]
    glass_file = BytesIO()
    with pd.ExcelWriter(glass_file, engine="xlsxwriter") as writer:
        # Glass sheet
        ws = writer.book.add_worksheet("Glass")
        ws.insert_image("A1", "ilogo.png", {"x_scale": 0.2, "y_scale": 0.2})
        ws.write("A5", "Project Name:")
        ws.write("B5", project_name)
        ws.write("A6", "Project Number:")
        ws.write("B6", project_number)
        ws.write("A7", "Date Created:")
        ws.write("B7", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        glass_df.to_excel(writer, sheet_name="Glass", index=False, startrow=10)
        # Parameters sheet
        param_ws = writer.book.add_worksheet("Parameters")
        param_ws.write("A1", "Glass Offset (mm)")
        param_ws.write("B1", glass_offset)

    # ===== Cutfile =====
    cutlist = []
    for _, row in df.iterrows():
        # SSP cutlist
        for pos, prof, angle in zip(["Top", "Bottom", "Left", "Right"], ["1401", "1501", "1101", "1101"], [90, 90, 90, 90]):
            length = row.get(f"SSP {pos}", 0)
            cutlist.append({
                "Item": len(cutlist) + 1,
                "Type": "Aluminium Profile",
                "Profile #": prof,
                "Description": "Support Spacer Profile",
                "Position": pos,
                "Qty": row["Qty"],
                "Length (mm)": length,
                "Length (in)": length * mm_to_inches,
                "Cutting Angle": angle
            })
        # UPP cutlist
        for pos, prof in zip(["Top", "Bottom", "Left", "Right"], ["2601", "2701", "2201", "2301"]):
            length = row.get(f"UPP {pos}", 0)
            cutlist.append({
                "Item": len(cutlist) + 1,
                "Type": "Aluminium Profile",
                "Profile #": prof,
                "Description": "Unitized Panel Profile",
                "Position": pos,
                "Qty": row["Qty"],
                "Length (mm)": length,
                "Length (in)": length * mm_to_inches,
                "Cutting Angle": 45
            })
    cutlist_df = pd.DataFrame(cutlist)
    cutfile = BytesIO()
    with pd.ExcelWriter(cutfile, engine="xlsxwriter") as writer:
        # Cutfile sheet
        ws = writer.book.add_worksheet("Cutfile")
        ws.insert_image("A1", "ilogo.png", {"x_scale": 0.2, "y_scale": 0.2})
        ws.write("A5", "Project Name:")
        ws.write("B5", project_name)
        ws.write("A6", "Project Number:")
        ws.write("B6", project_number)
        ws.write("A7", "Date Created:")
        ws.write("B7", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        cutlist_df.to_excel(writer, sheet_name="Cutfile", index=False, startrow=10)
        # Parameters sheet
        param_ws = writer.book.add_worksheet("Parameters")
        param_ws.write("A1", "Glass Offset (mm)")
        param_ws.write("B1", glass_offset)

    # Download Buttons
    st.download_button("Download Summary File", data=summary_file.getvalue(), file_name=f"{project_number}_IGR_Summary_File.xlsx")
    st.download_button("Download Glass File", data=glass_file.getvalue(), file_name=f"{project_number}_IGR_Glass_File.xlsx")
    st.download_button("Download Cutfile", data=cutfile.getvalue(), file_name=f"{project_number}_IGR_Cutfile.xlsx")
