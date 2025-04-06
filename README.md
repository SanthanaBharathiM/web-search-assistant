# Web Search Assistant

A powerful tool that enhances AI assistant responses with real-time web search capabilities.

## Description

Web Search Assistant is a Python application that leverages LLM capabilities to determine when web searches are necessary to provide accurate responses to user queries. It integrates Llama 3.1 with DuckDuckGo search to find, analyze, and incorporate relevant web content into assistant responses.

## Features

- 🧠 Intelligent search determination - The system uses AI to decide if a web search is needed
- 🔍 Dynamic search query generation - Creates optimal search queries based on user prompts
- 📊 Search result ranking - Evaluates search results to find the most relevant content
- 📝 Content evaluation - Determines if scraped content contains the data needed for a response
- 🌊 Streaming responses - Delivers AI responses in real-time as they're generated

## How It Works

1. User submits a query to the assistant
2. System determines if web search is required to answer accurately
3. If search is needed:
   - Generates an optimal search query
   - Performs a search using DuckDuckGo
   - Identifies the best search result
   - Scrapes and validates content relevance
   - Incorporates relevant data into the response
4. Assistant responds with enriched information

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/web-search-assistant.git
cd web-search-assistant

# Install dependencies
pip install ollama requests beautifulsoup4 trafilatura
```

## Usage

1. Make sure you have Ollama installed with the llama3.1 model available
2. Run the application:

```bash
python web_search_assistant.py
```

3. Enter your queries and receive responses enhanced with real-time web data

## Requirements

- Python 3.7+
- Ollama with llama3.1 model
- Internet connection for web searches

## Example Session

```
USER
What are the latest advancements in quantum computing?

SEARCH OR NOT RESULTS: True
Web search required
GENERATING SEARCH QUERY.

ASSISTANT
Based on recent web search data, quantum computing has seen several significant advancements:

Recent breakthroughs include IBM's 127-qubit Eagle processor announced in late 2023, which represents a major step in scaling quantum computing hardware. Google has also reported achieving quantum supremacy with their Sycamore processor, completing calculations that would take traditional supercomputers thousands of years.

Researchers have made progress in quantum error correction, a critical challenge in building practical quantum computers. New techniques like surface codes and lattice surgery are showing promise in managing quantum decoherence.

...
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
