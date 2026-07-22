# Notion Tools Design Documentation

**Author(s):** <medium><a href='https://github.com/pentagramswheel'>Wil Aquino Jr.</a></medium>

**Creation Date:** February 16, 2026

## Introduction
This repo schedules automated tasks which interact with Notion databases. Although it is intended to work with my personal Notion dashboards, it can be used by others as well.

## Installation (pip)
```
python -m venv .venv
source .venv/bin/activate
pip install -e .
python main.py
```

## Installation (uv)
```
uv sync
uv run main.py
```

## Usage

### Quick Start

1. Configure `.env` according to `.env.example`.
2. Run `main.py` to get started. 

### Commentary
The `main()` entry point can also interact with a CI/CD platform of choice to run a schedule of tasks with Notion. This is an ongoing project, but current features include:
- Dynamic chore tracking for families
- Whisker automatic litter box analytics tracking

Notion pictures and templates will be provided soon to showcase functionality.
