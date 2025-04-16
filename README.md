# Smart_code_review Bot

**Smart Code Review Bot** is a GitHub Action and Python-based tool that performs AI-powered code reviews using the [Ollama](https://ollama.com) API. It posts inline and general comments on pull requests to help developers improve code quality automatically.

## Features

- Automatically reviews code on pull requests
- Uses [CodeLlama](https://ollama.com/library/codellama) via Ollama for AI feedback
- Posts inline comments and general suggestions
- Fixes PEP 8 issues with `autopep8` and `black`
- Fixes Pylint issues using Codellama
- Supports multiple programming languages

## Supported Languages

- JavaScript (`.js`, `.jsx`)
- TypeScript (`.ts`, `.tsx`)
- Python (`.py`)
- Go (`.go`)
- Java (`.java`)
- Ruby (`.rb`)
- PHP (`.php`)
- C# (`.cs`)

## Requirements

- Python 3.9+
- Ollama installed and accessible in the GitHub Action or locally
- `requirements.txt` installed via `pip`

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/smartcode0108/smart_code_review.git
cd smart-code-review-bot