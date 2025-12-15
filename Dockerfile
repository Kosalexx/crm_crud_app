FROM python:3.13-slim

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    # python
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

RUN pip install uv

RUN apt-get update \
    && apt-get install -y build-essential gettext \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

ENV VIRTUAL_ENV=/opt/venv
RUN uv venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY pyproject.toml uv.lock ./

RUN uv pip install -e .

COPY . .

RUN useradd -m appuser
USER appuser
