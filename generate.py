import os
import time
import google.generativeai as genai
from PIL import Image
import io
from dotenv import load_dotenv

# ================= CONFIGURATION =================
MODEL_ID = "gemini-2.5-flash-image"
INPUT_FILE = "prompts.txt"
OUTPUT_FOLDER = "fakes"

# Safety settings to avoid censorship issues
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]
# =================================================

def generate_dataset():
    # 1. Setup
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY is not set. Add it to your .env file.")
        return
    genai.configure(api_key=api_key)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # 2. Read Prompts
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            prompts = [line.strip() for line in f if line.strip()]
        print(f"📂 Loaded {len(prompts)} prompts.")
    except FileNotFoundError:
        print(f"❌ ERROR: {INPUT_FILE} not found.")
        return

    print("🚀 Starting Image Generation...")

    # 3. The generation Loop
    for i, prompt_text in enumerate(prompts):
        # STRICT MAPPING: Prompt index 0 -> fake001.jpg
        # This ensures the file number ALWAYS matches the prompt line number
        file_number = i + 1 
        filename = f"fake{file_number:03d}.jpg"
        filepath = os.path.join(OUTPUT_FOLDER, filename)

        # --- Skip Logic ---
        if os.path.exists(filepath):
            # If fake001.jpg exists, we skip Prompt #1 and move to Prompt #2
            print(f"   [SKIP] {filename} already exists.")
            continue
        # ---------------------------

        # If we reach here, the file is missing. Generate it!
        print(f"[{file_number}/{len(prompts)}] Generating: {prompt_text[:50]}...")

        try:
            model = genai.GenerativeModel(MODEL_ID)
            response = model.generate_content(
                prompt_text,
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1
                ),
                safety_settings=SAFETY_SETTINGS
            )

            if response.parts:
                img_data = response.parts[0].inline_data.data
                img = Image.open(io.BytesIO(img_data))
                if img.mode not in ("RGB",):
                    img = img.convert("RGB")
                img.save(filepath, "JPEG")
                print(f"   ✅ Saved {filename}")
            else:
                print(f"   ⚠️ API returned no image!")

            # Pause to avoid rate limits
            time.sleep(10)

        except Exception as e:
            print(f"   ❌ Error on {filename}: {e}")
            if "429" in str(e):
                print("   ⏳ Rate limit hit.")
                time.sleep(30)
            else:
                time.sleep(10)

    print("\n🎉 All prompts processed!")

if __name__ == "__main__":
    generate_dataset()