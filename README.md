<h1 align="center"> [CHI'25 Accepted] Characterizing LLM-Empowered Personalized Story-Reading and Interaction for Children:
Insights from Multi-Stakeholder Perspectives
 </h1>

<p align="center">
    <a href="https://arxiv.org/abs/2503.00590">
        <img src="https://img.shields.io/badge/arXiv-2503.00590-B31B1B.svg?style=plastic&logo=arxiv" alt="arXiv">
    </a>
  	<a href="https://storymate.hailab.io/">
      	<img src="https://img.shields.io/badge/StoryMate-Demo-green?style=plastic" alt="demo">
  	</a>
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=plastic" alt="License: MIT">
    </a>
</p>

<p align="center">
Jiaju Chen, Minglong Tang, Yuxuan Lu, Bingsheng Yao, Elissa Fan, Xiaojuan Ma, Ying Xu, Dakuo Wang, Yuling Sun, Liang He
</p>


<p align="center">
    <img src="/figures/teaser.png" width="100%">
</p>



## Overview


Personalized interaction is highly valued by parents in their story-reading activities with children. While AI-empowered story-reading tools have been increasingly used, their abilities to support personalized interaction with children are still limited. Recent advances in large language models (LLMs) show promise in facilitating personalized interactions, but little is known about how to effectively and appropriately use LLMs to enhance children's personalized story-reading experiences. This work explores this question through a design-based study. Drawing on a formative study, we designed and developed StoryMate, an LLM-empowered personalized interactive story-reading tool for children, following an empirical study with children, parents, and education experts. Our participants valued the personalized features in StoryMate, and also highlighted the need to support personalized content, guiding mechanisms, reading context variations, and interactive interfaces. Based on these findings, we propose a series of design recommendations for better using LLMs to empower children's personalized story reading and interaction.



## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- OpenAI API key
- NLTK data



## Project Structure

```
StoryMate/
├── backend/
│   ├── Audio_Generation/
│   ├── Knowledge_Matching/
│   ├── Text_Process/
│   └── app.py
├── frontend/
│   ├── static/
│   └── templates/
├── requirements.txt
└── .env
```

Under the ``Knowledge_Matching`` folder, we organized the structured Next Generation Science Standards (NGSS) from kindergarten level to second grade level in ``NGSS_DC_EN.json`` and ``NGSS_DCI_CN.json``. The pre-calculated key word semantic similarities with pieces of real-world knowledge in NGSS are in ``Similarity_Dict_EN.json`` and ``Similarity_Dict_EN.json``.

## Installation

1. Clone the repository:

```bash
git clone [repository-url]
cd StoryMate
```

2. Create and activate a virtual environment (recommended):

```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Download required NLTK data:

```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

5. Set up environment variables:
   Create a `.env` file in the root directory with your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```



## Quick Start

### Loading a Book into the System

1. First, ensure your book text is organized in a JSON file with the following structure:

```json
[
    "First page text...",
    "Second page text...",
    "Third page text..."
]
```

2. Place your book JSON file in the following directory structure:

```
frontend/static/files/books/[BOOK_TITLE]/[BOOK_TITLE].json
```

3. Run the book loading script:

```bash
cd backend
python book_load.py
```

4. The script will:
   - Process the text and generate audio narration
   - Match scientific knowledge with the content
   - Generate interactive questions and explanations
   - Set up the necessary files for the interactive experience

Example usage:

```python
from book_load import load_book

# Load a book named "Amara and the Bats"
load_book("Amara and the Bats")
```

The book will then be available in the library interface of the application.



## Running the Application

1. Start the Flask server:

```bash
cd backend
python app.py
```

2. Open your web browser and navigate to:

```
http://localhost:5500
```



## Features

- Interactive storytelling with real-world knowledge integration
- Text-to-speech capabilities
- User progress tracking
- Personalized learning experience
- Support for both English and Chinese content



## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).



## Citation

```bibtex
@inproceedings{chen2025storymate,
  author    = {Jiaju Chen and Minglong Tang and Yuxuan Lu and Bingsheng Yao and Elissa Fan and Xiaojuan Ma and Ying Xu and Dakuo Wang and Yuling Sun and Liang He},
  title     = {StoryMate: An LLM-Empowered Personalized Interactive Story-Reading Tool for Children},
  booktitle = {Proceedings of the 2025 CHI Conference on Human Factors in Computing Systems},
  year      = {2025},
  month     = {April},
  location  = {Yokohama, Japan},
  publisher = {ACM},
  doi       = {10.1145/3706598.3713275},
  isbn      = {979-8-4007-1394-1},
}
```
