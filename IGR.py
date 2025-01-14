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
profiles = {
    "01401": {"Width": 38, "Height": 7.85},
}

# Fixed Profile Data
profile_01401 = profiles["01401"]
profile_width = profile_01401["Width"]
profile_height = profile_01401["Height"]

# User Input: Project Details
st.subheader("Enter Project Details")
project_name = st.text_input("Project Name")
project_number = st.text_input("Project Number", value="INO-")  # Prefill with "INO-"

# Input for Glass Offset in mm
glass_offset = st.number_input("Enter Glass Offset (mm)", value=4.76, step=0.01)

# ==================== Template File ====================
template_path = "IGR_testfile.csv"
template_df = pd.read_csv(template_path)

# Provide the original IGR_testfile.csv without alterations
st.download_button(
    "Download Template File",
    data=open(template_path, "rb").read(),
    file_name="IGR_testfile.csv"
)

# File Upload: Openings
st.subheader("Upload Openings Data")
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    # Load the uploaded file into a DataFrame
    df = pd.read_csv(uploaded_file)
    st.write("**Uploaded Data:**")
    st.dataframe(df)

    # Add calculated columns
    df["GS Width mm"] = df["VGA Width mm"] - df["Joint Left"] - df["Joint Right"]
    df["GS Height mm"] = df["VGA Height mm"] - df["Joint Top"] - df["Joint Bottom"]
    df["GS Width in"] = df["GS Width mm"] * mm_to_inches
    df["GS Height in"] = df["GS Height mm"] * mm_to_inches
    df["SSP Top"] = df["GS Width mm"]
    df["SSP Bottom"] = df["GS Width mm"]
    df["SSP Left"] = df["GS Height mm"] - profile_width - profile_height - (2 * 0.15)
    df["SSP Right"] = df["SSP Left"]
    df["UPP Top"] = df["GS Width mm"]  # Same as GS Width mm
    df["UPP Bottom"] = df["GS Width mm"]  # Same as GS Width mm
    df["UPP Left"] = df["GS Height mm"] - (2 * 0.15)  # GS Height mm minus 2 * 0.15
    df["UPP Right"] = df["UPP Left"]  # Same as UPP Left
    df["Framed G Width mm"] = df["GS Width mm"] - (2 * glass_offset)
    df["Framed G Height mm"] = df["GS Height mm"] - (2 * glass_offset)
    df["Framed G Width in"] = np.round((df["Framed G Width mm"] * mm_to_inches) * 16) / 16
    df["Framed G Height in"] = np.round((df["Framed G Height mm"] * mm_to_inches) * 16) / 16
    df["L1"] = 12 * inches_to_mm
    df["L2"] = 2 * inches_to_mm
    df["Qty1"] = np.floor((df["SSP Top"] - (2 * 25.4)) / df["L1"]).astype(int)
    df["Qty2"] = np.floor(
        (df["SSP Top"] - (2 * 25.4) - (df["Qty1"] * df["L1"])) / df["L2"]
    ).astype(int)
    df["TL1"] = df["L1"] * df["Qty1"]
    df["TL2"] = df["L2"] * df["Qty2"]

    # ==================== Summary File ====================
    summary_columns = list(df.columns) + [
        "GS Width mm", "GS Height mm", "GS Width in", "GS Height in", "SSP Top", "SSP Bottom", "SSP Left",
        "SSP Right", "Framed G Width in", "Framed G Height in", "Framed G Width mm", "Framed G Height mm",
        "L1", "L2", "Qty1", "Qty2", "TL1", "TL2"
    ]
    summary_df = df[summary_columns]

    summary_file = BytesIO()
    with pd.ExcelWriter(summary_file, engine="xlsxwriter") as writer:
        worksheet = writer.book.add_worksheet("Summary")
        worksheet.insert_image("A1", "ilogo.png", {"x_scale": 0.2, "y_scale": 0.2})
        worksheet.write("A5", "Project Name:")
        worksheet.write("A6", "Project Number:")
        worksheet.write("A7", "Date Created:")
        worksheet.write("B5", project_name)
        worksheet.write("B6", project_number)
        worksheet.write("B7", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        summary_df.to_excel(writer, index=False, sheet_name="Summary", startrow=10)

    # ==================== Glass File ====================
    glass_df = pd.DataFrame({
        "Item": range(1, len(df) + 1),
        "Glass Width in": df["Framed G Width in"],
        "Glass Height in": df["Framed G Height in"],
        "Area Each (ft²)": (df["Framed G Width in"] * df["Framed G Height in"]) * sq_inches_to_sq_feet,
        "Qty": df["Qty"],
        "Area Total (ft²)": df["Qty"] * (df["Framed G Width in"] * df["Framed G Height in"]) * sq_inches_to_sq_feet,
    })


    # Add rounded columns for Glass Width and Height
    def format_as_sixteenths(value):
        rounded = round(value * 16)  # Round to nearest 1/16
        numerator = rounded % 16  # Get the numerator
        whole_number = rounded // 16  # Get the whole number part
        if numerator == 0:
            return f"{whole_number}"  # No fractional part
        return f"{whole_number} {numerator}/16" if whole_number > 0 else f"{numerator}/16"


    glass_df["Glass Width (Nearest 1/16 in)"] = glass_df["Glass Width in"].apply(format_as_sixteenths)
    glass_df["Glass Height (Nearest 1/16 in)"] = glass_df["Glass Height in"].apply(format_as_sixteenths)

    # Reorder columns to place the new ones after their respective originals
    column_order = [
        "Item",
        "Glass Width in",
        "Glass Width (Nearest 1/16 in)",  # New column after Glass Width in
        "Glass Height in",
        "Glass Height (Nearest 1/16 in)",  # New column after Glass Height in
        "Area Each (ft²)",
        "Qty",
        "Area Total (ft²)"
    ]
    glass_df = glass_df[column_order]

    # Write the glass file to an Excel file
    glass_file = BytesIO()
    with pd.ExcelWriter(glass_file, engine="xlsxwriter") as writer:
        worksheet = writer.book.add_worksheet("Glass")
        worksheet.insert_image("A1", "ilogo.png", {"x_scale": 0.2, "y_scale": 0.2})
        worksheet.write("A5", "Project Name:")
        worksheet.write("A6", "Project Number:")
        worksheet.write("A7", "Date Created:")
        worksheet.write("B5", project_name)
        worksheet.write("B6", project_number)
        worksheet.write("B7", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        glass_df.to_excel(writer, index=False, sheet_name="Glass", startrow=10)
    # ==================== Cutfile ====================
    cutlist_data = []

    # Add rows for Support Spacer Profile first
    for _, row in df.iterrows():
        for position in ["Top", "Bottom", "Left", "Right"]:
            # Map position to corresponding SSP column
            column_name = f"SSP {position}"
            if column_name in df:
                length_mm = row[column_name]
            else:
                st.warning(f"Column {column_name} not found, skipping.")
                length_mm = 0

            # Assign Profile # based on position
            if position == "Top":
                profile_number = "1401"
            elif position == "Bottom":
                profile_number = "1501"
            elif position == "Left":
                profile_number = "1101"
            elif position == "Right":
                profile_number = "1101"

            # Create a dictionary for each row in the cutlist for SSP
            cutlist_data.append({
                "Item": len(cutlist_data) + 1,  # Running number
                "Type": "Aluminium Profile",  # Fixed value
                "Profile #": profile_number,  # Assigned Profile #
                "Description": "Support Spacer Profile",  # Fixed value
                "Position": position,  # Position from the column name
                "Qty": row["Qty"],  # Quantity from the initial DataFrame
                "Length (mm)": length_mm,  # Length in mm
                "Length (in)": length_mm * mm_to_inches,  # Length in inches
                "Cutting Angle": 90,  # Fixed value
            })

    # Add rows for Unitized Panel Profile next
    for _, row in df.iterrows():
        for position in ["Top", "Bottom", "Left", "Right"]:
            # Map position to corresponding UPP column
            column_name = f"UPP {position}"
            if column_name in df:
                length_mm = row[column_name]
            else:
                st.warning(f"Column {column_name} not found, skipping.")
                length_mm = 0

            # Assign Profile # based on position
            if position == "Top":
                profile_number = "2601"
            elif position == "Bottom":
                profile_number = "2701"
            elif position == "Left":
                profile_number = "2201"
            elif position == "Right":
                profile_number = "2301"

            # Create a dictionary for each row in the cutlist for UPP
            cutlist_data.append({
                "Item": len(cutlist_data) + 1,  # Running number
                "Type": "Aluminium Profile",  # Fixed value
                "Profile #": profile_number,  # Assigned Profile #
                "Description": "Unitized Panel Profile",  # Fixed value
                "Position": position,  # Position from the column name
                "Qty": row["Qty"],  # Quantity from the initial DataFrame
                "Length (mm)": length_mm,  # Length in mm
                "Length (in)": length_mm * mm_to_inches,  # Length in inches
                "Cutting Angle": 45,  # Fixed value
            })

    # Convert cutlist_data to a DataFrame
    cutlist_df = pd.DataFrame(cutlist_data)

    # Write the cutlist to an Excel file
    cutfile = BytesIO()
    with pd.ExcelWriter(cutfile, engine="xlsxwriter") as writer:
        worksheet = writer.book.add_worksheet("Cutfile")
        worksheet.insert_image("A1", "ilogo.png", {"x_scale": 0.2, "y_scale": 0.2})
        worksheet.write("A5", "Project Name:")
        worksheet.write("A6", "Project Number:")
        worksheet.write("A7", "Date Created:")
        worksheet.write("B5", project_name)
        worksheet.write("B6", project_number)
        worksheet.write("B7", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        cutlist_df.to_excel(writer, index=False, sheet_name="Cutfile", startrow=10)

    # ==================== Download Buttons ====================
    # ==================== Download Buttons ====================
    st.download_button("Download Summary File", data=summary_file.getvalue(), file_name=f"{project_number}_IGR_Summary_File.xlsx")
    st.download_button("Download Glass File", data=glass_file.getvalue(), file_name=f"{project_number}_IGR_Glass_File.xlsx")
    st.download_button("Download Cutfile", data=cutfile.getvalue(), file_name=f"{project_number}_IGR_Cutfile.xlsx")