# Comic Insights

A web application for AI-powered comic page generation using Stable Diffusion.

## Features

- Clean, minimal Gradio interface with integrated style and aspect ratio selection
- **Multi-tab UI:**
  - Plot/Story Setup (static placeholder, for entering story/scene context)
  - Image Generation & Editing (fully functional, all previous features)
  - Character Management (static placeholder, for future character roster)
- Each tab provides unique, context-appropriate tips
- Multiple art style options including Manga, Ghibli, and custom styles
- Prompt-driven comic creation with style-specific enhancements
- Image generation via AUTOMATIC1111/Forge Stable Diffusion API
- Session management and history tracking
- Export capabilities for images and session data
- Customizable dimensions and aspect ratios
- Negative prompt support for better image control
- **Extensive logging and debugging:**
  - Debug, info, and status logs for UI initialization, tab creation, and event handling
  - Improved traceability for easier debugging and monitoring

## Prerequisites

- Python 3.8 or higher
- AUTOMATIC1111/Forge Stable Diffusion web UI running locally
- [Ollama](https://ollama.com/) installed and running locally (for story summary generation)
- Gemma3:12b model pulled in Ollama (`ollama pull gemma3:12b`)
- Virtual environment (recommended)

## Ollama Integration (Story Summary Generation)

This project now supports local LLM-powered story summary generation using [Ollama](https://ollama.com/) and the Gemma3:12b model.

### Setup
1. [Download and install Ollama](https://ollama.com/download) for your platform.
2. Start the Ollama server:
   ```bash
   ollama serve
   ```
3. Pull the required model:
   ```bash
   ollama pull gemma3:12b
   ```

### Usage
When you use the "Plot/Story Setup" tab, your story prompt will be summarized by the local Gemma3:12b model via Ollama. No internet connection is required for LLM inference.

If you encounter a model not found error, ensure you have pulled the correct model (`gemma3:12b`) and that Ollama is running.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/adiavolo/Comic-Insights-Phase2-Comic-Generation.git
cd Comic-Insights-Phase2-Comic-Generation
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

2. Open your web browser and navigate to `http://localhost:7861` (default port)

3. Use the interface tabs:
   - **Plot/Story Setup:** Enter your main comic prompt, story context, or page/scene summary (static placeholder for now)
   - **Image Generation & Editing:** Enter scene description, select art/custom styles, aspect ratio, dimensions, CFG scale, negative prompts, generate/export images, and view history
   - **Character Management:** (static placeholder) Will allow character roster management in the future

4. Each tab provides unique tips relevant to its purpose.

## Project Structure

```
Comic-Insights-Phase2-Comic-Generation/
├── main.py              # Application entry point
├── ui/
│   ├── interface.py     # Gradio interface (multi-tab UI, logging, tips)
│   └── prompt_manager.py # Style and prompt management
├── backend/
│   ├── img_api.py       # Image generation API
│   ├── nlp_engine.py    # Text generation (Ollama integration for story summary)
│   └── session_manager.py # Session management
├── config/
│   ├── styles.json      # Base styles and aspect ratios
│   └── styles/
│       └── styles_integrated_filtered.csv # Custom styles
├── export/              # Generated images and exports
├── logs/                # Application logs (debug, status, error)
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

- Dialogue generation capabilities (via LLM)
- Multi-user support
- Advanced export options
- Gallery view for past generations
- Style preview functionality
- Batch generation capabilities
- Full backend for Plot/Story Setup and Character Management tabs

## License

[Your chosen license]

## Contributing

[Your contribution guidelines] 