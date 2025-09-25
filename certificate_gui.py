#!/usr/bin/env python3
"""
Certificate Generator GUI
A Streamlit-based GUI for generating LaTeX certificates with logo upload and configuration management.
"""

import streamlit as st
import os
import shutil
import tempfile
import subprocess
from pathlib import Path
import json
from datetime import datetime
import base64
from PIL import Image
import io
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('certificate_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration file paths
CONFIG_FILE = "workshop_info.txt"
TEMPLATE_FILE = "certificate.tex"
LOGOS_DIR = "logos"
PDFS_DIR = "pdfs"

def ensure_directories():
    """Ensure all necessary directories exist."""
    os.makedirs(LOGOS_DIR, exist_ok=True)
    os.makedirs(PDFS_DIR, exist_ok=True)

def read_workshop_config():
    """Read workshop configuration from file."""
    if not os.path.exists(CONFIG_FILE):
        return get_default_config(), []

    config = {}
    participants = []
    in_participants_section = False

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
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
        st.error(f"Error reading {CONFIG_FILE}: {str(e)}")
        return get_default_config(), []

def save_workshop_config(config, participants):
    """Save workshop configuration to file."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write("# Certificate Generation Configuration\n")
            f.write("# This file contains both participant names and certificate details\n")
            f.write("# Lines starting with '#' are comments and will be ignored\n\n")

            f.write("# === Certificate Details (applied to all certificates) ===\n")
            for key, value in config.items():
                if key not in ['participants']:
                    f.write(f"{key}={value}\n")

            f.write("\n=== Participant List ===\n")
            f.write("# Add one participant name per line below\n")
            f.write("# Format: FirstName LastName\n\n")
            for participant in participants:
                f.write(f"{participant}\n")

        return True
    except Exception as e:
        st.error(f"Error saving configuration: {str(e)}")
        return False

def get_default_config():
    """Get default configuration values."""
    return {
        'CERTIFICATE_NAME': 'Certificate of Achievement',
        'WORKSHOP_NAME': 'Workshop',
        'START_DATE': '01 January',
        'END_DATE': '31 January',
        'YEAR': str(datetime.now().year),
        'FOOTER_TEXT': 'The greatest missionary is the Bible in the mother tongue.',
        'TRAINER1': 'Trainer 1',
        'TRAINER_TITLE_1': 'Lead Trainer',
        'TRAINER2': '',
        'TRAINER_TITLE_2': '',
        'TRAINER3': '',
        'TRAINER_TITLE_3': '',
        'PARTNER_LOGO': 'logos/partner.png'
    }

def escape_latex(text):
    """Escape special LaTeX characters in the given text."""
    if not text:
        return ""

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
    # Get the actual number of trainers from config
    num_trainers = 0
    for i in range(1, 5):
        if config.get(f'TRAINER{i}', '').strip() or config.get(f'TRAINER_TITLE_{i}', '').strip():
            num_trainers = i
    
    if num_trainers == 0:
        return ""
    
    # Collect non-empty trainers
    trainers = []
    for i in range(1, num_trainers + 1):
        name = config.get(f'TRAINER{i}', '').strip()
        title = config.get(f'TRAINER_TITLE_{i}', '').strip()
        if name or title:  # Include if either name or title is not empty
            trainers.append((name, title))
    
    if not trainers:
        return ""
    
    # Generate table rows
    name_cells = []
    title_cells = []
    
    for name, title in trainers:
        if name:  # Only add if name is not empty
            name_cells.append(f"\\Large \\textbf{{{escape_latex(name)}}}")
        else:
            name_cells.append("")  # Empty cell if no name
            
        if title:  # Only add if title is not empty
            title_cells.append(f"\\small{{{escape_latex(title)}}}")
        else:
            title_cells.append("")  # Empty cell if no title
    
    # Calculate column spacing based on number of trainers
    col_sep = "@{\\hspace{" + str((16 / len(trainers)) + 2) + "em}}"
    col_spec = ("c" + col_sep) * (len(trainers) - 1) + "c"
    
    # Build the table
    table = [r"\begin{center}"]
    table.append(r"\begin{tabular}{%s}" % col_spec)
    
    # Add names row if at least one name exists
    if any(name_cells):
        table.append(" & ".join(name_cells) + r"\\[2pt]")
    
    # Add titles row if at least one title exists
    if any(title_cells):
        table.append(" & ".join(title_cells) + r"\\")
    
    table.append(r"\end{tabular}")
    table.append(r"\end{center}")
    
    return "\n".join(table)

def generate_certificate_preview(participant_name, config):
    """Generate a preview of the certificate template."""
    try:
        with open(TEMPLATE_FILE, 'r', encoding='utf-8') as file:
            content = file.read()

        trainer_table = generate_trainer_table(config)

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

        for i in range(1, 5):
            replacements[f'<<TRAINER{i}>>'] = escape_latex(config.get(f'TRAINER{i}', ''))
            replacements[f'<<TRAINER_TITLE_{i}>>'] = escape_latex(config.get(f'TRAINER_TITLE_{i}', ''))

        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        return content
    except Exception as e:
        return f"Error generating preview: {str(e)}"

def main():
    st.set_page_config(
        page_title="Certificate Generator",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🎓 Certificate Generator")
    st.markdown("Generate professional LaTeX certificates with custom logos and information")

    ensure_directories()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Configuration", "Logo Management", "Participants", "Preview & Generate", "Settings"]
    )

    # Load current configuration
    config, participants = read_workshop_config()

    if page == "Configuration":
        st.header("Workshop Configuration")
        st.markdown("Configure your workshop details and certificate information")

        # Initialize or update session state for number of trainers
        if 'num_trainers' not in st.session_state:
            # Count how many trainers we have in the config
            trainer_count = 0
            for i in range(1, 5):
                if config.get(f'TRAINER{i}', '').strip() or config.get(f'TRAINER_TITLE_{i}', '').strip():
                    trainer_count = i  # This will give us the highest non-empty trainer number
            st.session_state.num_trainers = max(1, trainer_count)  # At least 1 trainer
        
        
        # The form for configuration
        with st.form("workshop_config"):
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Certificate Details")
                cert_name = st.text_input("Certificate Name", config.get('CERTIFICATE_NAME', ''))
                workshop_name = st.text_input("Workshop Name", config.get('WORKSHOP_NAME', ''))
                start_date = st.text_input("Start Date", config.get('START_DATE', ''))
                end_date = st.text_input("End Date", config.get('END_DATE', ''))
                year = st.text_input("Year", config.get('YEAR', ''))

            with col2:
                st.subheader("Additional Information")
                footer_text = st.text_area("Footer Text", config.get('FOOTER_TEXT', ''), height=100)
            
            # Display trainer inputs inside the form
            st.subheader("Trainers")
            st.markdown("Add 1-4 trainers with their titles")
            for i in range(1, st.session_state.num_trainers + 1):
                with st.expander(f"Trainer {i}", expanded=True):
                    col1, col2 = st.columns([2, 3])
                    with col1:
                        trainer_name = st.text_input(
                            f"Name",
                            config.get(f'TRAINER{i}', ''),
                            key=f"trainer_{i}",
                            placeholder="Full Name"
                        )
                    with col2:
                        trainer_title = st.text_input(
                            f"Title",
                            config.get(f'TRAINER_TITLE_{i}', ''),
                            key=f"trainer_title_{i}",
                            placeholder="e.g., Lead Trainer, Facilitator"
                        )

            # Form submit button
            submitted = st.form_submit_button("Save Configuration", type="primary")
            if submitted:
                # Update config with dynamic number of trainers
                config.update({
                    'CERTIFICATE_NAME': cert_name,
                    'WORKSHOP_NAME': workshop_name,
                    'START_DATE': start_date,
                    'END_DATE': end_date,
                    'YEAR': year,
                    'FOOTER_TEXT': footer_text,
                })
                
                # Clear all trainer fields first
                for i in range(1, 5):
                    config[f'TRAINER{i}'] = ''
                    config[f'TRAINER_TITLE_{i}'] = ''
                
                # Update with current trainers
                num_trainers = st.session_state.get('num_trainers', 1)
                for i in range(1, num_trainers + 1):
                    config[f'TRAINER{i}'] = st.session_state.get(f'trainer_{i}', '')
                    config[f'TRAINER_TITLE_{i}'] = st.session_state.get(f'trainer_title_{i}', '')

                if save_workshop_config(config, participants):
                    st.success("Configuration saved successfully!")
                    st.rerun()
        
        # Trainer management controls (outside the form)
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.num_trainers < 4:
                if st.button("➕ Add Trainer", key="add_trainer_btn"):
                    st.session_state.num_trainers += 1
                    st.rerun()
        with col2:
            if st.session_state.num_trainers > 1:
                if st.button("➖ Remove Last Trainer", key="remove_trainer_btn"):
                    st.session_state.num_trainers -= 1
                    st.rerun()

    elif page == "Logo Management":
        st.header("Logo Management")
        st.markdown("Upload and manage the partner logo for your certificates")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Upload New Logo")
            st.info("Use a PNG image that's at least 250x250 pixels.")
            uploaded_file = st.file_uploader(
                "Choose a PNG logo file",
                type=['png'],
                help="Upload a PNG logo file. It will replace the existing partner logo."
            )

            if uploaded_file is not None:
                # Verify the file is a PNG
                if uploaded_file.type != 'image/png':
                    st.error("Only PNG files are allowed. Please upload a PNG file.")
                else:
                    # Define the target path as partner.png
                    logo_path = os.path.join(LOGOS_DIR, "partner.png")
                    
                    # Save the uploaded file as partner.png
                    with open(logo_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    st.success("Partner logo has been updated successfully!")

                    # Update config to use this logo
                    config['PARTNER_LOGO'] = "logos/partner.png"
                    save_workshop_config(config, participants)

        with col2:
            st.subheader("Current Partner Logo")
            partner_logo_path = os.path.join(LOGOS_DIR, "partner.png")
            if os.path.exists(partner_logo_path):
                st.image(partner_logo_path, caption="Current Partner Logo (partner.png)", width=200)
                if st.button("Remove Current Logo", type="secondary"):
                    try:
                        os.remove(partner_logo_path)
                        if 'PARTNER_LOGO' in config:
                            del config['PARTNER_LOGO']
                            save_workshop_config(config, participants)
                        st.success("Partner logo has been removed.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error removing logo: {str(e)}")
            else:
                st.info("No partner logo found. Upload a PNG logo to set as the partner logo.")

    elif page == "Participants":
        st.header("Participant Management")
        st.markdown("Manage the list of certificate recipients")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Current Participants")
            if participants:
                for i, participant in enumerate(participants):
                    st.text(f"{i+1}. {participant}")
            else:
                st.info("No participants added yet.")

        with col2:
            st.subheader("Add Participant")
            with st.form("add_participant_form", clear_on_submit=True):
                new_participant = st.text_input("Participant Name", key="new_participant")
                submitted = st.form_submit_button("Add Participant")
                if submitted:
                    if new_participant.strip():
                        participants.append(new_participant.strip())
                        if save_workshop_config(config, participants):
                            st.success(f"Added: {new_participant}")
                            st.rerun()
                    else:
                        st.error("Please enter a participant name.")

            if participants:
                st.subheader("Remove Participants")
                # Create a list of options with indices for multi-select
                participant_options = [f"{i+1}. {p}" for i, p in enumerate(participants)]
                selected_indices = st.multiselect(
                    "Select participants to remove",
                    options=range(len(participants)),
                    format_func=lambda x: participant_options[x]
                )
                
                if selected_indices and st.button("Remove Selected", type="secondary"):
                    # Sort indices in reverse order to avoid index shifting during removal
                    for idx in sorted(selected_indices, reverse=True):
                        removed = participants.pop(idx)
                        st.success(f"Removed: {removed}")
                    
                    if save_workshop_config(config, participants):
                        st.rerun()
                
                # Add Remove All button after the multi-select
                if participants:
                    st.markdown("---")
                    st.markdown("### Remove All Participants")
                    
                    # Checkbox for confirmation
                    confirm_remove_all = st.checkbox("I understand this will remove ALL participants", key="confirm_remove_all")
                    
                    # Disabled state based on checkbox
                    if st.button("⚠️ Remove All Participants", 
                               type="primary",
                               disabled=not confirm_remove_all,
                               help="Warning: This will remove ALL participants"):
                        participants.clear()
                        if save_workshop_config(config, participants):
                            st.success("All participants have been removed.")
                            st.rerun()

        # Bulk import
        st.subheader("Bulk Import")
        st.markdown("Import participants from a file (TXT or Excel)")

        # Move file uploader outside the form
        uploaded_file = st.file_uploader(
            "Choose participant file",
            type=['txt', 'xlsx', 'xls'],
            help="Upload a text file (one name per line) or Excel file (first column contains names)",
            key="participant_file_uploader"
        )

        # Only show the form if a file is uploaded
        if uploaded_file is not None:
            try:
                # Process the file
                if uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
                    # Handle Excel file
                    import pandas as pd
                    df = pd.read_excel(uploaded_file, header=None)
                    new_participants = [str(name).strip() for name in df[0].dropna() if str(name).strip()]
                else:
                    # Handle text file
                    content = uploaded_file.getvalue().decode('utf-8')
                    new_participants = [line.strip() for line in content.split('\n') if line.strip()]

                if new_participants:
                    st.success(f"Found {len(new_participants)} participants in the file")
                    
                    # Show preview
                    with st.expander("Preview first 5 participants"):
                        for i, name in enumerate(new_participants[:5], 1):
                            st.text(f"{i}. {name}")
                        if len(new_participants) > 5:
                            st.text(f"... and {len(new_participants) - 5} more")
                    
                    # Add form for the import button
                    with st.form("confirm_import_form"):
                        if st.form_submit_button("Confirm Import"):
                            participants.extend(new_participants)
                            if save_workshop_config(config, participants):
                                st.success(f"Successfully imported {len(new_participants)} participants. Total participants: {len(participants)}")
                                # Clear the file uploader by rerunning the app
                                st.rerun()
                else:
                    st.warning("No valid participant names found in the file.")

            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        else:
            st.info("Please upload a file to import participants.")

    elif page == "Preview & Generate":
        st.header("Preview & Generate Certificates")
        st.markdown("Preview your certificate design and generate PDFs")

        if not participants:
            st.warning("Please add participants before generating certificates.")
            return

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Certificate Preview")
            if participants:
                sample_participant = st.selectbox(
                    "Select participant for preview",
                    participants
                )

                if sample_participant:
                    preview_content = generate_certificate_preview(sample_participant, config)
                    st.code(preview_content, language='latex')

        with col2:
            st.subheader("Generate Certificates")

            st.markdown(f"**Ready to generate {len(participants)} certificates**")
            st.markdown(f"- Workshop: {config.get('WORKSHOP_NAME', 'N/A')}")
            st.markdown(f"- Date: {config.get('START_DATE', 'N/A')} to {config.get('END_DATE', 'N/A')} {config.get('YEAR', '')}")

            generate_col, download_col = st.columns(2)
            
            with generate_col:
                if st.button("Generate All Certificates", type="primary"):
                    with st.spinner("Generating certificates..."):
                        success_count = 0
                        for participant in participants:
                            if generate_single_certificate(participant, config):
                                success_count += 1
                        st.success(f"Generated {success_count} out of {len(participants)} certificates successfully!")
                        st.rerun()  # Refresh to show the new PDFs
            
            # Always show download links for existing PDFs
            if os.path.exists(PDFS_DIR):
                pdf_files = sorted(
                    [f for f in os.listdir(PDFS_DIR) if f.endswith('.pdf')],
                    key=lambda x: os.path.getmtime(os.path.join(PDFS_DIR, x)),
                    reverse=True
                )
                
                if pdf_files:
                    with download_col:
                        st.subheader("Download Certificates")
                        
                        # Download all button
                        import zipfile
                        import io
                        
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                            for pdf_file in pdf_files:
                                pdf_path = os.path.join(PDFS_DIR, pdf_file)
                                zipf.write(pdf_path, pdf_file)
                        
                        zip_buffer.seek(0)
                        st.download_button(
                            label="Download All Certificates as ZIP",
                            data=zip_buffer,
                            file_name="all_certificates.zip",
                            mime="application/zip",
                            key="download_all_zip"
                        )
                        
                        # Initialize selected files in session state if not exists
                        if 'selected_files' not in st.session_state:
                            st.session_state.selected_files = {pdf_file: False for pdf_file in pdf_files}
                        
                        # Track if we need to show the warning
                        show_warning = False
                        
                        # Handle download selected button
                        if st.button("Download Selected"):
                            selected_files = [f for f, selected in st.session_state.selected_files.items() if selected]
                            if not selected_files:
                                show_warning = True
                            else:
                                import zipfile
                                import io
                                
                                zip_buffer = io.BytesIO()
                                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                                    for pdf_file in selected_files:
                                        pdf_path = os.path.join(PDFS_DIR, pdf_file)
                                        zipf.write(pdf_path, pdf_file)
                                
                                zip_buffer.seek(0)
                                st.download_button(
                                    label=f"Download {len(selected_files)} selected certificates",
                                    data=zip_buffer,
                                    file_name=f"selected_certificates_{len(selected_files)}_files.zip",
                                    mime="application/zip",
                                    key="download_selected_zip"
                                )
                        
                        # Show warning if needed
                        if show_warning:
                            st.warning("Please select at least one certificate to download.")
                        
                        # Show individual download buttons with checkboxes
                        st.markdown("### Individual Certificates")
                        for pdf_file in pdf_files:
                            # Create columns for checkbox and download button
                            col1, col2 = st.columns([1, 10])
                            
                            # Checkbox for selection
                            with col1:
                                # Use a unique key for the checkbox based on the file name
                                checkbox_key = f"cb_{pdf_file}"
                                # Update the session state when the checkbox changes
                                if st.checkbox(
                                    "",
                                    value=st.session_state.selected_files.get(pdf_file, False),
                                    key=checkbox_key,
                                    label_visibility="collapsed"
                                ) != st.session_state.selected_files.get(pdf_file, False):
                                    st.session_state.selected_files[pdf_file] = not st.session_state.selected_files.get(pdf_file, False)
                                    st.rerun()
                            
                            # Download button
                            with col2:
                                pdf_path = os.path.join(PDFS_DIR, pdf_file)
                                with open(pdf_path, "rb") as f:
                                    st.download_button(
                                        label=pdf_file,
                                        data=f,
                                        file_name=pdf_file,
                                        mime="application/pdf",
                                        key=f"dl_{pdf_file}",
                                        use_container_width=True
                                    )

    elif page == "Settings":
        st.header("Settings")
        st.markdown("Application settings and information")

        st.subheader("File Locations")
        st.text(f"Configuration: {os.path.abspath(CONFIG_FILE)}")
        st.text(f"Template: {os.path.abspath(TEMPLATE_FILE)}")
        st.text(f"Logos: {os.path.abspath(LOGOS_DIR)}")
        st.text(f"Output: {os.path.abspath(PDFS_DIR)}")

        st.subheader("About")
        st.markdown("""
        **Certificate Generator GUI**

        A Streamlit-based interface for generating professional LaTeX certificates.

        Features:
        - Logo upload and management
        - Workshop configuration
        - Participant management
        - Certificate preview
        - PDF generation

        Requires LaTeX installation for PDF generation.
        """)

def generate_single_certificate(participant_name, config):
    """Generate a single certificate for the given participant."""
    try:
        with open(TEMPLATE_FILE, 'r', encoding='utf-8') as file:
            content = file.read()

        trainer_table = generate_trainer_table(config)

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

        for i in range(1, 5):
            replacements[f'<<TRAINER{i}>>'] = escape_latex(config.get(f'TRAINER{i}', ''))
            replacements[f'<<TRAINER_TITLE_{i}>>'] = escape_latex(config.get(f'TRAINER_TITLE_{i}', ''))

        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        # Create output directory if it doesn't exist
        output_dir = Path(PDFS_DIR)
        output_dir.mkdir(exist_ok=True)

        # Create a safe filename from the participant's name
        safe_filename = ''.join(c if c.isalnum() else '_' for c in participant_name)
        base_filename = f'certificate_{safe_filename.upper()}'
        tex_file = Path(f'{base_filename}.tex')

        # Write the modified content to the temporary file
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # Compile the LaTeX file to PDF
        for _ in range(2):
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', f'-output-directory={output_dir}', str(tex_file)],
                cwd='.',
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                st.error(f"Error generating certificate for {participant_name}")
                return False

        # Move the generated PDF to the output directory
        pdf_source = Path(f'{base_filename}.pdf')
        if pdf_source.exists():
            shutil.move(str(pdf_source), str(output_dir / pdf_source.name))

        # Clean up auxiliary files
        for directory in ['.', output_dir]:
            for ext in ['.aux', '.log', '.out', '.tex']:
                aux_file = Path(directory) / f'{base_filename}{ext}'
                if aux_file.exists() and aux_file.is_file():
                    try:
                        aux_file.unlink()
                    except:
                        pass

        return True

    except Exception as e:
        st.error(f"Error generating certificate for {participant_name}: {str(e)}")
        return False

if __name__ == "__main__":
    main()
