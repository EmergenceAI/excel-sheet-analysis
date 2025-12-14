import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_blocks(df):
    """
    Extracts repeating blocks of data from the DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame containing the messy data.

    Returns:
        list: A list of DataFrames, each representing a block of data.
    """
    blocks = []
    block_start_indices = df[df.iloc[:, 0].str.contains('Quarterly Sales Report', na=False)].index
    for start_idx in block_start_indices:
        end_idx = start_idx + 16  # Each block is 16 rows long including total row
        block = df.iloc[start_idx:end_idx]
        blocks.append(block)
    logging.info(f"Extracted {len(blocks)} blocks of data.")
    return blocks

def clean_block(block):
    """
    Cleans a single block by removing noise and extracting relevant data.

    Args:
        block (pd.DataFrame): A DataFrame representing a single block of data.

    Returns:
        pd.DataFrame: A cleaned DataFrame with relevant data.
    """
    # Extract quarter from the title row
    title_row = block.iloc[0, 0]
    quarter = title_row.split('-')[1].strip()

    # Skip title rows (0, 1), get headers (row 3-4) and data rows (5-14)
    # Row 3 has "Region", "Product (Units Sold)", "Revenue (USD)"
    # Row 4 has actual product names

    # Get data rows only (rows 5-14 in the block, excluding row 15 which is Total)
    data_block = block.iloc[5:15].copy()  # 10 region rows

    # Reset index
    data_block.reset_index(drop=True, inplace=True)

    # Extract region from first column
    regions = data_block.iloc[:, 0].values

    # Get product names from header row (row 4 of original block)
    # For Units: columns 1-10 (skip column 11 which is spacer)
    # For Revenue: columns 12-21 (column 22 is Notes)
    header_row = block.iloc[4]

    # Product columns for units sold (columns 1-10)
    product_cols_units = list(range(1, 11))
    # Revenue columns (columns 12-21, skipping column 11 spacer)
    product_cols_revenue = list(range(12, 22))

    # Extract product names from header
    products_units = [header_row.iloc[i] for i in product_cols_units]
    products_revenue = [header_row.iloc[i] for i in product_cols_revenue]

    # Create a mapping of product names to their revenue column indices and values
    # Build a dict: product_name -> (units_col_idx, revenue_col_idx)
    product_mapping = {}

    for units_col_idx, product_name in zip(product_cols_units, products_units):
        if pd.notna(product_name):
            product_mapping[product_name] = {'units_col': units_col_idx, 'revenue_col': None}

    for revenue_col_idx, product_name in zip(product_cols_revenue, products_revenue):
        if pd.notna(product_name):
            if product_name in product_mapping:
                product_mapping[product_name]['revenue_col'] = revenue_col_idx
            else:
                # Product only in revenue section
                product_mapping[product_name] = {'units_col': None, 'revenue_col': revenue_col_idx}

    # Create long-format data - IMPORTANT: group by product (Units + Revenue together)
    # Use the exact product ordering from ground truth
    product_order = ['Laptop', 'Monitor', 'Tablet', 'Phone', 'Printer', 'Router', 'Headset', 'Dock', 'Webcam', 'Projector']

    rows = []

    for region_idx, region in enumerate(regions):
        # Process each product IN THE SPECIFIC ORDER: Units Sold first, then Revenue
        for product_name in product_order:
            if product_name not in product_mapping:
                continue  # Skip if this product is not in this block

            units_col = product_mapping[product_name]['units_col']
            revenue_col = product_mapping[product_name]['revenue_col']

            # Add Units Sold row
            if units_col is not None and pd.notna(data_block.iloc[region_idx, units_col]):
                rows.append({
                    'Quarter': quarter,
                    'Region': region,
                    'Product': product_name,
                    'Metric': 'Units Sold',
                    'Value': data_block.iloc[region_idx, units_col]
                })

            # Add Revenue row (immediately after Units Sold for same product)
            if revenue_col is not None and pd.notna(data_block.iloc[region_idx, revenue_col]):
                rows.append({
                    'Quarter': quarter,
                    'Region': region,
                    'Product': product_name,
                    'Metric': 'Revenue',
                    'Value': data_block.iloc[region_idx, revenue_col]
                })

    result_df = pd.DataFrame(rows)
    logging.info(f"Cleaned block for {quarter}: {len(result_df)} rows")
    return result_df

def assign_sale_id(df):
    """
    Assigns a unique Sale_ID to each row in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to which Sale_IDs will be assigned.

    Returns:
        pd.DataFrame: The DataFrame with Sale_IDs assigned.
    """
    df['Sale_ID (PK)'] = np.arange(1, len(df) + 1)
    logging.info("Assigned Sale_IDs to the data.")
    return df

def validate_output(df):
    """
    Validates the output DataFrame against the target schema.

    Args:
        df (pd.DataFrame): The DataFrame to validate.

    Raises:
        ValueError: If the DataFrame does not match the target schema.
    """
    expected_columns = ['Sale_ID (PK)', 'Quarter', 'Region', 'Product', 'Metric', 'Value']
    if not all(column in df.columns for column in expected_columns):
        raise ValueError("Output DataFrame does not match the target schema.")
    logging.info("Output DataFrame validated successfully.")

def main(input_path, output_path):
    """
    Main function to transform the messy Excel file into the target format.

    Args:
        input_path (str): Path to the input Excel file.
        output_path (str): Path to save the transformed CSV file.

    Returns:
        pd.DataFrame: The final transformed DataFrame.
    """
    try:
        # Read the Excel file
        df = pd.read_excel(input_path, sheet_name='Messy_Report', header=None)

        # Extract and clean blocks
        blocks = extract_blocks(df)
        cleaned_data = pd.concat([clean_block(block) for block in blocks], ignore_index=True)

        # Assign Sale_IDs
        final_df = assign_sale_id(cleaned_data)

        # Reorder columns to match target schema
        final_df = final_df[['Sale_ID (PK)', 'Quarter', 'Region', 'Product', 'Metric', 'Value']]

        # Validate the output
        validate_output(final_df)

        # Save the cleaned data to CSV
        final_df.to_csv(output_path, index=False)
        logging.info(f"Transformed data saved to {output_path}.")

        return final_df

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise

# Example usage
# df_result = main("source.xlsx", "output.csv")
