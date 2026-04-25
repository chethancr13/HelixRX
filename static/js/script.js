// Toast notification function
function showToast(message, type = 'error') {
    const toastContainer = document.createElement('div');
    toastContainer.className = `toast ${type}`;
    
    // Add icon
    let icon = '⚠️';
    if (type === 'success') icon = '✓';
    if (type === 'error') icon = '✕';
    
    toastContainer.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${message}</span>
    `;
    
    document.body.appendChild(toastContainer);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        toastContainer.classList.add('removing');
        setTimeout(() => {
            toastContainer.remove();
        }, 300);
    }, 4000);
}

document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.querySelector('.btn-primary');
    const drugsInput = document.getElementById('enter-drugs');
    const vcfInput = document.getElementById('vcf-upload');
    const jsonDataElement = document.getElementById('json-data');
    const copyBtn = document.getElementById('copy');
    const downloadBtn = document.getElementById('download');
    const suggestedDrugsSelect = document.getElementById('suggested-drugs');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const resultsHeader = document.getElementById('results-header');
    const uploadArea = document.querySelector('.upload-area');
    
    let currentResponse = null; // Store current response for tab display
    
    // Drag-and-drop functionality
    if (uploadArea) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        // Highlight drop area when dragging over it
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight(e) {
            uploadArea.classList.add('drag-over');
        }
        
        function unhighlight(e) {
            uploadArea.classList.remove('drag-over');
        }
        
        // Handle dropped files
        uploadArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                // Update the file input
                vcfInput.files = files;
                
                // Update UI to show filename
                const fileName = files[0].name;
                const uploadText = uploadArea.querySelector('.upload-text');
                if (uploadText) {
                    uploadText.innerHTML = `<strong>${fileName}</strong><br/>(Max. size of 5MB)`;
                }
            }
        }
    }
    
    // Handle suggested drugs selection
    if (suggestedDrugsSelect) {
        suggestedDrugsSelect.addEventListener('change', function() {
            const currentValue = drugsInput.value.trim();
            const selectedDrug = this.value;
            
            if (currentValue && !currentValue.includes(selectedDrug)) {
                drugsInput.value = currentValue + ', ' + selectedDrug;
            } else if (!currentValue) {
                drugsInput.value = selectedDrug;
            }
        });
    }
    
    // Update upload area text when file is selected via click
    if (vcfInput) {
        vcfInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                const fileName = this.files[0].name;
                const uploadText = uploadArea.querySelector('.upload-text');
                if (uploadText) {
                    uploadText.innerHTML = `<strong>${fileName}</strong><br/>(Max. size of 5MB)`;
                }
            }
        });
    }
    
    // Handle analyze button click
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            // Get drug input
            const drugs = drugsInput.value.trim();
            if (!drugs) {
                showToast('Please enter at least one drug name', 'error');
                return;
            }
            
            // Get VCF file
            const vcfFile = vcfInput.files[0];
            if (!vcfFile) {
                showToast('Please select a VCF file', 'error');
                return;
            }
            
            // Check file type
            if (!vcfFile.name.endsWith('.vcf')) {
                showToast('Please upload a proper .vcf file', 'error');
                return;
            }
            
            // Check file size (5MB max)
            const maxSize = 5 * 1024 * 1024; // 5MB in bytes
            if (vcfFile.size > maxSize) {
                showToast('File size exceeds 5MB. Please upload a proper file.', 'error');
                return;
            }
            
            // Create FormData
            const formData = new FormData();
            formData.append('vcf_file', vcfFile);
            formData.append('drugs', drugs);
            
            // Show loading state
            analyzeBtn.disabled = true;
            const originalText = analyzeBtn.textContent;
            analyzeBtn.textContent = 'Analyzing...';
            
            try {
                // Send POST request to /api/analysis
                const response = await fetch('/api/analysis', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.analyses && data.analyses.length > 0) {
                        const allResponses = data.analyses;
                        
                        // Store the first response for tab display
                        currentResponse = allResponses[0];
                        
                        // Display results header and populate it
                        if (resultsHeader) {
                            resultsHeader.style.display = 'block';
                            
                            // Populate results header with actual data
                            const riskLabel = currentResponse.risk_assessment?.risk_label || '-';
                            const confidence = currentResponse.risk_assessment?.confidence_score || 0;
                            const severity = currentResponse.risk_assessment?.severity || '-';
                            
                            // Update severity
                            const severityEl = document.getElementById('severity');
                            if (severityEl) {
                                const severityText = severity.charAt(0).toUpperCase() + severity.slice(1);
                                severityEl.textContent = `Intake Severity: ${severityText}`;
                            }
                            
                            // Update risk label badge color based on risk
                            const riskLabelEl = document.getElementById('risk-label');
                            if (riskLabelEl) {
                                riskLabelEl.textContent = `Drug Intake: ${riskLabel}`;
                                riskLabelEl.className = 'badge-' + riskLabel.toLowerCase().replace(/\s+/g, '-');
                            }
                            
                            // Update confidence
                            const confidenceEl = document.getElementById('confidence');
                            if (confidenceEl) {
                                const confidencePercent = (confidence * 100).toFixed(1);
                                confidenceEl.textContent = `Model Confidence: ${confidencePercent}%`;
                            }
                        }
                        
                        // Populate tab content
                        populateTabs(currentResponse);
                        
                        // Show first tab by default
                        activateTab(0);
                        
                        // If multiple drugs, display them as an array
                        let displayData;
                        if (allResponses.length === 1) {
                            displayData = allResponses[0];
                        } else {
                            displayData = {
                                "total_analyses": allResponses.length,
                                "analyses": allResponses
                            };
                        }
                        
                        // Update JSON display
                        jsonDataElement.textContent = JSON.stringify(displayData, null, 2);
                        console.log('Analysis successful:', data);
                    } else {
                        jsonDataElement.textContent = JSON.stringify(data, null, 2);
                    }
                } else {
                    const errorData = await response.json();
                    const errorMessage = errorData.error || 'Analysis failed';
                    jsonDataElement.textContent = JSON.stringify({
                        error: errorMessage,
                        details: errorData.details || 'Unknown error'
                    }, null, 2);
                    showToast(errorMessage + ' - Please upload a proper file', 'error');
                }
            } catch (error) {
                const errorObj = {
                    error: 'Network error',
                    message: error.message
                };
                jsonDataElement.textContent = JSON.stringify(errorObj, null, 2);
                showToast('Error: ' + error.message, 'error');
                console.error('Error:', error);
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = originalText;
            }
        });
    }
    
    // Copy to clipboard functionality
    if (copyBtn) {
        copyBtn.addEventListener('click', function() {
            const jsonText = jsonDataElement.textContent;
            
            navigator.clipboard.writeText(jsonText).then(() => {
                // Show feedback
                const originalTitle = copyBtn.title || 'Copy to clipboard';
                copyBtn.title = 'Copied!';
                setTimeout(() => {
                    copyBtn.title = originalTitle;
                }, 1500);
            }).catch(err => {
                alert('Failed to copy to clipboard');
                console.error('Copy failed:', err);
            });
        });
    }
    
    // Download JSON functionality
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            const jsonText = jsonDataElement.textContent;
            
            // Create blob
            const blob = new Blob([jsonText], { type: 'application/json' });
            
            // Create download link
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'pharmacogenomic_analysis.json';
            
            // Trigger download
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // Clean up
            URL.revokeObjectURL(url);
        });
    }
    
    // Tab switching functionality
    tabButtons.forEach((btn, index) => {
        btn.addEventListener('click', function() {
            activateTab(index);
        });
    });
    
    // Function to activate a tab
    function activateTab(tabIndex) {
        // Remove active class from all buttons
        tabButtons.forEach(btn => btn.classList.remove('active'));
        
        // Hide all tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = 'none';
        });
        
        // Activate selected button
        if (tabButtons[tabIndex]) {
            tabButtons[tabIndex].classList.add('active');
        }
        
        // Show selected tab content
        const tabContent = document.getElementById(`tab-content-${tabIndex}`);
        if (tabContent) {
            tabContent.style.display = 'block';
        }
    }
    
    // Function to populate tabs with response data
    function populateTabs(response) {
        if (!response) return;
        
        // Tab 0: Pharmacogenomic Profile
        const pharmaProfile = response.pharmacogenomic_profile || {};
        const pharmaContent = document.getElementById('pharma-profile-content');
        if (pharmaContent) {
            let profileHtml = '<div style="padding: 10px;">';
            profileHtml += `<p><strong>Primary Gene:</strong> ${pharmaProfile.primary_gene || 'N/A'}</p>`;
            profileHtml += `<p><strong>Diplotype:</strong> ${pharmaProfile.diplotype || 'N/A'}</p>`;
            profileHtml += `<p><strong>Phenotype:</strong> ${pharmaProfile.phenotype || 'N/A'}</p>`;
            
            if (pharmaProfile.detected_variants && Array.isArray(pharmaProfile.detected_variants)) {
                profileHtml += '<p><strong>Detected Variants:</strong></p><ul>';
                pharmaProfile.detected_variants.forEach(variant => {
                    profileHtml += `<li>${variant.rsid || 'Unknown'}: ${variant.star || 'Unknown'}</li>`;
                });
                profileHtml += '</ul>';
            }
            
            // Add guideline citation if available
            if (response.guideline_url) {
                profileHtml += '<hr style="margin: 15px 0;">';
                profileHtml += '<p><strong>Clinical Guideline Citation:</strong></p>';
                profileHtml += `<p><a href="${response.guideline_url}" target="_blank" rel="noopener noreferrer" style="color: #0066cc; text-decoration: underline;">View CPIC Clinical Guideline</a></p>`;
            }
            
            profileHtml += '</div>';
            pharmaContent.innerHTML = profileHtml;
        }
        
        // Tab 1: Clinical Recommendation
        const clinicalRec = response.clinical_recommendation || {};
        const recContent = document.getElementById('clinical-rec-content');
        if (recContent) {
            let recHtml = '<div style="padding: 10px;">';
            recHtml += `<p><strong>Dosage Adjustment:</strong></p><p>${clinicalRec.dosage_adjustment || 'Pending analysis'}</p>`;
            recHtml += `<p><strong>Monitoring:</strong></p><p>${clinicalRec.monitoring || 'Pending analysis'}</p>`;
            if (clinicalRec.alternative_drugs && Array.isArray(clinicalRec.alternative_drugs)) {
                recHtml += '<p><strong>Alternative Drugs:</strong></p><ul>';
                clinicalRec.alternative_drugs.forEach(alt => {
                    recHtml += `<li>${alt}</li>`;
                });
                recHtml += '</ul>';
            }
            recHtml += '</div>';
            recContent.innerHTML = recHtml;
        }
        
        // Tab 2: Clinical Explanation
        const llmExplain = response.llm_generated_explanation || {};
        const explainContent = document.getElementById('clinical-exp-content');
        if (explainContent) {
            let explainHtml = '<div style="padding: 10px;">';
            explainHtml += `<p><strong>Summary:</strong></p><p>${llmExplain.summary || 'Awaiting LLM analysis'}</p>`;
            explainHtml += `<p><strong>Mechanism:</strong></p><p>${llmExplain.mechanism || 'Awaiting LLM analysis'}</p>`;
            explainHtml += `<p><strong>Evidence Basis:</strong></p><p>${llmExplain.evidence_basis || 'Awaiting LLM analysis'}</p>`;
            
            if (llmExplain.interaction_notes && Array.isArray(llmExplain.interaction_notes)) {
                explainHtml += '<p><strong>Important Notes:</strong></p><ul>';
                llmExplain.interaction_notes.forEach(note => {
                    explainHtml += `<li>${note}</li>`;
                });
                explainHtml += '</ul>';
            }
            
            explainHtml += '</div>';
            explainContent.innerHTML = explainHtml;
        }
    }
});