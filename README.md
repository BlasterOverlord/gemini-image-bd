# AI Image Dataset Generator

This project batch generates synthetic images from a list of prompts using the Gemini image model. The model used is `gemini-2.5-flash-image` (nano banana).

## Workflow

1. Generate prompts (500 lines) using the Gemini Flash web UI.
2. Save the prompts into `prompts.txt`, one prompt per line.
3. Put your API key in a `.env` file as `GEMINI_API_KEY=...`.
4. Run `generate.py` to create images in the `fakes/` folder.

## Notes

- The script skips any files that already exist, so you can resume without wasting quota.
- Images are saved as JPEG with names like `fake001.jpg`, `fake002.jpg`, etc.
