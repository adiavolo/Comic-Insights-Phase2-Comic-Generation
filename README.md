# Comic Insights

A web application for AI-powered comic page generation using Stable Diffusion.

## Features

- Clean, minimal Gradio interface with integrated style and aspect ratio selection
- Multiple art style options including Manga, Ghibli, and custom styles
- Prompt-driven comic creation with style-specific enhancements
- Image generation via AUTOMATIC1111/Forge Stable Diffusion API
- Session management and history tracking
- Export capabilities for images and session data
- Customizable dimensions and aspect ratios
- Negative prompt support for better image control

## Prerequisites

- Python 3.8 or higher
- AUTOMATIC1111/Forge Stable Diffusion web UI running locally
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd comic-insights
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Ensure AUTOMATIC1111/Forge is running locally at http://localhost:7860
2. The default API endpoint is set to `http://localhost:7860/sdapi/v1/txt2img`
3. Art styles and other configurations can be modified in:
   - `config/styles.json` for base styles and aspect ratios
   - `config/styles/styles_integrated_filtered.csv` for custom styles

## Usage

1. Start the application:
```bash
python main.py
```

2. Open your web browser and navigate to `http://localhost:7862` (default port)

3. Use the interface to:
   - Enter detailed scene descriptions
   - Select base art style (e.g., Manga, Ghibli)
   - Choose custom styles to enhance the generation
   - Select aspect ratio and adjust dimensions
   - Set CFG scale for prompt adherence
   - Add negative prompts to avoid unwanted elements
   - Generate and export comic pages
   - View generation history

## Project Structure

```
comic-insights/
├── main.py              # Application entry point
├── ui/
│   ├── interface.py     # Gradio interface
│   └── prompt_manager.py # Style and prompt management
├── backend/
│   ├── img_api.py       # Image generation API
│   ├── nlp_engine.py    # Text generation (placeholder)
│   └── session_manager.py # Session management
├── config/
│   ├── styles.json      # Base styles and aspect ratios
│   └── styles/
│       └── styles_integrated_filtered.csv # Custom styles
├── export/              # Generated images and exports
├── logs/                # Application logs
└── requirements.txt     # Python dependencies
```

## Style Configuration

The application supports two types of styles:
1. Base Styles: Defined in `styles.json`, these are the main art styles (e.g., Manga, Ghibli)
2. Custom Styles: Defined in `styles_integrated_filtered.csv`, these are additional style modifiers that can be combined with base styles

Each style can include:
- Prompt additions
- Negative prompts
- LoRA weights
- Style-specific parameters

## Future Enhancements

- Integration with NLP models for plot generation
- Dialogue generation capabilities
- Multi-user support
- Advanced export options
- Gallery view for past generations
- Style preview functionality
- Batch generation capabilities

## License

[Your chosen license]

## Contributing

[Your contribution guidelines] 