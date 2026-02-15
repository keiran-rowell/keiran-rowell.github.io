"""
Codon rarity analysis utilities for web deployment.
Refactored from rare_codons.py, map_codon_rarity_to_pdb.py, and like4like_codons.py
Uses BioPython for robust sequence and structure handling.
"""

import pickle
from typing import Dict, List, Tuple, Optional
from io import StringIO

from Bio import SeqIO
from Bio.PDB import PDBParser, PDBIO
from Bio.SeqUtils import seq1, seq3
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


# Standard genetic code (single letter AA -> codons)
STANDARD_CODON_TABLE = {
    '*': ['TAA', 'TAG', 'TGA'], 
    'A': ['GCA', 'GCC', 'GCG', 'GCT'], 
    'C': ['TGC', 'TGT'], 
    'D': ['GAC', 'GAT'], 
    'E': ['GAA', 'GAG'], 
    'F': ['TTC', 'TTT'], 
    'G': ['GGA', 'GGC', 'GGG', 'GGT'], 
    'H': ['CAC', 'CAT'], 
    'I': ['ATA', 'ATC', 'ATT'],
    'K': ['AAA', 'AAG'],
    'L': ['CTA', 'CTC', 'CTG', 'CTT', 'TTA', 'TTG'],
    'M': ['ATG'],
    'N': ['AAC', 'AAT'],
    'P': ['CCA', 'CCC', 'CCG', 'CCT'],
    'Q': ['CAA', 'CAG'], 
    'R': ['AGA', 'AGG', 'CGA', 'CGC', 'CGG', 'CGT'],
    'S': ['AGC', 'AGT', 'TCA', 'TCC', 'TCG', 'TCT'], 
    'T': ['ACA', 'ACC', 'ACG', 'ACT'], 
    'V': ['GTA', 'GTC', 'GTG', 'GTT'], 
    'W': ['TGG'], 
    'Y': ['TAC', 'TAT']
}

# Reverse lookup: codon -> AA
CODON_TO_AA = {}
for aa, codons in STANDARD_CODON_TABLE.items():
    for codon in codons:
        CODON_TO_AA[codon] = aa


def load_codon_tables(pkl_data: bytes) -> Dict:
    """Load codon tables from pickle bytes (uploaded file)."""
    return pickle.loads(pkl_data)


def parse_fasta(fasta_text: str) -> str:
    """Parse FASTA file and return sequence string."""
    fasta_io = StringIO(fasta_text)
    seq_record = SeqIO.read(fasta_io, 'fasta')
    return str(seq_record.seq).upper()


def nucseq_to_codons(nucseq: str) -> List[str]:
    """Split nucleotide sequence into codons using BioPython."""
    seq = Seq(nucseq.upper().strip())
    # BioPython doesn't have a built-in codon splitter, so we do it manually
    # but at least we're using a Seq object for consistency
    codons = [str(seq[i:i+3]) for i in range(0, len(seq), 3)]
    return codons


def translate_sequence(nucseq: str) -> str:
    """Translate nucleotide sequence to amino acids using BioPython."""
    seq = Seq(nucseq.upper())
    return str(seq.translate())


def parse_pdb_structure(pdb_text: str, structure_id: str = 'structure'):
    """Parse PDB file text and return BioPython structure object."""
    pdb_io = StringIO(pdb_text)
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(structure_id, pdb_io)
    return structure


def extract_sequence_from_pdb(structure) -> str:
    """Extract amino acid sequence from PDB structure."""
    residues = []
    for model in structure:
        for chain in model:
            for residue in chain:
                res_name = residue.get_resname()
                # Skip heteroatoms (water, ligands, etc.)
                if residue.id[0] == ' ':
                    try:
                        res_1let = seq1(res_name)
                        residues.append(res_1let)
                    except:
                        # Non-standard amino acid
                        residues.append('X')
    return ''.join(residues)


