import os
import subprocess
import shlex
import shutil
from functools import lru_cache
from urllib.parse import urlparse

import requests
from loguru import logger


def _url_basename(url):
    parse_res = urlparse(url)
    return os.path.split(parse_res.path)[1]


def _normalize_dst(src, dst):
    if os.path.isdir(dst):
        dst = os.path.join(dst, _url_basename(src))

    return dst


@lru_cache
def detect_aria2():
    p = subprocess.run(["aria2c", "--version"], shell=True)
    return p.returncode == 0


def download_with_aria2(src, dst, num_connections=16, quiet=False, extra_args=None):
    if not detect_aria2():
        raise RuntimeError("aria2c not detected")

    dst = _normalize_dst(src, dst)
    if extra_args is None:
        extra_args = []
    elif not isinstance(extra_args, list):
        raise ValueError(f"Invalid extra_args type {type(extra_args)}")

    parts = [
        "aria2",
        "-x",
        str(num_connections),
        "-s",
        str(num_connections),
        "--retry-after",
        "3",
        *extra_args,
    ]
    if quiet:
        parts.append("-q")
    else:
        parts.append("--console-log-level=error")
        parts.append("--download-result=hide")
        # known issue: tqdm progress bar may still be overided by aria2
        parts.append("--show-console-readout=false")

    parts.append(src)
    dst_dir = os.path.dirname(dst)
    dst_name = os.path.basename(dst)
    parts.append("-d")
    parts.append(dst_dir)
    parts.append("-o")
    parts.append(dst_name)
    cmd = shlex.join(parts)
    subprocess.run(cmd, shell=True, check=True)

    return dst


def download_with_requests(src, dst):
    dst = _normalize_dst(src, dst)
    with requests.get(src, stream=True) as r:
        r.raise_for_status()
        with open(dst, "wb") as f:
            shutil.copyfileobj(r.raw, f)

    return dst


def download(src, dst):
    if detect_aria2():
        return download_with_aria2(src, dst)
    else:
        logger.info(f"aria2 not found, fallback to requests")
        return download_with_requests(src, dst)
