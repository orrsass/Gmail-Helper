# Email Classifier

A professional, scalable Python package for classifying Gmail emails using GPT4All, with Redis caching and Matplotlib visualizations.

## Features
- Gmail authentication and email fetching
- Email categorization, priority, and action-required detection using LLM
- Redis caching for LLM responses
- Pie chart visualization of email categories
- Command-line interface (CLI)

## Project Structure

```
my-email-classifier/
├─ src/
│  └─ email_classifier/
│     ├─ __init__.py
│     ├─ config.py
│     ├─ gmail.py
│     ├─ classifier.py
│     ├─ cache.py
│     ├─ plotter.py
│     └─ cli.py
├─ tests/
│  ├─ test_gmail.py
│  ├─ test_classifier.py
│  └─ test_plotter.py
├─ .gitignore
├─ pyproject.toml
├─ README.md
└─ LICENSE
```

## Setup

1. Clone the repository.
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up your Gmail API credentials and environment variables (see `src/email_classifier/config.py`).

## Usage

Run the CLI:
```sh
python -m email_classifier.cli --fetch --classify --plot
```

## Testing

Run tests with:
```sh
pytest tests/
```

## License

MIT License 