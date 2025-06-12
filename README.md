# Email Classifier CLI

A lightweight, extensible command‑line tool to fetch, categorize, and visualize your Gmail messages using on‑device AI.

---

##  Overview

**Email Classifier CLI** streamlines email triage by automatically retrieving your latest Gmail messages, classifying them into custom categories (e.g., Finance, Personal, Urgent), and generating insightful charts. Ideal for power users, developers, and small teams who want a no‑cloud, privacy‑first solution for email management.

---

##  Key Advantages

* **Privacy‑First**: All processing (LLM inference, caching, plotting) happens locally—no sensitive data is sent to external services.
* **Extensible Categories**: Define or adapt categories via prompt templates; supports granular, context‑aware classification.
* **High Performance**: Caches results in Redis to avoid re‑processing and accelerates repeat runs.
* **Portable & Self‑Contained**: Built with GPT4All for on‑device AI; works offline once dependencies are installed.
* **Clear Insights**: Generates pie‑charts and other visualizations with Matplotlib for quick analysis of email distributions.
* **Developer‑Friendly**: Easy to install, test, and extend with a modular architecture and standard packaging.

---

##  Technologies Used

* **Gmail API** (`google-api-python-client`, `google-auth-oauthlib`): Secure OAuth2 authentication and message retrieval.
* **GPT4All**: On‑device LLM for fast, private email classification without external API calls.
* **Redis** (`redis-py`): Caching layer to store classification results and speed up subsequent runs.

---

##  Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your‑username/email-classifier.git
   cd email-classifier
   ```
2. Install dependencies (via pip):

   ```bash
   pip install -e .
   ```

---

##  Configuration

The app reads all sensitive settings from environment variables. Create a `.env` file or export them manually:

```bash
export GMAIL_CLIENT_ID="<your-google-client-id>"
export GMAIL_CLIENT_SECRET="<your-google-client-secret>"
export GOOGLE_CREDENTIALS_PATH="/path/to/credentials.json"
export TOKEN_PATH="/path/to/token.pickle"
export REDIS_URL="redis://localhost:6379/0"
export MODEL_PATH="/path/to/gpt4all-model.bin"
```

---

##  Usage

Use the install script's console command:

```bash
# Fetch your latest 50 emails
email-classifier fetch --since 1d --limit 50

# Classify and display categories
email-classifier classify --since 3d

# Plot a pie chart of categories
email-classifier plot --since 7d --output report.png
```

Run `email-classifier --help` for all commands and options.

---

##  Testing & CI

1. Run unit tests with pytest:

   ```bash
   pytest
   ```
2. Lint and format checks:

   ```bash
   black --check .
   flake8 .
   ```
3. Continuous Integration (GitHub Actions) is configured to run tests, linting, and type checks on each push.

---

##  Contributing

Contributions and issues are welcome! Please:

1. Fork the repo and create a feature branch.
2. Write tests for new functionality.
3. Submit a pull request describing your changes.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
