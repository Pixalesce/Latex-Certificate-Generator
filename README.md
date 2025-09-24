# Certificate Generator

This tool generates professional certificates from a LaTeX template for a list of participants. You can run it either natively (with Python and LaTeX installed) or using Docker (recommended).

## 🚀 Features

- Generate beautiful, professional certificates from a LaTeX template
- Supports custom logos and design elements
- Containerized with Docker for easy setup
- Cross-platform support (Windows, macOS, Linux)
- Batch processing of multiple participants

## Prerequisites

### Option 1: Using Docker (Recommended)

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine

### Option 2: Native Installation

#### 1. Python 3.6 or higher

- **Windows**: Download from [python.org](https://www.python.org/downloads/windows/)
- **Linux**: Use your package manager (e.g., `sudo apt install python3` on Ubuntu/Debian)
- **macOS**: Comes pre-installed or use [Homebrew](https://brew.sh/): `brew install python`

#### 2. LaTeX Distribution

##### Windows

1. Download and install [MiKTeX](https://miktex.org/download) (Recommended)
   - Choose the complete installation
   - Enable automatic package installation when prompted

##### macOS

1. Install BasicTeX (minimal TeX distribution):
   ```bash
   brew install --cask basictex
   ```
2. After installation, add the following to your shell profile (e.g., `~/.zshrc` or `~/.bash_profile`):
   ```bash
   export PATH="$PATH:/Library/TeX/texbin"
   ```

##### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install texlive-full
```

## Installation

Clone or download this repository

```bash
git clone https://github.com/Pixalesce/Latex-Certificate-Generator
cd certificate-generator
```

## Usage

### Using Docker (Recommended)

#### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine installed
- Git (optional, if cloning the repository)

#### Quick Start

1. **Configure your certificates**:
   - Edit `workshop_info.txt` with your workshop details and participant names
   - Customize `certificate.tex` if you want to change the design
   - Add your logo files to the `logos/` directory

2. **Build and run the container**:

   ```bash
   # Build the Docker image (first time only)
   docker compose build certificate-generator

   # Generate certificates
   docker compose run --rm certificate-generator
   ```

   The generated PDFs will be available in the `pdfs/` directory.

#### Advanced Usage

- **Regenerate certificates** (after making changes to templates or data):

  ```bash
  docker compose run --rm certificate-generator
  ```

- **Clean up** (remove generated files and Docker resources):

  ```bash
  # Remove generated PDFs
  rm -rf pdfs/*

  # Remove Docker containers and networks (keeps the built image)
  docker compose down

  # Remove everything including built images
  docker compose down --rmi all
  ```

#### Volume Mounts

The Docker container uses the following volume mounts:

- `./pdfs` - Output directory for generated PDFs
- `./workshop_info.txt` - Workshop configuration and participant list
- `./certificate.tex` - LaTeX template for the certificate
- `./logos/` - Directory containing logo files

You can modify these in the `docker compose.yml` file if needed.

### Native Installation

1. Prepare your `workshop_info.txt` file with workshop details and participant names
2. Run the generator:
   ```
   python3 generate_certificates.py
   ```
3. Find your generated PDFs in the `pdfs` directory

## 🎨 Customization

### Certificate Design

Edit the `certificate.tex` file to customize the certificate design.

### Logos

Place your logo file in the `logos/` directory and rename it as `partner.png`

### Workshop Information

Edit `workshop_info.txt` to set up your workshop details and participant list. The format is:

```
# Workshop details
workshop_title=My Awesome Workshop
workshop_date=January 1, 2024
trainer_name=John Doe

# Participant list (one per line)
== Participants ==
Alice Smith
Bob Johnson
Charlie Brown
```

## 🔧 Troubleshooting

### Docker Issues

- **Container won't start**:
  - Make sure Docker is running
  - Check for errors with `docker compose logs`
  - Try rebuilding the container: `docker compose build --no-cache`

- **Permission issues with generated files**:
  ```bash
  # On Linux/macOS, fix permissions:
  sudo chown -R $USER:$USER .
  ```

### LaTeX Issues

- **Missing LaTeX packages**:
  - The Docker image includes common LaTeX packages
  - If you need additional packages, modify the Dockerfile and rebuild:
    ```dockerfile
    RUN tlmgr update --self
    RUN tlmgr install collection-fontsrecommended
    ```

- **Font issues**:
  - The container includes standard fonts
  - For custom fonts, add them to the `fonts/` directory and update the Dockerfile

### Common Errors

- **"No such file or directory"**: Check file paths in your configuration
- **LaTeX compilation errors**: Check the output for specific LaTeX error messages
- **Missing logos**: Ensure logo files exist in the `logos/` directory
