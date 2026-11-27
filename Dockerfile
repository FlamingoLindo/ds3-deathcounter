FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-eng \
        libgl1 \
        libglib2.0-0 \
        firefox-esr \
        ffmpeg \
        curl \
        ca-certificates \
        xz-utils \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/firefox \
    && curl -fsSL https://ftp.mozilla.org/pub/firefox/releases/159.0/linux-x86_64/en-US/firefox-159.0.tar.xz \
    | tar -xJ -C /opt/firefox --strip-components=1

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
