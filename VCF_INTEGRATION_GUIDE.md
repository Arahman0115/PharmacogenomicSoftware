# VCF Integration Implementation Guide

## Overview
VCF (Variant Call Format) file integration for automatic genetic variant extraction and drug-gene interaction detection.

---

## Completed Implementation

### **Files Created:**

1. **`ui/utils/vcf_parser.py`**
   - VCFParser class for parsing VCF files
   - Extracts: gene names, variants (rsID), genotypes, positions
   - Supports SnpEff (ANN) and VEP (CSQ) annotation formats
   - Handles both plain VCF and gzipped files

2. **`ui/utils/pharmgkb_api.py`**
   - PharmGKBClient for querying PharmGKB API
   - Methods:
     - `query_gene_drug_interactions()` - Get drugs for a gene/variant
     - `batch_query()` - Query multiple variants in succession
     - Risk level determination from API responses

3. **`ui/components/vcf_upload_dialog.py`**
   - VCFUploadDialog - Main upload interface
   - VCFProcessWorker - Background threading for VCF parsing
   - Features:
     - File browser with .vcf and .vcf.gz support
     - Real-time progress logging
     - Background processing (non-blocking UI)
     - Direct import to patient profile

4. **`ui/utils/__init__.py`**
   - Package initialization for utilities

5. **Updated `ui/views/patient/tabs/genomics_tab.py`**
   - Added "Upload VCF File" button to Genomics tab
   - New method `upload_vcf_file()` to launch VCF import dialog
   - Automatic reload of genomic data after successful import

---

## Workflow

```
Patient Profile → Genomics Tab (6. Genomics)
    ↓
[Upload VCF File] button
    ↓
VCFUploadDialog appears
    ├─ Browse for .vcf or .vcf.gz file
    └─ Click "Upload & Process VCF"
    ↓
Background Processing:
    ├─ Parse VCF (extract genes, variants, genotypes)
    ├─ Query PharmGKB API for each gene/variant
    └─ Prepare drug-gene interaction data
    ↓
Preview Results:
    ├─ Shows number of variants found
    ├─ Shows number of drug interactions detected
    └─ Option to "Import to Patient Profile"
    ↓
Import to Database:
    ├─ INSERT into final_genetic_info (variant storage)
    └─ INSERT into drug_review (auto-flags drug warnings)
    ↓
Patient Profile Updated:
    ├─ Genomics tab shows imported variants
    ├─ Drug Review tab auto-populates with warnings
    └─ Prescriptions from Drug Review queue auto-flag
```

---

## Database Integration

### **Tables Populated:**

**`final_genetic_info`** (variant storage)
```sql
user_id, gene, variant, genotype, source='vcf_upload', created_date
```

**`drug_review`** (auto-generated drug warnings)
```sql
user_id, medication_id, gene, variant, risk_level, description, notes, status='active'
```

### **Automatic Workflow:**
1. VCF imported → Variants stored in `final_genetic_info`
2. PharmGKB queried → Drug interactions found
3. Drug interactions → AUTO-INSERTED into `drug_review` table
4. Patient creates prescription → Drug Review queue auto-shows warnings
5. Pharmacist reviews and approves/rejects

---

## Installation Requirements

Add to `requirements.txt`:
```
requests>=2.32.5  # Already installed for API calls
# cyvcf2 is optional - currently using pure Python VCF parsing
# If processing many large VCF files, install: cyvcf2>=0.30.0
```

**Note:** Current implementation uses pure Python VCF parsing (no external library required). For large-scale processing, consider installing `cyvcf2` for 170x speed improvement.

---

## VCF File Requirements

### **Supported Formats:**
- Plain text VCF: `patient.vcf`
- Gzip compressed: `patient.vcf.gz`

### **Required VCF Fields:**
- CHROM, POS, ID (rsID or chr:pos)
- REF, ALT (reference/alternate alleles)
- FORMAT column with GT (genotype)

### **Recommended:**
- Pre-annotated VCF with gene names in INFO field
  - SnpEff format: `ANN=....|GENE_NAME|...`
  - VEP format: `CSQ=....|GENE|...`
- If not pre-annotated, annotation tools:
  - SnpEff: `snpEff -ann input.vcf > output.vcf`
  - VEP: `vep -i input.vcf -o output.vcf`

---

## Error Handling

**Handled Scenarios:**
- Missing VCF file
- Corrupted VCF (invalid format)
- Missing gene names in annotation
- PharmGKB API timeout/connection error
- Medication not found in local database
- Database insert failures

**User Feedback:**
- Progress messages in dialog
- Error dialogs with specific error messages
- Warning messages for medications not in database
- Success confirmation with import count

---

## Performance Notes

- **VCF Parsing:** ~100-1000 variants/second (depends on file size)
- **PharmGKB Queries:** 1 API call per gene/variant (~0.5-1 second each)
- **UI:** Non-blocking (background thread for all processing)
- **Database:** Batch inserts for speed

**For 100 variants:**
- Parsing: <1 second
- PharmGKB queries: ~50-100 seconds (parallel would speed this up)
- Database import: <1 second
- **Total:** ~1-2 minutes

---

## Future Enhancements

1. **Parallel PharmGKB Queries** - Query multiple variants simultaneously
2. **Bulk Import** - Import multiple patient VCF files at once
3. **VCF Validation** - Pre-flight checks for VCF format compliance
4. **Annotation Caching** - Cache PharmGKB results to reduce API calls
5. **HIPAA Encryption** - Encrypt VCF files at rest
6. **Audit Logging** - Track who imported what VCF files when

---

## Testing

### **Test VCF File Creation:**
```
##fileformat=VCFv4.2
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	sample1
1	100	rs123456	A	G	60	PASS	ANN=A|missense|MODERATE|SLCO1B1|ENSG001	GT	0/1
1	200	rs789012	C	T	50	PASS	ANN=C|synonymous|LOW|CYP2C9|ENSG002	GT	1/1
```

### **Test Workflow:**
1. Patient Profile → Genomics tab
2. Click "Upload VCF File"
3. Select test VCF
4. Click "Upload & Process"
5. Verify variants appear in Genomics tab
6. Verify drug warnings appear in Drug Review tab

---

## Support & Troubleshooting

**VCF Not Parsing:**
- Ensure file format is valid (use online VCF validator)
- Check that gene names are in INFO field

**No Drug Interactions Found:**
- Variant may not be in PharmGKB database
- Gene may not have known drug interactions
- Check PharmGKB website manually for verification

**Medications Not Imported:**
- Medication name from PharmGKB may not match local database
- Check spelling in local medications table
- May need to add medication to local database first

**API Timeout:**
- PharmGKB API may be slow or down
- Retry after a few minutes
- Check internet connection

---

## References

- [VCF Format Specification](https://samtools.github.io/hts-specs/VCFv4.2.pdf)
- [PharmGKB API Documentation](https://api.pharmgkb.org/docs/)
- [SnpEff Annotation Tool](http://snpEff.sourceforge.net/)
- [VEP Variant Effect Predictor](https://www.ensembl.org/vep)
