FROM debian:10 as builder
RUN apt-get update && \
    apt-get install autoconf automake autotools-dev g++ pkg-config python-dev libtool make git curl ca-certificates -y

ENV DUMB_INIT_VERSION=1.2.0
RUN curl -L -o /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v${DUMB_INIT_VERSION}/dumb-init_${DUMB_INIT_VERSION}_amd64 && \
    chmod +x /usr/local/bin/dumb-init

WORKDIR /usr/src

RUN git clone https://github.com/uber/pyflame.git . && \
    ./autogen.sh && \
    ./configure && \
    make install

RUN curl -o /usr/local/bin/flame-chart-json https://raw.githubusercontent.com/uber/pyflame/master/utils/flame-chart-json && \
    chmod +x /usr/local/bin/flame-chart-json


FROM python:2.7.16-slim as final

LABEL org.label-schema.vcs-ref=master \
      org.label-schema.vcs-url="https://github.com/gcavalcante8808/gunicorn_cpu_profiler"

COPY --from=builder /usr/local/bin/pyflame /usr/local/bin/pyflame
COPY --from=builder /usr/local/bin/flame-chart-json /usr/local/bin/flame-chart-json
COPY --from=builder /usr/local/bin/dumb-init /usr/local/bin/dumb-init

RUN apt-get update && \
    apt-get install --no-install-recommends -y gcc libc6-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
COPY gunicorn_cpu_monitor.py .

ENTRYPOINT ["/usr/local/bin/dumb-init","python","gunicorn_cpu_monitor.py"]
