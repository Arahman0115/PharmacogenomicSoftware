"""VCF File Parser - Extracts genetic variants from VCF files"""
import re
from typing import List, Dict, Tuple


class VCFParser:
    """Parse VCF files and extract gene/variant/genotype information"""

    def __init__(self, vcf_file_path: str):
        self.vcf_file_path = vcf_file_path
        self.variants = []
        self.sample_name = None

    def parse(self) -> List[Dict]:
        """
        Parse VCF file and extract variants
        Returns list of dicts with: {
            'chrom': str,
            'pos': int,
            'ref': str,
            'alt': str,
            'rsid': str,
            'gene': str,
            'genotype': str,
            'qual': str
        }
        """
        try:
            with open(self.vcf_file_path, 'r') as f:
                header_line = None
                sample_index = None

                for line in f:
                    # Skip comments
                    if line.startswith('##'):
                        continue

                    # Parse header line
                    if line.startswith('#'):
                        header_line = line.strip().split('\t')
                        # Find sample column (after FORMAT)
                        if 'FORMAT' in header_line:
                            sample_index = header_line.index('FORMAT') + 1
                            if sample_index < len(header_line):
                                self.sample_name = header_line[sample_index]
                        continue

                    # Parse variant lines
                    if not line.startswith('#'):
                        variant = self._parse_variant_line(line, sample_index)
                        if variant:
                            self.variants.append(variant)

            return self.variants

        except FileNotFoundError:
            raise Exception(f"VCF file not found: {self.vcf_file_path}")
        except Exception as e:
            raise Exception(f"Error parsing VCF file: {e}")

    def _parse_variant_line(self, line: str, sample_index: int = None) -> Dict:
        """Parse a single variant line from VCF"""
        fields = line.strip().split('\t')

        if len(fields) < 8:
            return None

        chrom = fields[0]
        pos = fields[1]
        rsid = fields[2] if fields[2] != '.' else f"chr{chrom}:{pos}"
        ref = fields[3]
        alt = fields[4]
        qual = fields[5]
        info = fields[7]

        # Extract gene name from INFO field (GENE=, ANN or CSQ)
        gene = self._extract_gene_from_info(info)

        # Extract impact/clinical significance from INFO field
        impact = self._extract_impact_from_info(info)

        # Extract genotype from sample column
        genotype = None
        if sample_index is not None and sample_index < len(fields):
            genotype = self._extract_genotype(fields, sample_index)

        return {
            'chrom': chrom,
            'pos': pos,
            'ref': ref,
            'alt': alt,
            'rsid': rsid,
            'gene': gene,
            'genotype': genotype,
            'qual': qual,
            'impact': impact
        }

    def _extract_impact_from_info(self, info_field: str) -> str:
        """
        Extract impact/clinical significance from INFO field
        Looks for IMPACT= or CSQ fields with impact information
        """
        # Try custom IMPACT= format first
        impact_match = re.search(r'IMPACT=([^;]+)', info_field)
        if impact_match:
            impact = impact_match.group(1).strip()
            if impact and impact != '.':
                return impact

        # Default
        return "Unknown"

    def _extract_gene_from_info(self, info_field: str) -> str:
        """
        Extract gene name from INFO field
        Supports custom GENE=, SnpEff (ANN) and VEP (CSQ) formats
        """
        # Try custom GENE= format first: GENE=SLCO1B1;...
        gene_match = re.search(r'GENE=([^;]+)', info_field)
        if gene_match:
            gene = gene_match.group(1).strip()
            if gene and gene != '.':
                return gene

        # Try SnpEff ANN format: ANN=A|missense_variant|...|SLCO1B1|...
        ann_match = re.search(r'ANN=([^;]*)', info_field)
        if ann_match:
            ann_value = ann_match.group(1).split(',')[0]  # Get first annotation
            parts = ann_value.split('|')
            if len(parts) > 4:
                gene = parts[4]  # Gene name is at position 4
                if gene and gene != '.':
                    return gene

        # Try VEP CSQ format: CSQ=...|GENE|...
        csq_match = re.search(r'CSQ=([^;]*)', info_field)
        if csq_match:
            csq_value = csq_match.group(1).split(',')[0]  # Get first consequence
            parts = csq_value.split('|')
            # Gene position varies, but often around index 3-4
            for part in parts:
                if part and not part.isdigit() and len(part) < 50 and part != '.':  # Likely a gene name
                    return part

        return "Unknown"

    def _extract_genotype(self, fields: List[str], sample_index: int) -> str:
        """
        Extract genotype from sample column
        Returns: '0/0', '0/1', '1/1', or '.|.' for missing
        """
        if sample_index >= len(fields):
            return None

        # Get FORMAT and sample data
        format_field = fields[8] if len(fields) > 8 else None
        sample_field = fields[sample_index] if sample_index < len(fields) else None

        if not format_field or not sample_field:
            return None

        # FORMAT typically starts with GT (genotype)
        if format_field.startswith('GT'):
            # Sample field first element is genotype
            genotype = sample_field.split(':')[0]
            return genotype if genotype != '.' else None

        return None

    def get_variants_summary(self) -> str:
        """Return human-readable summary of parsed variants"""
        if not self.variants:
            return "No variants found"

        genes = set(v.get('gene', 'Unknown') for v in self.variants)
        return f"Found {len(self.variants)} variants across {len(genes)} genes: {', '.join(sorted(genes))}"
