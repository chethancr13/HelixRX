#!/usr/bin/env python
"""Compare actual API output with required schema."""

import requests
import json

# Test the API
files = {'vcf_file': open('data/test_patient.vcf', 'rb')}
data = {'drugs': 'CODEINE'}
response = requests.post('http://localhost:5000/api/analysis', files=files, data=data)
actual = response.json()

print("=== REQUIRED SCHEMA ===")
required_schema = {
    "patient_id": "PATIENT_XXX",
    "drug": "DRUG_NAME",
    "timestamp": "ISO8601_timestamp",
    "risk_assessment": {
        "risk_label": "Safe|Adjust Dosage|Toxic|...",
        "confidence_score": 0.0,
        "severity": "none|low|moderate|high|critical"
    },
    "pharmacogenomic_profile": {
        "primary_gene": "GENE_SYMBOL",
        "diplotype": "*X/*Y",
        "phenotype": "PM|IM|NM|RM|URM|Unknown",
        "detected_variants": [{"rsid": "rsXXXX"}]
    },
    "clinical_recommendation": {},
    "llm_generated_explanation": {"summary": "..."},
    "quality_metrics": {"vcf_parsing_success": True}
}
print(json.dumps(required_schema, indent=2))

print("\n=== ACTUAL API OUTPUT (First Analysis) ===")
if 'analyses' in actual and len(actual['analyses']) > 0:
    # Show just the structure with truncated values
    analysis = actual['analyses'][0]
    structure = {}
    for key, value in analysis.items():
        if isinstance(value, dict):
            structure[key] = {k: type(v).__name__ for k, v in value.items()}
        elif isinstance(value, list):
            structure[key] = f"[{len(value)} items]"
        else:
            structure[key] = type(value).__name__
    print(json.dumps(structure, indent=2))
    
    print("\n=== FIELD COMPARISON ===")
    required_fields = set(required_schema.keys())
    actual_fields = set(analysis.keys())
    
    print(f"✅ Required fields present: {required_fields.intersection(actual_fields)}")
    missing = required_fields - actual_fields
    if missing:
        print(f"❌ Missing fields: {missing}")
    else:
        print("✅ All required fields present!")
    
    extra = actual_fields - required_fields
    if extra:
        print(f"✓ Bonus fields: {extra}")
    
    print("\n=== FULL ACTUAL RESPONSE ===")
    print(json.dumps(actual, indent=2))
else:
    print("❌ No analyses in response")
