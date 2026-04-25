"""
Alternative drugs recommendation engine with clinical reasoning.
Maps drugs to their alternatives based on phenotype and genetic metabolism.
"""

DRUG_ALTERNATIVES = {
    "CODEINE": {
        "alternatives": [
            {
                "drug": "TRAMADOL",
                "reason": "Tramadol has less reliance on CYP2D6 metabolism, making it safer for poor metabolizers",
                "suitable_for": ["PM", "IM"]
            },
            {
                "drug": "MORPHINE",
                "reason": "Direct opioid bypassing CYP2D6 metabolism, better for poor metabolizers",
                "suitable_for": ["PM"]
            },
            {
                "drug": "FENTANYL",
                "reason": "Minimal CYP2D6 dependency, effective for ultra-rapid metabolizers requiring lower doses",
                "suitable_for": ["URM"]
            }
        ]
    },
    "WARFARIN": {
        "alternatives": [
            {
                "drug": "APIXABAN",
                "reason": "Direct-acting anticoagulant with minimal CYP2C9 metabolism, better for poor metabolizers",
                "suitable_for": ["PM", "IM"]
            },
            {
                "drug": "DABIGATRAN",
                "reason": "Direct-acting anticoagulant not dependent on CYP2C9, consistent dosing for rapid metabolizers",
                "suitable_for": ["RM", "URM"]
            },
            {
                "drug": "RIVAROXABAN",
                "reason": "DOAC with predictable pharmacokinetics independent of CYP2C9 metabolism",
                "suitable_for": ["PM", "IM", "RM", "URM"]
            }
        ]
    },
    "CLOPIDOGREL": {
        "alternatives": [
            {
                "drug": "PRASUGREL",
                "reason": "Less dependent on CYP2C19, more reliable antiplatelet effect for poor metabolizers",
                "suitable_for": ["PM", "IM"]
            },
            {
                "drug": "TICAGRELOR",
                "reason": "Not reliant on CYP2C19 activation, consistent response across all metabolizer types",
                "suitable_for": ["PM", "IM", "RM", "URM"]
            }
        ]
    },
    "SIMVASTATIN": {
        "alternatives": [
            {
                "drug": "PRAVASTATIN",
                "reason": "Not metabolized by SLCO1B1, safer option for patients with reduced SLCO1B1 function",
                "suitable_for": ["PM", "IM"]
            },
            {
                "drug": "ROSUVASTATIN",
                "reason": "Minimal SLCO1B1 metabolism, predictable lipid-lowering effects",
                "suitable_for": ["PM", "IM"]
            },
            {
                "drug": "FLUVASTATIN",
                "reason": "Lower SLCO1B1 dependence, alternative for patients with transporter variants",
                "suitable_for": ["PM", "IM"]
            }
        ]
    },
    "AZATHIOPRINE": {
        "alternatives": [
            {
                "drug": "MYCOPHENOLATE",
                "reason": "TPMT-independent immunosuppressant, safe for poor metabolizers",
                "suitable_for": ["PM"]
            },
            {
                "drug": "TACROLIMUS",
                "reason": "Alternative immunosuppressant not dependent on TPMT metabolism",
                "suitable_for": ["PM", "IM"]
            }
        ]
    },
    "FLUOROURACIL": {
        "alternatives": [
            {
                "drug": "CAPECITABINE",
                "reason": "Prodrug with built-in safety monitoring for DPYD deficiency",
                "suitable_for": ["PM", "IM"]
            },
            {
                "drug": "TEGAFUR",
                "reason": "Alternative fluoropyrimidine with dose adjustment for poor DPYD metabolizers",
                "suitable_for": ["PM", "IM"]
            }
        ]
    }
}


def get_alternatives_for_drug_phenotype(drug: str, phenotype: str) -> list:
    """
    Get alternative drug recommendations based on drug and patient phenotype.
    
    Parameters:
    -----------
    drug : str
        Drug name (uppercase)
    phenotype : str
        Metabolic phenotype (PM, IM, NM, RM, URM, Unknown)
    
    Returns:
    --------
    list
        List of alternative drug objects with explanations
    """
    
    if drug not in DRUG_ALTERNATIVES:
        return []
    
    alternatives = DRUG_ALTERNATIVES[drug]["alternatives"]
    
    # Filter alternatives suitable for this phenotype
    suitable = [
        alt for alt in alternatives 
        if phenotype in alt.get("suitable_for", [])
    ]
    
    return suitable


def build_alternatives_list(drug: str, phenotype: str, risk_label: str) -> list:
    """
    Build a list of alternatives with reasoning for display.
    Uses both phenotype matching and risk classification.
    
    Parameters:
    -----------
    drug : str
        Drug name (uppercase)
    phenotype : str
        Metabolic phenotype
    risk_label : str
        Risk assessment (Safe, Adjust Dosage, Toxic, Ineffective, Unknown)
    
    Returns:
    --------
    list
        Formatted list of alternatives with explanations
    """
    
    # Only suggest alternatives for problematic phenotypes
    risky_phenotypes = ["PM", "URM"]
    risky_risks = ["Toxic", "Ineffective", "Adjust Dosage"]
    
    if phenotype not in risky_phenotypes and risk_label not in risky_risks:
        return []
    
    alternatives = get_alternatives_for_drug_phenotype(drug, phenotype)
    
    # Format for display
    formatted = [
        {
            "drug_name": alt["drug"],
            "reason": alt["reason"],
            "why_suitable": f"Recommended for {phenotype} patients: {alt['reason']}"
        }
        for alt in alternatives
    ]
    
    return formatted
