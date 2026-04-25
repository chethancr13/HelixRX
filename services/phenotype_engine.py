def determine_phenotype(gene: str, variants: list) -> dict:
    """
    Determine metabolic phenotype from STAR alleles and build diplotype.
    
    Parameters:
    -----------
    gene : str
        Gene name (e.g., "CYP2D6")
    variants : list
        List of variant dictionaries with STAR alleles
        Example: [{"rsid": "rs3892097", "star": "*4"}, ...]
        
    Returns:
    --------
    dict
        Structure:
        {
            "gene": "CYP2D6",
            "diplotype": "*4/*10",
            "phenotype": "IM",
            "confidence": "high" or "low"
        }
    """
    
    # Phenotype map for all supported genes
    PHENOTYPE_MAP = {
        "CYP2D6": {
            "*1/*1": "NM",
            "*1/*2": "NM",
            "*1/*3": "IM",
            "*1/*4": "IM",
            "*1/*5": "IM",
            "*1/*6": "IM",
            "*1/*10": "IM",
            "*1/*41": "IM",
            "*2/*2": "NM",
            "*3/*4": "PM",
            "*4/*4": "PM",
            "*4/*5": "PM",
            "*4/*6": "PM",
            "*4/*10": "IM",
            "*5/*5": "PM",
            "*41/*41": "NM",
            # Wildcard patterns for combinations
        },
        "CYP2C19": {
            "*1/*1": "NM",
            "*1/*2": "IM",
            "*1/*3": "IM",
            "*2/*2": "PM",
            "*2/*3": "PM",
            "*3/*3": "PM",
        },
        "CYP2C9": {
            "*1/*1": "NM",
            "*1/*2": "IM",
            "*1/*3": "IM",
            "*2/*2": "IM",
            "*2/*3": "PM",
            "*3/*3": "PM",
        },
        "SLCO1B1": {
            "*1/*1": "NM",
            "*1/*5": "IM",
            "*5/*5": "PM",
        },
        "TPMT": {
            "*1/*1": "NM",
            "*1/*3": "IM",
            "*3/*3": "PM",
        },
        "DPYD": {
            "*1/*1": "NM",
            "*1/*2": "IM",
            "*2/*2": "PM",
        }
    }
    
    # Normalize gene name
    gene = str(gene).strip().upper()
    
    # Result structure
    result = {
        "gene": gene,
        "diplotype": None,
        "phenotype": "Unknown",
        "confidence": "low"
    }
    
    try:
        # Handle empty variants list
        if not variants or not isinstance(variants, list):
            result["phenotype"] = "No variants detected"
            return result
        
        # Extract STAR alleles from variants
        star_alleles = []
        for variant in variants:
            if isinstance(variant, dict):
                star = variant.get("star")
                if star:
                    star_alleles.append(str(star).strip())
        
        # Handle no alleles found
        if not star_alleles:
            result["phenotype"] = "No variants detected"
            return result
        
        # Build diplotype candidates
        gene_phenotype_map = PHENOTYPE_MAP.get(gene, {})

        unique_alleles = []
        for allele in star_alleles:
            if allele not in unique_alleles:
                unique_alleles.append(allele)

        def phenotype_rank(label: str) -> int:
            ranking = {
                "PM": 5,
                "IM": 4,
                "NM": 3,
                "RM": 2,
                "URM": 1
            }
            return ranking.get(label, 0)

        def pick_best_diplotype(alleles: list) -> tuple:
            candidates = []
            if len(alleles) == 1:
                candidates.append((alleles[0], alleles[0]))
            else:
                for i in range(len(alleles)):
                    for j in range(i + 1, len(alleles)):
                        candidates.append((alleles[i], alleles[j]))

            best = None
            best_label = None
            for a1, a2 in candidates:
                direct = f"{a1}/{a2}"
                reverse = f"{a2}/{a1}"
                if direct in gene_phenotype_map:
                    label = gene_phenotype_map[direct]
                    if not best or phenotype_rank(label) > phenotype_rank(best_label):
                        best = direct
                        best_label = label
                if reverse in gene_phenotype_map:
                    label = gene_phenotype_map[reverse]
                    if not best or phenotype_rank(label) > phenotype_rank(best_label):
                        best = reverse
                        best_label = label

            return best, best_label

        diplotype, phenotype_label = pick_best_diplotype(unique_alleles)

        if not diplotype:
            if len(unique_alleles) >= 2:
                diplotype = f"{unique_alleles[0]}/{unique_alleles[1]}"
                result["confidence"] = "medium"
            else:
                allele = unique_alleles[0]
                diplotype = f"{allele}/{allele}"
                result["confidence"] = "medium"

        result["diplotype"] = diplotype

        if phenotype_label:
            result["phenotype"] = phenotype_label
            result["confidence"] = "high"
        else:
            result["phenotype"] = "Unknown"
            result["confidence"] = "low"
        
        return result
    
    except Exception as e:
        # Catch any unexpected errors
        result["phenotype"] = "Unknown"
        result["error"] = str(e)
        return result
