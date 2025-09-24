# Certificate Generator

This tool generates professional certificates from a LaTeX template for a list of participants.

## Prerequisites

### 1. Python 3.6 or higher
- **Windows**: Download from [python.org](https://www.python.org/downloads/windows/)
- **Linux**: Use your package manager (e.g., `sudo apt install python3` on Ubuntu/Debian)
- **macOS**: Comes pre-installed or use [Homebrew](https://brew.sh/): `brew install python`

### 2. LaTeX Distribution

#### Windows
1. Download and install [MiKTeX](https://miktex.org/download) (Recommended)
   - Choose the complete installation
   - Enable automatic package installation when prompted

#### macOS
1. Install BasicTeX (minimal TeX distribution):
   ```bash
   brew install --cask basictex
   ```
2. After installation, add the following to your shell profile (e.g., `~/.zshrc` or `~/.bash_profile`):
   ```bash
   export PATH="$PATH:/Library/TeX/texbin"
   ```
3. Install additional required packages:
   ```bash
   sudo tlmgr update --self
   sudo tlmgr install latexmk
   ```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install texlive-latex-base texlive-latex-extra latexmk
```

## Installation

1. Clone or download this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Prepare a text file (`participants.txt`) with one participant name per line

2. Run the generator:
   ```bash
   python generate_certificates.py participants.txt
   ```

3. Generated PDFs will be saved in the `pdfs` directory

## Command Line Options

```
usage: generate_certificates.py [-h] [-o OUTPUT_DIR] input_file

Generate certificates from a list of names

positional arguments:
  input_file            Text file containing participant names (one per line)

options:
  -h, --help            show this help message and exit
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Directory to save generated PDFs (default: pdfs)
```

## Customization

To modify the certificate design, edit the `certificate.tex` file. The following placeholders are used:
- `PARTICIPANT_NAME`: Will be replaced with the participant's name
- `TRAINER_NAME`: Will be replaced with the trainer's name
- `DATE`: Will be replaced with the current date

## Troubleshooting

- **LaTeX not found**: Ensure the LaTeX binaries are in your system PATH
- **Missing LaTeX packages**: Install any missing packages using your LaTeX distribution's package manager
- **Permission errors**: On Linux/macOS, you might need to use `sudo` for package installations

## License

This project is licensed under the MIT License - see the LICENSE file for details.
