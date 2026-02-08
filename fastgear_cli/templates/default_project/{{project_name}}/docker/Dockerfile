# define an alias for the specific python version used in this file.
FROM docker.io/python:3.13.7-slim-bookworm AS python

# Python build stage
FROM python AS python-build-stage

# Set environment variables
# Available options for MODE: "production", "local"
ARG MODE="production"

# Install curl
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
 		&& rm -rf /var/lib/apt/lists/*

# Install uv
# The installer requires curl (and certificates) to download the release archive
RUN curl -fsSL https://astral.sh/uv/install.sh -o /uv-installer.sh \
    && sh /uv-installer.sh \
 		&& rm /uv-installer.sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Set environment variables
ENV HOMEDIR="/app"

WORKDIR ${HOMEDIR}

# Copy the application code
COPY . ${HOMEDIR}/

# Install dependencies
RUN  uv sync --locked  $(if [ "$MODE" = "local" ]; then echo "--group dev"; fi)
RUN uv run pip install --no-deps .


# Python 'run' stage
FROM python AS python-run-stage

# Set environment variables
ENV MODE=${MODE} \
    HOMEDIR="/app"

# Copy only necessary files from the python-build-stage stage
COPY --from=python-build-stage ${HOMEDIR} ${HOMEDIR}

# Create a non-root user and group
RUN groupadd -r nonroot-group  \
    && useradd -r -g nonroot-group nonroot-user \
    && chown -R nonroot-user:nonroot-group ${HOMEDIR}

ENV VIRTUAL_ENV="${HOMEDIR}/.venv" \
    PATH="${HOMEDIR}/.venv/bin:$PATH" \
    PYTHONPATH="${HOMEDIR}"

WORKDIR ${HOMEDIR}
USER nonroot-user
EXPOSE ${APP_PORT}

CMD ["python", "src/main.py"]