FROM fluent/fluentd:v1.12.0-debian-1.0
LABEL maintainer=Mona_Labs<infrastructure@monalabs.io>
LABEL Description="Mona Agent for Unix Domain Sockets"
USER root
RUN buildDeps="sudo make gcc g++ libc-dev ruby-dev" \
    && apt-get update \
    && apt-get install -y --no-install-recommends sudo make gcc g++ libc-dev ruby-dev vim \
    && sudo gem sources --clear-all \
    && sudo gem install fluent-plugin-multiprocess \
    && SUDO_FORCE_REMOVE=yes \
    apt-get purge -y --auto-remove \
    -o APT::AutoRemove::RecommendsImportant=false \
    sudo make gcc g++ libc-dev ruby-dev \
    && mkdir /tmp/buffer \
    && chown fluent:fluent /tmp/buffer \
    && rm -rf /var/lib/apt/lists/* \
    /home/fluent/.gem/ruby/2.6.6/cache/*.gem

COPY fluent*.conf /fluentd/etc/
RUN mkdir -p /var/run/mona && \
    chown -R 999:999 /var/run/mona/

# Default Environment Variable
ENV UDS_SERVER_ADDRESS="/var/run/mona/mona.sock"
ENV LOG_LEVEL="warn"

ENV FLUSH_INTERVAL="30s"
ENV MONA_REST_TIMEOUT=5
ENV MONA_REST_FORMAT_TYPE="json"
ENV FLUSH_THREAD_COUNT="50"
ENV FLUSH_THREAD_INTERVAL=10
ENV FLUSH_THREAD_BURST_INTERVAL=5
ENV BUFFER_TOTAL_SIZE="8GB"
ENV BUFFER_TYPE="file"
ENV CHUNK_MAX_SIZE="16MB"
ENV CHUNK_MAX_RECORD_COUNT=1000

USER fluent

