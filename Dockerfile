FROM debian:bookworm-slim

RUN apt-get update -qq && apt-get install -y -qq git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://mise.run | sh
ENV PATH="/root/.local/bin:$PATH"

COPY docs/running-the-server.sh /running-the-server.sh

WORKDIR /
ENTRYPOINT ["bash", "/running-the-server.sh"]
