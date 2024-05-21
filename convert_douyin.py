import pandas as pd
import re
import argparse
from datetime import datetime

# Function to clean the 'property' column by removing parenthesis and content inside them
def clean_property(prop):
    # Remove everything within parenthesis and the parenthesis themselves
    cleaned_prop = re.sub(r'\(.*?\)', '', prop)
    cleaned_prop = re.sub(r'\（.*?\）', '', cleaned_prop)

    return cleaned_prop.strip()

# Function to split the cleaned property into category, size, and color
def split_property(prop):
    # Define regex patterns for category, color, and size
    category_pattern = r'[A-Za-z0-9]+(?=[\u4e00-\u9fff])'
    color_pattern = r'[\u4e00-\u9fff].*?(?=;)'
    size_pattern = r'(?<=:)\d+'

    # Find category
    category_match = re.search(category_pattern, prop)
    category = category_match.group() if category_match else None

    # Find color, which starts right after the category
    if category:
        color_match = re.search(color_pattern, prop[prop.find(category) + len(category):])
        color = color_match.group().strip() if color_match else None
    else:
        color = None

    # Find size, which starts after the color
    if color:
        size_match = re.search(size_pattern, prop[prop.find(color) + len(color):])
        size = size_match.group() if size_match else None
    else:
        size = None

    return [category, size, color]


def process_excel_file(input_file):
    # Determine the file extension
    file_extension = input_file.split('.')[-1]

    # Read the Excel file with the appropriate engine
    if file_extension == 'xls':
        df = pd.read_excel(input_file, sheet_name=0, engine='xlrd')
    elif file_extension == 'xlsx':
        df = pd.read_excel(input_file, sheet_name=0, engine='openpyxl')
    else:
        raise ValueError("Unsupported file format. Please provide an Excel file with .xls or .xlsx extension.")

    # Apply the cleaning function to the 'property' column
    df['cleaned_property'] = df['销售属性'].apply(clean_property)

    # Split the cleaned property into new columns
    category = "货号"
    df[[category, '鞋码', '颜色']] = df['cleaned_property'].apply(lambda x: pd.Series(split_property(x)))

    # Drop the intermediate 'cleaned_property' column as it's no longer needed
    df.drop(columns=['cleaned_property'], inplace=True)
    df = df.dropna(subset=[category])
    # Save the processed DataFrame to a new Excel file
    # Create a timestamped output file name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_path = f"{input_file.rsplit('.', 1)[0]}_{timestamp}.xlsx"    
    # selected_columns = ['A', 'B', 'C']
    # df_selected = df[selected_columns]

    df.to_excel(output_file_path, index=False, engine='openpyxl')  # Use openpyxl engine for output

    print(f"Processed file saved as {output_file_path}")
    return output_file_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process an Excel file to split the property column.')
    parser.add_argument('input_file', type=str, help='The path to the input Excel file')
    
    args = parser.parse_args()
    process_excel_file(args.input_file)
