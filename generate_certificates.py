import os
import shutil
import subprocess
from pathlib import Path


def read_workshop_config(filename='workshop_info.txt'):
    """Read workshop configuration from file.
    Returns a tuple of (config_dict, participants_list)
    """
    config = {}
    participants = []
    in_participants_section = False
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                if line.startswith('===') and 'Participant' in line:
                    in_participants_section = True
                    continue
                    
                if '=' in line and not in_participants_section:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
                elif in_participants_section and line and not line.startswith('=='):
                    participants.append(line.strip())
        
        return config, participants
        
    except Exception as e:
        print(f"Error reading {filename}: {str(e)}")
        return None, None

def escape_latex(text):
    """Escape special LaTeX characters in the given text."""
    if not text:
        return ""
    
    # First replace backslashes, then other special characters
    replacements = {
        '\\': '\textbackslash{}',
        '&': '\&',
        '%': '\%',
        '$': '\$',
        '#': '\#',
        '_': '\_',
        '{': '\{',
        '}': '\}',
        '~': '\textasciitilde{}',
        '^': '\textasciicircum{}',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def generate_trainer_table(config):
    """Generate LaTeX table for 1-4 trainers with dynamic column widths."""
    # Collect all trainers
    trainers = []
    for i in range(1, 5):
        trainer_name = config.get(f'TRAINER{i}', '').strip()
        if trainer_name:
            trainer_title = config.get(f'TRAINER_TITLE_{i}', '').strip()
            trainers.append((trainer_name, trainer_title))
    
    if not trainers:
        return ""  # No trainers to display
    
    num_trainers = len(trainers)
    
    # Build the table rows
    name_cells = []
    title_cells = []
    
    for name, title in trainers:
        name_cells.append(f"\\Large \\textbf{{{escape_latex(name)}}}")
        title_cells.append(f"\\small{{{escape_latex(title)}}}")
    
    # Create a simple centered table with trainer names and titles
    table = [r"\begin{center}"]
    
    # Add horizontal space between columns (2em on each side of the column separator)
    col_sep = "@{\hspace{" + str((16 / num_trainers) + 2) + "em}}"
    col_spec = ("c" + col_sep) * (num_trainers - 1) + "c"
    
    # Start the table with centered columns and custom column separation
    table.append(r"\begin{tabular}{%s}" % col_spec)
    
    # Add name cells with minimal vertical spacing
    table.append(" & ".join(name_cells) + r"\\[2pt]")  # Reduced from [6pt] to [2pt]
    
    # Add title cells with minimal vertical spacing
    table.append(" & ".join(title_cells) + r"\\")
    
    # Close the table
    table.append(r"\end{tabular}")
    table.append(r"\end{center}")
    
    return "\n".join(table)

def generate_certificate(participant_name, config):
    """Generate a certificate for the given participant using the provided config."""
    # Read the template
    with open('certificate.tex', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Generate the trainer table
    trainer_table = generate_trainer_table(config)
    
    # Prepare replacements
    replacements = {
        '<<PARTICIPANT_NAME>>': escape_latex(participant_name),
        '<<CERTIFICATE_NAME>>': escape_latex(config.get('CERTIFICATE_NAME', 'Certificate of Achievement')),
        '<<WORKSHOP_NAME>>': escape_latex(config.get('WORKSHOP_NAME', 'Workshop')),
        '<<START_DATE>>': escape_latex(config.get('START_DATE', '')),
        '<<END_DATE>>': escape_latex(config.get('END_DATE', '')),
        '<<YEAR>>': escape_latex(config.get('YEAR', '')),
        '<<FOOTER_TEXT>>': escape_latex(config.get('FOOTER_TEXT', '')),
        '<<PARTNER_LOGO>>': config.get('PARTNER_LOGO', 'logos/partner.png'),
        '<<TRAINER_TABLE>>': trainer_table
    }
    
    # Add trainer placeholders for backward compatibility (though they won't be used in the template)
    for i in range(1, 5):
        replacements[f'<<TRAINER{i}>>'] = escape_latex(config.get(f'TRAINER{i}', ''))
        replacements[f'<<TRAINER_TITLE_{i}>>'] = escape_latex(config.get(f'TRAINER_TITLE_{i}', ''))
    
    # Apply all replacements
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    
    # Create output directory if it doesn't exist
    output_dir = Path('pdfs')
    output_dir.mkdir(exist_ok=True)
    
    # Create a safe filename from the participant's name
    safe_filename = ''.join(c if c.isalnum() else '_' for c in participant_name)
    base_filename = f'certificate_{safe_filename.upper()}'
    tex_file = Path(f'{base_filename}.tex')
    
    # Write the modified content to the temporary file in the current directory
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Compile the LaTeX file to PDF
    try:
        # Run pdflatex twice to ensure references are resolved
        for _ in range(2):
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', f'-output-directory={output_dir}', str(tex_file)],
                cwd='.',
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Error generating certificate for {participant_name}:")
                print("LaTeX Error Output:")
                print(result.stderr)
                print("LaTeX Output:")
                print(result.stdout)
                return False
        
        # Move the generated PDF to the output directory
        pdf_source = Path(f'{base_filename}.pdf')
        if pdf_source.exists():
            shutil.move(str(pdf_source), str(output_dir / pdf_source.name))
        
        # Clean up auxiliary files from both current and output directories
        for directory in ['.', output_dir]:
            for ext in ['.aux', '.log', '.out', '.tex']:
                aux_file = Path(directory) / f'{base_filename}{ext}'
                if aux_file.exists() and aux_file.is_file():
                    try:
                        aux_file.unlink()
                    except Exception as e:
                        print(f"Warning: Could not remove {aux_file}: {str(e)}")
        
        print(f"Successfully generated certificate for: {participant_name}")
        return True
        
    except Exception as e:
        print(f"Unexpected error generating certificate for {participant_name}: {str(e)}")
        return False


def main():
    # Read configuration and participants from file
    config, participants = read_workshop_config()
    if not config or participants is None:
        print("Error reading workshop configuration. Please check workshop_info.txt")
        return
        
    if not participants:
        print("No participants found in the configuration file.")
        return
    
    print(f"Found {len(participants)} participants to process...\n")
    print(f"Workshop: {config.get('WORKSHOP_NAME', 'N/A')}")
    print(f"Date: {config.get('START_DATE', 'N/A')} to {config.get('END_DATE', 'N/A')} {config.get('YEAR', '')}\n")
    
    # Generate certificates for all participants
    success_count = 0
    for participant in participants:
        if generate_certificate(participant, config):
            success_count += 1
    
    print(f"\nSuccessfully generated {success_count} out of {len(participants)} certificates.")
    print(f"PDFs are available in the '{os.path.abspath('pdfs')}' directory.")

if __name__ == "__main__":
    main()
