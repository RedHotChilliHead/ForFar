FROM openlabs/docker-wkhtmltopdf-aas

RUN apt-get update && apt-get install -y fonts-dejavu-core

RUN apt-get clean && rm -rf /var/lib/apt/lists/*
