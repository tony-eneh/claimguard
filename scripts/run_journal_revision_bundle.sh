#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUN_SEPOLIA="${RUN_SEPOLIA:-0}"

log() {
  printf '[journal-bundle] %s\n' "$1"
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$1" >&2
    exit 1
  fi
}

require_cmd npm
require_cmd npx
require_cmd python
require_cmd pdflatex
require_cmd bibtex

cd "$ROOT_DIR"

log 'Installing root dependencies'
npm install

log 'Compiling and testing contracts'
npx hardhat compile
npx hardhat test

log 'Installing PEG dependencies and building TypeScript'
cd claimguard-peg
npm install
npm run build
cd "$ROOT_DIR"

log 'Installing Python dependencies'
python -m pip install -r requirements.txt

log 'Running local experiment suite'
cd claimguard-peg
python e2_run.py
python e3_run.py
python e4_run.py
python e6_run.py
cd "$ROOT_DIR"

log 'Running E5 analysis utilities'
python e5_audit_query_performance.py
python e5_additional_metrics.py
python analyze_e5.py
python analyze_e6.py

if [[ "$RUN_SEPOLIA" == "1" ]]; then
  log 'Running optional Sepolia experiment path via claimguard-peg/run_experiments.py'
  cd claimguard-peg
  python run_experiments.py
  cd "$ROOT_DIR"
else
  log 'Skipping Sepolia experiment path; set RUN_SEPOLIA=1 to enable it'
fi

log 'Building journal PDF'
cd papers/2_journal
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
cd "$ROOT_DIR"

log 'Journal revision bundle complete'