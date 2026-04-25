import pandas as pd
from pathlib import Path


def load_cpic_data(filepath: str) -> dict:
    """
    Load CPIC data from an Excel file.
    
    Parameters:
    -----------
    filepath : str
        Path to the Excel file containing CPIC data
        
    Returns:
    --------
    dict
        Dictionary with drug names (uppercase) as keys and gene/cpic_level as values
        Example: {"CODEINE": {"gene": "CYP2D6", "cpic_level": "A"}}
        
    Raises:
    -------
    FileNotFoundError
        If the Excel file does not exist
    ValueError
        If required columns (Drug, Gene) are missing from the file
    """
    
    # Convert to Path object for better file handling
    file_path = Path(filepath)
    
    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(f"Excel file not found: {filepath}")
    
    # Load the Excel file
    try:
        df = pd.read_excel(filepath)
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {e}")
    
    # Check for required columns
    required_columns = {"Drug", "Gene"}
    available_columns = set(df.columns)
    
    if not required_columns.issubset(available_columns):
        missing = required_columns - available_columns
        raise ValueError(f"Required columns missing: {missing}. Available columns: {available_columns}")
    
    # Initialize result dictionary
    cpic_data = {}
    
    # Process each row
    for idx, row in df.iterrows():
        drug = row["Drug"]
        gene = row["Gene"]
        
        # Skip rows with missing Drug or Gene
        if pd.isna(drug) or pd.isna(gene):
            continue
        
        # Convert drug name to uppercase and strip whitespace
        drug_key = str(drug).strip().upper()
        gene_value = str(gene).strip()
        
        # Build the entry
        entry = {"gene": gene_value}
        
        # Add CPIC Level if it exists and is not null
        if "CPIC Level" in df.columns and pd.notna(row["CPIC Level"]):
            entry["cpic_level"] = str(row["CPIC Level"]).strip()
        
        cpic_data[drug_key] = entry
    
    # Print confirmation message
    print(f"Loaded {len(cpic_data)} drugs from CPIC data")
    
    return cpic_data
