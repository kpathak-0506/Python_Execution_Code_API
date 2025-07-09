FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libprotobuf-dev \
    protobuf-compiler \
    pkg-config \
    libnl-3-dev \
    libnl-route-3-dev \
    libcap-dev \
    libseccomp-dev \
    libprotobuf-c-dev \
    libz-dev \
    wget \
    ca-certificates \
    flex \
    bison \
 && rm -rf /var/lib/apt/lists/*


RUN git clone https://github.com/google/nsjail.git /opt/nsjail && \
    cd /opt/nsjail && make && cp nsjail /usr/local/bin/nsjail

RUN mkdir -p /tmp/nsjail-temp
VOLUME /tmp/nsjail-temp

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

EXPOSE 8080

CMD ["python", "main_app.py"]

