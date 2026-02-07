"""PharmGKB API Client - Query drug-gene interactions"""
import requests
from typing import List, Dict, Optional


class PharmGKBClient:
    """Client for querying PharmGKB API for drug-gene interactions"""

    BASE_URL = "https://api.pharmgkb.org/v1"

    # Risk level mapping
    RISK_LEVEL_MAP = {
        'high': 'High',
        'moderate': 'Moderate',
        'lower': 'Low',
        'unknown': 'Unknown'
    }

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def query_gene_drug_interactions(self, gene_name: str, variant: str = None, impact: str = None) -> List[Dict]:
        """
        Query PharmGKB for drug-gene interactions

        Args:
            gene_name: Gene name (e.g., 'SLCO1B1')
            variant: Optional variant rsID (e.g., 'rs4149056')
            impact: Optional clinical impact description

        Returns:
            List of dicts with: {
                'drug_name': str,
                'gene': str,
                'variant': str,
                'risk_level': str,
                'clinical_annotation': str,
                'dosing_guideline': str
            }
        """
        interactions = []

        try:
            # Try querying by rsID first (more specific)
            if variant and variant.startswith('rs'):
                print(f"[PharmGKB] Querying by variant rsID: {variant}")
                variant_drugs = self._query_variant(variant)
                if variant_drugs:
                    for drug_info in variant_drugs:
                        interaction = {
                            'drug_name': drug_info.get('name', 'Unknown'),
                            'gene': gene_name,
                            'variant': variant,
                            'risk_level': self._determine_risk_level(drug_info, impact),
                            'clinical_annotation': drug_info.get('summary', '') or impact or '',
                            'dosing_guideline': drug_info.get('dosing_guideline', '')
                        }
                        interactions.append(interaction)

            # Also query by gene name for comprehensive results
            print(f"[PharmGKB] Querying by gene: {gene_name}")
            gene_drugs = self._query_genes(gene_name)
            if not gene_drugs:
                print(f"[PharmGKB] No genes found for {gene_name}")
                return interactions

            for drug_info in gene_drugs:
                interaction = {
                    'drug_name': drug_info.get('name', 'Unknown'),
                    'gene': gene_name,
                    'variant': variant or '',
                    'risk_level': self._determine_risk_level(drug_info, impact),
                    'clinical_annotation': drug_info.get('summary', '') or impact or '',
                    'dosing_guideline': drug_info.get('dosing_guideline', '')
                }
                interactions.append(interaction)

            return interactions

        except Exception as e:
            print(f"Error querying PharmGKB for {gene_name}/{variant}: {e}")
            return []

    def _query_genes(self, gene_name: str) -> List[Dict]:
        """Query PharmGKB for genes"""
        try:
            # Search for gene
            url = f"{self.BASE_URL}/genes"
            params = {
                'query': gene_name,
                'size': 10
            }

            print(f"[PharmGKB API] Requesting: {url} with query={gene_name}")
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            print(f"[PharmGKB API] Response status: {response.status_code}, data keys: {data.keys() if data else 'empty'}")

            if data.get('data'):
                gene_data = data['data'][0] if data['data'] else {}
                print(f"[PharmGKB API] Gene data keys: {gene_data.keys() if gene_data else 'empty'}")
                result = self._extract_drug_interactions(gene_data)
                print(f"[PharmGKB API] Extracted {len(result)} interactions from gene data")
                return result

            print(f"[PharmGKB API] No data returned from API")
            return []

        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return []
        except Exception as e:
            print(f"Error parsing API response: {e}")
            return []

    def _extract_drug_interactions(self, gene_data: Dict) -> List[Dict]:
        """Extract drug interactions from gene data"""
        drugs = []

        print(f"[PharmGKB API] Extracting interactions - available keys: {list(gene_data.keys())}")

        # Get related drugs from gene data
        if 'relatedDrugs' in gene_data:
            print(f"[PharmGKB API] Found relatedDrugs: {len(gene_data.get('relatedDrugs', []))} drugs")
            for drug in gene_data.get('relatedDrugs', []):
                drug_info = {
                    'name': drug.get('drugName', drug.get('name', 'Unknown')),
                    'summary': drug.get('summary', ''),
                    'dosing_guideline': drug.get('dosingGuideline', '')
                }
                drugs.append(drug_info)

        # Alternative: Check related variants
        if 'variants' in gene_data:
            print(f"[PharmGKB API] Found variants: {len(gene_data.get('variants', []))} variants")
            for variant in gene_data.get('variants', []):
                if 'relatedDrugs' in variant:
                    print(f"[PharmGKB API] Variant has {len(variant.get('relatedDrugs', []))} related drugs")
                    for drug in variant.get('relatedDrugs', []):
                        drug_info = {
                            'name': drug.get('drugName', drug.get('name', 'Unknown')),
                            'summary': drug.get('summary', ''),
                            'dosing_guideline': drug.get('dosingGuideline', '')
                        }
                        drugs.append(drug_info)

        print(f"[PharmGKB API] Total drugs extracted: {len(drugs)}")
        return drugs

    def _query_variant(self, rsid: str) -> List[Dict]:
        """Query PharmGKB for a specific variant"""
        try:
            url = f"{self.BASE_URL}/variants"
            params = {
                'query': rsid,
                'size': 10
            }

            print(f"[PharmGKB API] Requesting: {url} with query={rsid}")
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            print(f"[PharmGKB API] Variant response status: {response.status_code}")

            if data.get('data'):
                variant_data = data['data'][0] if data['data'] else {}
                print(f"[PharmGKB API] Variant data keys: {list(variant_data.keys())}")
                result = self._extract_variant_drugs(variant_data)
                print(f"[PharmGKB API] Extracted {len(result)} drugs from variant")
                return result

            return []

        except Exception as e:
            print(f"Variant query failed: {e}")
            return []

    def _extract_variant_drugs(self, variant_data: Dict) -> List[Dict]:
        """Extract drug info from variant data"""
        drugs = []

        # Check various possible fields for drug information
        for key in ['relatedDrugs', 'drugs', 'drugRelationships']:
            if key in variant_data:
                print(f"[PharmGKB API] Found {key}: {len(variant_data.get(key, []))} drugs")
                for drug in variant_data.get(key, []):
                    drug_info = {
                        'name': drug.get('drugName', drug.get('name', 'Unknown')),
                        'summary': drug.get('summary', drug.get('description', '')),
                        'dosing_guideline': drug.get('dosingGuideline', '')
                    }
                    drugs.append(drug_info)

        return drugs

    def _determine_risk_level(self, drug_info: Dict, impact: str = None) -> str:
        """Determine risk level from drug info"""
        # Check impact field first (from VCF annotation)
        if impact:
            impact_lower = impact.lower()
            if any(word in impact_lower for word in ['loss of function', 'contraindicated', 'avoid']):
                return 'High'
            elif any(word in impact_lower for word in ['decreased', 'reduced', 'impaired', 'myopathy', 'increased risk']):
                return 'Moderate'
            elif any(word in impact_lower for word in ['increased', 'enhanced']):
                return 'Low'

        # Fall back to summary text
        summary = drug_info.get('summary', '').lower()

        if any(word in summary for word in ['contraindicated', 'avoid', 'high risk', 'significant']):
            return 'High'
        elif any(word in summary for word in ['moderate', 'consider', 'caution']):
            return 'Moderate'
        elif any(word in summary for word in ['minimal', 'no evidence', 'low risk']):
            return 'Low'
        else:
            return 'Unknown'

    def batch_query(self, variants: List[Dict]) -> List[Dict]:
        """
        Query multiple variants in succession

        Args:
            variants: List of variant dicts with 'gene' and 'variant' keys

        Returns:
            Combined list of all drug interactions found
        """
        all_interactions = []

        print(f"[PharmGKB] batch_query called with {len(variants)} variants")

        if not variants:
            print(f"[PharmGKB] No variants provided!")
            return []

        for idx, variant in enumerate(variants):
            print(f"[PharmGKB] Variant {idx}: {variant}")

            gene = variant.get('gene', 'Unknown')
            variant_id = variant.get('rsid', '')

            print(f"[PharmGKB] Processing variant - gene={gene}, rsid={variant_id}")

            if gene == 'Unknown':
                print(f"[PharmGKB] Skipping - gene is Unknown")
                continue

            print(f"[PharmGKB] Querying gene: {gene}, variant: {variant_id}")

            # Query PharmGKB
            interactions = self.query_gene_drug_interactions(gene, variant_id)

            print(f"[PharmGKB] Found {len(interactions)} interactions for {gene}")
            all_interactions.extend(interactions)

        print(f"[PharmGKB] Total interactions found: {len(all_interactions)}")
        return all_interactions
