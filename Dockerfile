FROM python:3.9-slim-buster as base

FROM base as builder

RUN apt-get -qq update \
    && rm -rf /var/lib/apt/lists/*

# get packages
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base as final
# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
# Enable Profiler
ENV ENABLE_PROFILER=1

WORKDIR /server

# Grab packages from builder
COPY --from=builder /usr/local/lib/python3.9/ /usr/local/lib/python3.9/

# Add the application
COPY . .

EXPOSE 8080
ENTRYPOINT [ "python", "main.py" ]