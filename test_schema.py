#!/usr/bin/env python
"""Test script to verify JSON schema compliance"""

import json
import requests
import time

print("=" * 80)
print("TESTING COMPLETE JSON SCHEMA COMPLIANCE")
print("=" * 80)

# Read a test VCF file
with open('data/sample_normal_metabolizer.vcf', 'rb') as f:
    vcf_content = f.read()

# Prepare test data with correct parameter name
drugs_list = ['CODEINE', 'WARFARIN', 'SIMVASTATIN']

print("\n[1] Uploading VCF file and analyzing...")
print(f"    Drugs to analyze: {drugs_list}")

try:
    response = requests.post(
        'http://127.0.0.1:5000/api/analysis',
        data={'drugs': ','.join(drugs_list)},  # Corrected parameter name
        files={'vcf_file': ('test.vcf', vcf_content)},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Request successful")
        
        # Print the full response
        print("\n[2] Complete Response Output:")
        print("-" * 80)
        print(json.dumps(result, indent=2))
        print("-" * 80)
        
        # Validate schema for each analysis
        print("\n[3] Schema Validation:")
        required_top_level = ['total_analyses', 'analyses']
        required_analysis_fields = [
            'patient_id',
            'drug',
            'timestamp',
            'risk_assessment',
            'pharmacogenomic_profile',
            'clinical_recommendation',
            'llm_generated_explanation',
            'quality_metrics'
        ]
        
        required_llm_fields = [
            'summary',
            'mechanism',
            'interaction_notes',
            'evidence_basis'
        ]
        
        # Check top-level
        for field in required_top_level:
            if field in result:
                print(f"✓ {field}")
            else:
                print(f"✗ MISSING: {field}")
        
        print("\nAnalyzing individual records:")
        for i, analysis in enumerate(result.get('analyses', []), 1):
            print(f"\n  Analysis #{i} ({analysis.get('drug')}):")
            
            # Check all required fields
            for field in required_analysis_fields:
                if field in analysis:
                    print(f"    ✓ {field}")
                else:
                    print(f"    ✗ MISSING: {field}")
            
            # Check LLM explanation fields
            llm_exp = analysis.get('llm_generated_explanation', {})
            print(f"    LLM Explanation Fields:")
            for field in required_llm_fields:
                if field in llm_exp:
                    value = llm_exp[field]
                    if isinstance(value, list):
                        print(f"      ✓ {field}: ({len(value)} items)")
                    else:
                        print(f"      ✓ {field}: {len(str(value))} chars")
                else:
                    print(f"      ✗ MISSING: {field}")
        
        print("\n" + "=" * 80)
        print("TESTING COMPLETE")
        print("=" * 80)
        
    else:
        print(f"✗ Request failed with status {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"✗ Error: {e}")
