# Use a smaller base image with just the required LaTeX packages
FROM ubuntu:22.04

# Install Python and basic LaTeX
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-recommended \
    texlive-pictures \
    texlive-luatex \
    lmodern \
    fonts-lmodern \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy only necessary files
COPY generate_certificates.py .
COPY certificate.tex .
COPY workshop_info.txt .
COPY logos/ ./logos/

# Create the output directory
RUN mkdir -p /app/pdfs

# Set the entry point with Python unbuffered for better logging
ENTRYPOINT ["python3", "-u", "generate_certificates.py"]

# Default command to show help if no arguments are provided
CMD ["--help"]
