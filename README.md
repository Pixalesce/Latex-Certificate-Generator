# Certificate Generator

This tool generates professional certificates from a LaTeX template for a list of participants. You can run it either:

- Using the graphical user interface
- Via command line
  > both methods are supported via Docker

## Features

- Generate professional certificates from a LaTeX template
- User-friendly graphical interface for easy customization
- Batch processing of multiple participants
- Supports adding of custom logo
- Containerized with Docker for easy setup across platforms

## Installation

1. Clone this repository:

```bash
git clone https://github.com/Pixalesce/Latex-Certificate-Generator
cd Latex-Certificate-Generator
```

## Usage

### Using Docker

#### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine installed
- Git (optional, if cloning the repository)

#### Option 1: Using the GUI (Recommended)

1. **Start the GUI service**:

   ```bash
   # Build the Docker images (first time only)
   docker compose build certificate-gui

   # Start the GUI
   docker compose up -d certificate-gui
   ```

2. **Access the Web Interface**:
   - Open your web browser and go to: `http://localhost:8501`
   - Configure your certificates using the web interface
   - Download generated PDFs

#### Option 2: Using the Command Line

1. **Configure your certificates**:
   - Edit `workshop_info.txt` with your workshop details and participant names in your favourite text editor
   - Add your partner's logo to the `logos/` directory, naming it as `partner.png`

2. **Build and run the container**:

   ```bash
   # Build the Docker image (first time only)
   docker compose build certificate-generator

   # Generate certificates
   docker compose run --rm certificate-generator
   ```

   The generated PDFs will be available in the `pdfs/` directory.

#### Stopping the Services

- To stop the GUI service, press `Ctrl+C` in the terminal where it's running
- To remove all containers and networks:

  ```bash
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

> You can modify these in the `docker compose.yml` file if needed.

### Native Installation

#### Prerequisites

- Python 3.6 or higher
  - **Windows**: Download from [python.org](https://www.python.org/downloads/windows/)
  - **Linux**: Use your package manager (e.g., `sudo apt install python3` on Ubuntu/Debian)
  - **macOS**: Comes pre-installed or use [Homebrew](https://brew.sh/): `brew install python`

- LaTeX Distribution
  - Windows
    - Download and install [MiKTeX](https://miktex.org/download) (Recommended)
    - Choose the complete installation
    - Enable automatic package installation when prompted
  - macOS
    1. Install BasicTeX (minimal TeX distribution):
       ```bash
       brew install --cask basictex
       ```
    2. After installation restart your terminal or run:
       ```bash
       eval "$(/usr/libexec/path_helper)";
       ```
  - Linux (Ubuntu/Debian)

    ```bash
    sudo apt update
    sudo apt install texlive-full
    ```

#### Option 1: Using the GUI

1. Run the generator:
   ```
   python3 run_gui.py
   ```
2. Open the dashboard at `http://localhost:8501`

#### Option 2: Using the Command Line

1. Prepare your `workshop_info.txt` file with workshop details and participant names in your favourite text editor
2. Add your partner's logo to the `logos/` directory, naming it as `partner.png`
3. Run the generator:
   ```
   python3 generate_certificates.py
   ```
4. Find your generated PDFs in the `pdfs` directory

## Customization

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

_this project was built with the help of AI_
