FROM python:3.13-slim

# -y -> say yes, to all 'Do you want to continue? [Y/n]'
# --no-install-recommends -> only install the packages we need, not the recommended ones (saves space)
# build-essential and gcc, these are compilers needed to build some of the python packages that have native extensions (like pyjwt)
# libffi-dev is needed for cryptography package, which is a dependency of some of our packages (like pyjwt)

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libffi-dev \
       redis-server \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install uv
RUN uv sync

EXPOSE 8000

# by default CMD use 1 process, now to run 2 at same time for redis and fastapi, we use sh and -c
# --save '' -> disables snapshot
# --appendonly no -> disables the tran log
# --daemonize yes -> It tells Redis to start and then move to the background

# this will start redis in bg and start fastapi using univorn
CMD ["sh", "-c", "redis-server --save '' --appendonly no --daemonize yes && exec uv run run.py --host 0.0.0.0 --port 8000"]
