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
project_number = st.text_input("Project Number")

# Input for Glass Offset in mm
glass_offset = st.number_input("Enter Glass Offset (mm)", value=4.76, step=0.01)

# ==================== Template File ====================
template_path = "IGR_testfile.csv"
template_df = pd.read_csv(template_path)

template_file = BytesIO()
with pd.ExcelWriter(template_file, engine="xlsxwriter") as writer:
    worksheet = writer.book.add_worksheet("Template")
    worksheet.insert_image("A1", "ilogo.png", {"x_scale": 0.2, "y_scale": 0.2})
    worksheet.write("A5", "Template File")
    worksheet.write("A6", "Date Created:")
    worksheet.write("B6", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    template_df.to_excel(writer, index=False, sheet_name="Template", startrow=10)

st.download_button(
    "Download Template File",
    data=template_file.getvalue(),
    file_name="Template_File.xlsx"
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

    # Define the variables and their explanations for the Variables tab
    variables_data = {
        "Variable Name": summary_columns,
        "Explanation": [
            "Read from uploaded file" if col in [
                "VGA Width mm", "VGA Height mm", "Joint Left", "Joint Right", "Joint Top", "Joint Bottom", "Qty", "Type"
            ] else
            "Calculated: VGA Width mm - Joint Left - Joint Right" if col == "GS Width mm" else
            "Calculated: VGA Height mm - Joint Top - Joint Bottom" if col == "GS Height mm" else
            "Calculated: GS Width mm * mm_to_inches" if col == "GS Width in" else
            "Calculated: GS Height mm * mm_to_inches" if col == "GS Height in" else
            "Calculated: GS Width mm (directly from columns)" if col in ["SSP Top", "SSP Bottom"] else
            "Calculated: GS Height mm - profile_width - profile_height - (2 * 0.15)" if col in ["SSP Left", "SSP Right"] else
            "Calculated: GS Width mm - (2 * glass_offset)" if col == "Framed G Width mm" else
            "Calculated: GS Height mm - (2 * glass_offset)" if col == "Framed G Height mm" else
            "Predefined constant: 12 inches in mm" if col == "L1" else
            "Predefined constant: 2 inches in mm" if col == "L2" else
            "Calculated: Floor((SSP Top - (2 * 25.4)) / L1)" if col == "Qty1" else
            "Calculated: Floor((SSP Top - (2 * 25.4) - (Qty1 * L1)) / L2)" if col == "Qty2" else
            "Calculated: L1 * Qty1" if col == "TL1" else
            "Calculated: L2 * Qty2" if col == "TL2" else
            "Unknown (custom column)"
            for col in summary_columns
        ]
    }
    variables_df = pd.DataFrame(variables_data)

    summary_file = BytesIO()
    with pd.ExcelWriter(summary_file, engine="xlsxwriter") as writer:
        # First tab: Summary
        worksheet = writer.book.add_worksheet("Summary")
        worksheet.insert_image("A1", "ilogo.png", {"x_scale": 0.2, "y_scale": 0.2})
        worksheet.write("A5", "Project Name:")
        worksheet.write("A6", "Project Number:")
        worksheet.write("A7", "Date Created:")
        worksheet.write("B5", project_name)
        worksheet.write("B6", project_number)
        worksheet.write("B7", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        summary_df.to_excel(writer, index=False, sheet_name="Summary", startrow=10)

        # Second tab: Variables
        variables_df.to_excel(writer, index=False, sheet_name="Variables")

    # ==================== Glass File ====================
    glass_df = pd.DataFrame({
        "Item": range(1, len(df) + 1),
        "Glass Width in": df["Framed G Width in"],
        "Glass Height in": df["Framed G Height in"],
        "Area Each (ft²)": (df["Framed G Width in"] * df["Framed G Height in"]) * sq_inches_to_sq_feet,
        "Qty": df["Qty"],
        "Area Total (ft²)": df["Qty"] * (df["Framed G Width in"] * df["Framed G Height in"]) * sq_inches_to_sq_feet,
    })

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

    # ==================== AggCutOnly File ====================
    df["Qty x 2"] = df["Qty"] * 2
    width_counts = df.groupby("Framed G Width in")["Qty"].sum().sort_values(ascending=False)
    height_counts = df.groupby("Framed G Height in")["Qty"].sum().sort_values(ascending=False)
    unique_dimensions = pd.Index(width_counts.index.tolist() + height_counts.index.tolist()).unique()

    agg_df = pd.DataFrame(0, index=unique_dimensions, columns=["Part #", "Miter"] + df["Type"].unique().tolist() + ["Total QTY"])
    agg_df["Part #"] = f"IGR-{project_number}"
    agg_df["Miter"] = "**"

    for i, row in df.iterrows():
        width, height, type_, qty_x_2 = row["Framed G Width in"], row["Framed G Height in"], row["Type"], row["Qty x 2"]
        if width in agg_df.index and type_ in agg_df.columns:
            agg_df.at[width, type_] += qty_x_2
        if height in agg_df.index and type_ in agg_df.columns:
            agg_df.at[height, type_] += qty_x_2

    agg_df["Total QTY"] = agg_df[df["Type"].unique()].sum(axis=1)
    agg_df.index.name = "Finished Length in"
    agg_df = agg_df.reset_index()

    agg_file = BytesIO()
    with pd.ExcelWriter(agg_file, engine="xlsxwriter") as writer:
        worksheet = writer.book.add_worksheet("Cutfile")
        worksheet.insert_image("A1", "ilogo.png", {"x_scale": 0.2, "y_scale": 0.2})
        worksheet.write("A5", "Project Name:")
        worksheet.write("A6", "Project Number:")
        worksheet.write("A7", "Date Created:")
        worksheet.write("B5", project_name)
        worksheet.write("B6", project_number)
        worksheet.write("B7", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        agg_df.to_excel(writer, index=False, sheet_name="Cutfile", startrow=10)

    # ==================== Download Buttons ====================
    st.download_button("Download Summary File", data=summary_file.getvalue(), file_name="Summary_File.xlsx")
    st.download_button("Download Glass File", data=glass_file.getvalue(), file_name="Glass_File.xlsx")
    st.download_button("Download Cutfile", data=agg_file.getvalue(), file_name="Cutfile.xlsx")