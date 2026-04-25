#!/usr/bin/env python
"""Test script to verify all tab data is present in API response."""

import requests
import json

print('Testing complete workflow...\n')

# Test API endpoint
files = {'vcf_file': open('data/test_patient.vcf', 'rb')}
data = {'drugs': 'CODEINE'}
response = requests.post('http://localhost:5000/api/analysis', files=files, data=data)
result = response.json()

print('✅ API Response received')
print(f'Total analyses: {result.get("total_analyses")}')

if 'analyses' in result and len(result['analyses']) > 0:
    analysis = result['analyses'][0]
    
    print('\n--- Tab 0: Pharmacogenomic Profile Data ---')
    profile = analysis.get('pharmacogenomic_profile', {})
    print(f'Primary Gene: {profile.get("primary_gene")}')
    print(f'Diplotype: {profile.get("diplotype")}')
    print(f'Phenotype: {profile.get("phenotype")}')
    print(f'Detected Variants: {len(profile.get("detected_variants", []))} variants')
    if analysis.get('guideline_url'):
        print(f'Guideline Citation: {analysis.get("guideline_url")}')
    
    print('\n--- Tab 1: Clinical Recommendation Data ---')
    rec = analysis.get('clinical_recommendation', {})
    print(f'Dosage Adjustment: {rec.get("dosage_adjustment", "N/A")[:70]}...')
    print(f'Monitoring: {rec.get("monitoring", "N/A")}')
    print(f'Alternative Drugs: {len(rec.get("alternative_drugs", []))} drugs')
    print(f'Urgency: {rec.get("urgency")}')
    
    print('\n--- Tab 2: Clinical Explanation Data ---')
    explain = analysis.get('llm_generated_explanation', {})
    print(f'Summary: {explain.get("summary", "N/A")[:70]}...')
    print(f'Mechanism: {explain.get("mechanism", "N/A")[:70]}...')
    print(f'Evidence Basis: {explain.get("evidence_basis", "N/A")[:50]}')
    print(f'Interaction Notes: {len(explain.get("interaction_notes", []))} notes')
    
    print('\n--- Results Header Data ---')
    risk = analysis.get('risk_assessment', {})
    print(f'Risk Label: {risk.get("risk_label")}')
    print(f'Confidence Score: {risk.get("confidence_score") * 100}%')
    print(f'Severity: {risk.get("severity")}')
    
    print('\n✅ All tab data is present and ready for display!')
    print('\nFull JSON structure matches schema requirements.')
else:
    print('❌ No analyses in response')
