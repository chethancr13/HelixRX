def match_drug_with_vcf(drug: str, vcf_data: dict, cpic_engine: dict, allow_gemini_fallback: bool = True) -> dict:
    """
    Match a user-input drug with CPIC gene and check if gene variants exist in VCF data.
    If drug not in CPIC, mark for Gemini fallback analysis.
    
    Parameters:
    -----------
    drug : str
        Drug name to match
    vcf_data : dict
        Parsed VCF data from vcf_parser.parse_vcf()
        Expected structure: {"vcf_parsing_success": bool, "variants": {...}}
    cpic_engine : dict
        CPIC data from cpic_engine.initialize_cpic_engine()
        Expected structure: {"DRUG": {"gene": "GENE", "cpic_level": "LEVEL", ...}}
    allow_gemini_fallback : bool
        If True, mark drug for Gemini fallback when not in CPIC (instead of error)
        
    Returns:
    --------
    dict
        Structure:
        {
            "drug": "CODEINE",
            "valid": True/False,
            "gene": "CYP2D6",
            "cpic_level": "A",
            "guideline_url": "...",
            "gene_found_in_vcf": True/False,
            "variant_count": 0,
            "gemini_fallback": False,  # True if drug not in CPIC but allowed
            "error": "..." (if valid is False)
        }
    """
    
    # Result structure
    result = {
        "drug": "",
        "valid": False,
        "gene": None,
        "cpic_level": None,
        "guideline_url": None,
        "gene_found_in_vcf": False,
        "variant_count": 0,
        "gemini_fallback": False
    }
    
    try:
        # Normalize drug name
        drug_normalized = str(drug).strip().upper()
        result["drug"] = drug_normalized
        
        # Check if drug exists in CPIC engine
        if drug_normalized not in cpic_engine:
            # Allow fallback to Gemini for unsupported drugs
            if allow_gemini_fallback:
                result["valid"] = True
                result["gemini_fallback"] = True
                result["error"] = f"Drug not in CPIC database - will use Gemini for analysis"
                return result
            else:
                result["error"] = "Drug not found in CPIC dataset"
                return result
        
        # Get drug data from CPIC engine
        drug_data = cpic_engine[drug_normalized]
        
        # Extract gene information
        gene = drug_data.get("gene")
        cpic_level = drug_data.get("cpic_level")
        guideline_url = drug_data.get("guideline_url")
        
        # Update result
        result["valid"] = True
        result["gene"] = gene
        result["cpic_level"] = cpic_level
        result["guideline_url"] = guideline_url
        
        # Check if VCF data is valid
        if not isinstance(vcf_data, dict):
            result["error"] = "Invalid VCF data format"
            result["valid"] = False
            return result
        
        # Check if parsing was successful
        vcf_success = vcf_data.get("vcf_parsing_success", False)
        if not vcf_success:
            result["error"] = vcf_data.get("error", "VCF parsing failed")
            result["valid"] = False
            return result
        
        # Get variants from VCF data
        variants = vcf_data.get("variants", {})
        
        # Check if gene exists in VCF variants
        if gene and gene in variants:
            result["gene_found_in_vcf"] = True
            variant_list = variants[gene]
            
            # Count variants for this gene
            if isinstance(variant_list, list):
                result["variant_count"] = len(variant_list)
        
        return result
    
    except Exception as e:
        # Catch any unexpected errors
        result["valid"] = False
        result["error"] = f"Error matching drug with VCF: {str(e)}"
        result["drug"] = str(drug).strip().upper()
        return result
