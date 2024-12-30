FROM python:3.12

WORKDIR /app

# Update package lists and install necessary packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install dev-specific packages
RUN apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Git clone
RUN git clone https://github.com/hailpam/bndt-indicator.git .

# Upgrade Pip
RUN pip install --upgrade pip setuptools wheel

RUN pip install -v numpy cython --no-cache-dir --only-binary=:all:

RUN pip install -v ternary pyarrow

RUN pip install -v --only-binary=:all: --no-input --no-cache-dir -r minimal.requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/dtpi/_stcore/health -v

ENTRYPOINT ["make", "debug"]