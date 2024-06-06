import pandas as pd
import re
import argparse
from datetime import datetime
from convert_douyin import *
from util import *
pd.options.display.float_format='{:f}'.format
# Function to clean the 'property' column by removing parenthesis and content inside them
def clean_property(prop):
    try:
        # Remove everything within parenthesis and the parenthesis themselves
        cleaned_prop = re.sub(r'\(.*?\)', '', prop)
        cleaned_prop = re.sub(r'\（.*?\）', '', cleaned_prop) #中文括号过滤
        cleaned_prop = re.sub(r'\[.*?\]', '', cleaned_prop) #中文括号过滤     
        return cleaned_prop.strip()
    except:
        return ""

# Function to split the cleaned property into category, size, and color
def split_property(prop):
    # Define regex patterns for category, color, and size
    category_pattern = r'[A-Za-z0-9-]+(?=[\u4e00-\u9fff])'
    # color_pattern = r'[\u4e00-\u9fff].*?(?=;)'  # 以;结束，这是修改前的
    color_pattern = r'[\u4e00-\u9fff].*?(?=;|、)' #以;或、结束 ，这是修改后的
    # size_pattern = r'(?<=:)\d+' #以：开始的
    size_pattern = r'\d+'  # 修改后直接找数字

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


def tmall_process_excel_file(input_file):
    # Determine the file extension
    file_extension = input_file.split('.')[-1]

    # Read the Excel file with the appropriate engine
    if file_extension == 'xls':
        df = pd.read_excel(input_file, sheet_name=0, engine='xlrd')
    elif file_extension == 'xlsx':
        df = pd.read_excel(input_file, sheet_name=0, engine='openpyxl')
    else:
        raise ValueError("Unsupported file format. Please provide an Excel file with .xls or .xlsx extension.")
    # if df['销售属性'] is not None: #如果是抖音文件，调用抖音脚本 
    if '销售属性' in df.columns:
        return douyin_process_excel_file(input_file)
    
    
    # Apply the cleaning function to the 'property' column
    df['cleaned_property'] = df['属性'].apply(clean_property)



    # Split the cleaned property into new columns
    category = "货号"
    shoe_size =  '鞋码'
    shoe_color = '颜色'
    df[[category,shoe_size,shoe_color ]] = df['cleaned_property'].apply(lambda x: pd.Series(split_property(x)))

    # Drop the intermediate 'cleaned_property' column as it's no longer needed
    df.drop(columns=['cleaned_property'], inplace=True)
    df = df.dropna(subset=[category])
    # Save the processed DataFrame to a new Excel file
    # Create a timestamped output file name
    selected_columns = ["打印时间","店铺名称", "快递公司", "快递单号", "商家编码","属性","子订单商品数量", category, shoe_color, shoe_size, "主订单编号"]
    df['属性'] = df[category]  + df[shoe_color] + '，' + df[shoe_size]
    df_selected = df[selected_columns]
    df_selected.columns = ["付款时间","店铺", "物流公司", "运单号","商家编码","属性", "商品数量", category, shoe_color, shoe_size , "订单编号"] # 保持和天猫同名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_path = f"{input_file.rsplit('.', 1)[0]}_{timestamp}.xlsx"    
    output_file_path = add_prefix_to_specific_file(output_file_path, 'tm_')
    df_selected.to_excel(output_file_path, index=False, engine='openpyxl')  # Use openpyxl engine for output
    
    print(f"Processed file saved as {output_file_path}")
    return output_file_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process an Excel file to split the property column.')
    parser.add_argument('input_file', type=str, help='The path to the input Excel file')
    
    args = parser.parse_args()
    tmall_process_excel_file(args.input_file)