def calculate_codon_rarity(nucseq: str, codon_table: Dict) -> List[Dict]:
    """
    Calculate rarity for each codon position.
    
    Returns list of dicts with position, codon, AA, and rarity (frequency).
    """
    codons = nucseq_to_codons(nucseq)
    rarity_data = []
    
    for idx, codon in enumerate(codons):
        if len(codon) != 3:  # Skip incomplete codons at the end
            continue
            
        aa = CODON_TO_AA.get(codon, 'X')
        
        if aa == 'X' or aa not in codon_table:
            rarity = 0.0
        else:
            rarity = codon_table[aa].get(codon, 0.0)
        
        rarity_data.append({
            'position': idx + 1,
            'codon': codon,
            'aa': aa,
            'rarity': rarity  # Note: Higher value = more common (not rare)
        })
    
    return rarity_data


def map_rarity_to_pdb(pdb_text: str, nucseq: str, codon_table: Dict, 
                      structure_id: str = 'structure') -> Tuple[str, List[Dict]]:
    """
    Map codon rarity to PDB b-factors for visualization.
    
    Returns tuple of (modified PDB text, rarity info).
    Based on your map_codon_rarity_to_pdb.py
    """
    structure = parse_pdb_structure(pdb_text, structure_id)
    codons = nucseq_to_codons(nucseq)
    
    rarity_info = []
    res_idx = 0
    
    for model in structure:
        for chain in model:
            for residue in chain:
                # Only process standard amino acids
                if residue.id[0] != ' ':
                    continue
                    
                if res_idx >= len(codons):
                    break
                    
                res_3let = residue.get_resname()
                try:
                    res_1let = seq1(res_3let)
                except:
                    res_1let = 'X'
                
                codon = codons[res_idx]
                
                # Get codon rarity/frequency
                if res_1let in codon_table and codon in codon_table[res_1let]:
                    codon_rarity_val = codon_table[res_1let][codon]
                else:
                    codon_rarity_val = 0.0
                
                # Set b-factor for all atoms in residue
                for atom in residue:
                    atom.set_bfactor(codon_rarity_val)
                
                rarity_info.append({
                    'index': res_idx + 1,
                    'aa': res_1let,
                    'codon': codon,
                    'rarity': round(codon_rarity_val, 3)
                })
                
                res_idx += 1
    
    # Save structure to string
    pdb_io = StringIO()
    io = PDBIO()
    io.set_structure(structure)
    io.save(pdb_io)
    modified_pdb = pdb_io.getvalue()
    
    return modified_pdb, rarity_info


def harmonize_sequence(input_seq: str, input_taxid: str, output_taxid: str, 
                       codon_tables: Dict) -> Dict:
    """
    Harmonize codon usage between organisms (like4like).
    Maps codons to maintain similar rarity in target organism.
    
    Based on your like4like_codons.py algorithm.
    
    Returns dict with harmonized sequence and change information.
    """
    input_table = codon_tables[input_taxid]
    output_table = codon_tables[output_taxid]
    
    input_codons = nucseq_to_codons(input_seq)
    output_codons = []
    changes = []
    
    for idx, input_codon in enumerate(input_codons):
        if len(input_codon) != 3:  # Skip incomplete codons
            output_codons.append(input_codon)
            continue
            
        aa = CODON_TO_AA.get(input_codon, 'X')
        
        if aa == 'X' or aa not in input_table or aa not in output_table:
            output_codons.append(input_codon)
            continue
        
        # Sort codons by frequency (rarity order) in input organism
        input_aa_codons = input_table[aa]
        sorted_input = sorted(input_aa_codons.items(), key=lambda x: x[1])
        
        # Find rank of input codon
        input_rank = next((i for i, (c, _) in enumerate(sorted_input) if c == input_codon), 0)
        
        # Sort codons by frequency in output organism
        output_aa_codons = output_table[aa]
        sorted_output = sorted(output_aa_codons.items(), key=lambda x: x[1])
        
        # Map to same rarity rank in output organism
        if input_rank < len(sorted_output):
            output_codon = sorted_output[input_rank][0]
        else:
            output_codon = sorted_output[-1][0]  # Fallback to most common
        
        output_codons.append(output_codon)
        
        # Record change if different
        if input_codon != output_codon:
            input_rarity = input_aa_codons[input_codon]
            output_rarity = output_aa_codons[output_codon]
            
            changes.append({
                'position': idx + 1,
                'original': input_codon,
                'new': output_codon,
                'aa': aa,
                'original_rarity': round(input_rarity, 2),
                'new_rarity': round(output_rarity, 2),
                'rarity_diff': round(abs(input_rarity - output_rarity), 2)
            })
    
    harmonized_seq = ''.join(output_codons)
    
    # Calculate average rarity preservation
    if changes:
        avg_preservation = 1 - (sum(c['rarity_diff'] for c in changes) / len(changes))
    else:
        avg_preservation = 1.0
    
    return {
        'sequence': harmonized_seq,
        'changes': changes,
        'num_changes': len(changes),
        'avg_rarity_preservation': max(0, round(avg_preservation, 2)),
        'sequence_length': len(harmonized_seq),
        'protein_length': len(output_codons)
    }


