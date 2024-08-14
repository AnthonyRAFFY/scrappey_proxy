FROM python:3.12.4-slim-bookworm

ARG TARGETPLATFORM

ENV POETRY_VERSION=1.8.3
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

RUN apt-get update
RUN apt-get install -qq -y --fix-missing --no-install-recommends \
    build-essential \
    gcc \
    openssl \
    libffi-dev \
    libssl-dev \
    pkg-config \
    curl

RUN if [ "$TARGETPLATFORM" = "linux/arm/v7" ] ; then curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sed 's#/proc/self/exe#\/bin\/sh#g' | sh -s -- -y && \
    . $HOME/.cargo/env; \
    fi

ENV PATH="/root/.cargo/bin:${PATH}"

RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app/

COPY ./pyproject.toml ./poetry.lock* /app/

ARG INSTALL_DEV=false
RUN sh -c "if [ $INSTALL_DEV = true ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

ENV PYTHONPATH "/app/scrappey_proxy"

COPY ./scrappey_proxy /app/scrappey_proxy

EXPOSE 8191

CMD ["poetry", "run", "gunicorn", "main:app", "--bind", "0.0.0.0:8191", "--timeout", "600"]
