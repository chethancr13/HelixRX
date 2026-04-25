def parse_vcf(file) -> dict:
    """
    Parse a VCF v4.2 file and extract pharmacogenomic variants.
    
    Parameters:
    -----------
    file : file-like object
        The VCF file uploaded via Flask (e.g., file from request.files)
        
    Returns:
    --------
    dict
        Structure:
        {
            "vcf_parsing_success": True/False,
            "patient_id": "...",
            "variants": {
                "CYP2D6": [{"rsid": "rs...", "star": "*4"}, ...],
                "CYP2C19": [...],
                ...
            },
            "error": "..." (if parsing failed)
        }
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
    
    # Result structure
    result = {
        "vcf_parsing_success": False,
        "patient_id": None,
        "variants": {}
    }
    
    try:
        # Read entire file content to check if empty
        content = file.read()
        if not content:
            result["error"] = "VCF file is empty"
            return result
        
        # Reset file pointer for re-reading
        if hasattr(file, 'seek'):
            file.seek(0)
        else:
            # If can't seek, recreate from content
            from io import BytesIO
            file = BytesIO(content)
        
        # Initialize gene dictionaries
        for gene in SUPPORTED_GENES:
            result["variants"][gene] = []
        
        # Track file validation
        has_vcf_header = False
        has_column_header = False
        has_data_lines = False
        total_variants_found = 0
        line_count = 0
        
        # Read file line by line
        for line in file:
            line_count += 1
            
            # Handle both bytes and string
            if isinstance(line, bytes):
                line = line.decode('utf-8').strip()
            else:
                line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check for VCF header
            if line.startswith("##fileformat=VCF"):
                has_vcf_header = True
                continue
            
            # Check for column header line
            if line.startswith("#CHROM"):
                has_column_header = True
                header_fields = line.split('\t')
                if len(header_fields) > 9:
                    result["patient_id"] = header_fields[9].strip()
                continue
            
            # Skip other metadata lines
            if line.startswith("#"):
                continue
            
            # Data line found
            has_data_lines = True
            
            try:
                # Parse VCF line
                fields = line.split('\t')
                
                # VCF standard format: CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO, ...
                if len(fields) < 8:
                    continue
                
                info_field = fields[7]
                format_field = fields[8] if len(fields) > 8 else ""
                sample_field = fields[9] if len(fields) > 9 else ""
                
                # Parse INFO field (KEY=VALUE;KEY=VALUE;...)
                info_dict = {}
                for info_pair in info_field.split(';'):
                    if '=' in info_pair:
                        key, value = info_pair.split('=', 1)
                        info_dict[key] = value
                    else:
                        info_dict[info_pair] = True
                
                # Extract required fields
                gene = info_dict.get("GENE", "").upper()
                rsid = info_dict.get("RS", "")
                star = info_dict.get("STAR", "")

                # Skip reference-only genotypes when possible
                if format_field and sample_field:
                    format_keys = format_field.split(':')
                    sample_values = sample_field.split(':')
                    format_map = dict(zip(format_keys, sample_values))
                    genotype = format_map.get("GT")
                    if genotype and genotype in {"0/0", "0|0"}:
                        continue
                
                # Only process if gene is supported
                if gene not in SUPPORTED_GENES:
                    continue
                
                # Build variant object
                variant = {}
                
                if rsid:
                    variant["rsid"] = rsid
                
                if star:
                    variant["star"] = star
                
                # Only add if we have at least rsid or star
                if variant:
                    result["variants"][gene].append(variant)
                    total_variants_found += 1
            
            except Exception as e:
                # Skip malformed lines
                continue
        
        # Validation checks
        if line_count == 0:
            result["error"] = "VCF file is empty - no lines found"
            return result
        
        if not has_vcf_header:
            result["error"] = "Invalid VCF file - missing '##fileformat=VCFv4.2' header"
            return result
        
        if not has_column_header:
            result["error"] = "Invalid VCF file - missing '#CHROM' column header line"
            return result
        
        if not has_data_lines:
            result["error"] = "VCF file has no data lines - only headers present"
            return result
        
        if total_variants_found == 0:
            result["error"] = "No pharmacogenomic variants found in VCF file for supported genes (CYP2D6, CYP2C19, CYP2C9, SLCO1B1, TPMT, DPYD)"
            return result
        
        result["vcf_parsing_success"] = True
        
    except Exception as e:
        # Catch any unexpected errors during file reading
        print(f"Error parsing VCF file: {e}")
        result["vcf_parsing_success"] = False
        result["error"] = str(e)
    
    return result