def optimize_sequence(input_seq: str, output_taxid: str, codon_tables: Dict) -> Dict:
    """
    Optimise sequence for expression using most common codons.
    
    Returns dict with optimised sequence and change information.
    """
    output_table = codon_tables[output_taxid]
    
    input_codons = nucseq_to_codons(input_seq)
    output_codons = []
    changes = []
    
    for idx, input_codon in enumerate(input_codons):
        if len(input_codon) != 3:  # Skip incomplete codons
            output_codons.append(input_codon)
            continue
            
        aa = CODON_TO_AA.get(input_codon, 'X')
        
        if aa == 'X' or aa not in output_table:
            output_codons.append(input_codon)
            continue
        
        # Find most common codon for this AA
        output_aa_codons = output_table[aa]
        most_common_codon = max(output_aa_codons.items(), key=lambda x: x[1])[0]
        
        output_codons.append(most_common_codon)
        
        # Record change if different
        if input_codon != most_common_codon:
            # Get input frequency (if it exists in output table)
            input_freq = output_aa_codons.get(input_codon, 0.0)
            output_freq = output_aa_codons[most_common_codon]
            
            changes.append({
                'position': idx + 1,
                'original': input_codon,
                'new': most_common_codon,
                'aa': aa,
                'original_freq': round(input_freq, 2),
                'new_freq': round(output_freq, 2),
                'freq_improvement': round(output_freq - input_freq, 2)
            })
    
    optimised_seq = ''.join(output_codons)
    
    return {
        'sequence': optimised_seq,
        'changes': changes,
        'num_changes': len(changes),
        'sequence_length': len(optimised_seq),
        'protein_length': len(output_codons)
    }


def format_codon_table_tsv(codon_table: Dict, taxid: str) -> str:
    """Format codon table as TSV string for download."""
    lines = ['Codon\tAminoAcid\tFrequency']
    
    for aa in sorted(codon_table.keys()):
        for codon, freq in sorted(codon_table[aa].items()):
            lines.append(f'{codon}\t{aa}\t{freq}')
    
    return '\n'.join(lines)


def parse_custom_codon_table(tsv_text: str) -> Dict:
    """
    Parse uploaded TSV codon table into standard format.
    
    Expected format:
    Codon   AminoAcid   Frequency
    TTT     F           0.45
    """
    lines = tsv_text.strip().split('\n')
    if len(lines) < 2:
        raise ValueError("TSV must have header and at least one data row")
    
    header = lines[0].split('\t')
    header_lower = [h.strip().lower() for h in header]
    
    try:
        codon_idx = next(i for i, h in enumerate(header_lower) if 'codon' in h)
        freq_idx = next(i for i, h in enumerate(header_lower) if 'freq' in h or 'usage' in h)
        aa_idx = next((i for i, h in enumerate(header_lower) if 'amino' in h), None)
    except StopIteration:
        raise ValueError("TSV must have 'Codon' and 'Frequency'/'Usage' columns")
    
    table = {}
    for line in lines[1:]:
        cols = line.split('\t')
        if len(cols) < max(codon_idx, freq_idx) + 1:
            continue
        
        codon = cols[codon_idx].strip().upper()
        freq = float(cols[freq_idx].strip())
        
        # Get AA from column or infer from codon
        if aa_idx is not None and len(cols) > aa_idx:
            aa = cols[aa_idx].strip().upper()
        else:
            aa = CODON_TO_AA.get(codon, 'X')
        
        if aa not in table:
            table[aa] = {}
        table[aa][codon] = freq
    
    return table


def generate_fasta_output(sequence: str, header: str) -> str:
    """Generate FASTA format string (single line, no wrapping)."""
    return f'>{header}\n{sequence}'
