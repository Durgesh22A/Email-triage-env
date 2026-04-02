---
title: Email Triage Env
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
tags:
  - openenv
---

# Email Triage Environment

## Description
An OpenEnv environment where an AI agent triages emails by classifying their priority, category, and recommended action.

## Action Space
| Field | Values |
|-------|--------|
| priority | urgent, normal, low |
| category | support, sales, spam, hr |
| action | reply, forward, archive, delete |

## Observation Space
| Field | Type |
|-------|------|
| email_id | integer |
| subject | string |
| body | string |
| sender | string |

## Tasks
| Task | Difficulty | Description |
|------|-----------|-------------|
| task1_easy | Easy | Detect and delete spam emails |
| task2_medium | Medium | Triage emails with mixed signals |
| task3_hard | Hard | Handle business-critical crisis emails |

## Baseline Scores
| Task | Score |
|------|-------|
| task1_easy | 1.0 |
| task2_medium | 1.0 |
| task3_hard | 0.4 |
| Average | 0.8 |

## Setup Instructions

### Local Setup
```bash
git clone <your-repo>
cd email-triage-env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Inference
```bash
export HF_TOKEN="your-groq-key"
export MODEL_NAME="llama-3.1-8b-instant"
export API_BASE_URL="https://api.groq.com/openai/v1"
python3 inference.py
```

### Docker
```bash
docker build -t email-triage-env .
docker run -e HF_TOKEN="key" -e MODEL_NAME="llama-3.1-8b-instant" -e API_BASE_URL="https://api.groq.com/openai/v1" email-triage-env
```