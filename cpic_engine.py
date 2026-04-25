from services.cpic_loader import load_cpic_data


SUPPORTED_DRUGS = [
    "CODEINE",
    "WARFARIN",
    "CLOPIDOGREL",
    "SIMVASTATIN",
    "AZATHIOPRINE",
    "FLUOROURACIL"
]

# Note: If a drug is not found in CPIC data, Gemini LLM will be used for analysis


def initialize_cpic_engine(filepath: str) -> dict:
    """
    Initialize the CPIC engine by loading and filtering supported drugs.
    
    Parameters:
    -----------
    filepath : str
        Path to the Excel file containing CPIC data
        
    Returns:
    --------
    dict
        Dictionary containing only supported drugs with their gene/cpic_level data
        Example: {"CODEINE": {"gene": "CYP2D6", "cpic_level": "A"}}
    """
    
    # Supported pharmacogenomic genes
    SUPPORTED_GENES = {
        "CYP2D6",
        "CYP2C19",
        "CYP2C9",
        "SLCO1B1",
        "TPMT",
        "DPYD"
    }
    
    # Load all CPIC data
    all_cpic_data = load_cpic_data(filepath)
    
    # Filter to only supported drugs
    supported_cpic_data = {}
    
    for drug in SUPPORTED_DRUGS:
        if drug in all_cpic_data:
            drug_info = all_cpic_data[drug]
            gene = drug_info.get("gene", "").upper()
            
            # Only include if gene is in supported genes
            if gene in SUPPORTED_GENES:
                supported_cpic_data[drug] = drug_info
    
    # Check for missing drugs
    loaded_drugs = set(supported_cpic_data.keys())
    supported_set = set(SUPPORTED_DRUGS)
    missing_drugs = supported_set - loaded_drugs
    
    if missing_drugs:
        print(f"Warning: Missing drugs from CPIC dataset: {', '.join(sorted(missing_drugs))}")
    
    # Print confirmation message
    print(f"Loaded {len(supported_cpic_data)} supported drugs from CPIC dataset.")
    
    return supported_cpic_data
