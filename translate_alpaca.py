import json
import os
import time
import argparse
from tqdm import tqdm
from openai import OpenAI

# Argument parser
parser = argparse.ArgumentParser(description="Translate Alpaca JSON data to Polish.")
parser.add_argument('--input', default='data/alpaca_data.json', help='Input JSON file path')
parser.add_argument('--output', default='data/alpaca_data_pl.jsonl', help='Output JSONL file path')
parser.add_argument('--batch-size', type=int, default=10, help='Number of items per request batch')
parser.add_argument('--recover', action='store_true', help='Enable recovery mode for skipped/malformed items')
args = parser.parse_args()

input_path = args.input
output_path = args.output
batch_size = args.batch_size
recover_mode = args.recover

# Translation prompt template
translation_prompt = """\
You are a professional translator specialized in translating chatbot training data (in JSON format) into Polish.

You will receive a JSON array of items. Each item is a JSON object with three keys: "instruction", "input", and "output". Your task is to translate all three fields into Polish while preserving the structure exactly.

⚠️ Translation guidelines:
- Be as close to the original English as possible while ensuring the Polish is natural and grammatically correct.
- Do not summarize, interpret meaning, or add context — just translate faithfully.
- Use consistent terminology and tone across all fields.
- Leave fields unchanged if they are empty (e.g., "input": "")
- Do not add, remove, or rename any keys.

📤 Output format:
Only return a valid JSON array with the translated content.
- No markdown
- No extra commentary
- No headings or explanations
- Ensure output array length matches input
- Keep the order of items the same

🧪 Example Input:
[
  {{ "instruction": "What is the capital of France?", "input": "", "output": "The capital of France is Paris." }},
  {{ "instruction": "Identify the odd one out.", "input": "Twitter, Instagram, Telegram", "output": "Telegram" }}
]

Example Output:
[
  {{ "instruction": "Jaka jest stolica Francji?", "input": "", "output": "Stolicą Francji jest Paryż." }},
  {{ "instruction": "Zidentyfikuj element, który nie pasuje.", "input": "Twitter, Instagram, Telegram", "output": "Telegram" }}
]

Your task:
Translate the following CONVERSATION into Polish:
{json_data}
"""

# Load input data
with open(input_path, 'r', encoding='utf-8') as f:
    alpaca_data = json.load(f)

client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama',
)

# Translation function
def translate_batch(convo_batch):
    prompt_formatted = translation_prompt.format(json_data=json.dumps(convo_batch, ensure_ascii=False))
    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model="gemma3:12b",
                messages=[{"role": "user", "content": prompt_formatted}]
            )
            content = response.choices[0].message.content.strip()
            content = content.replace("```json", "").replace("```", "")
            parsed = json.loads(content)
            if not isinstance(parsed, list):
                print("⚠️ Response is not a JSON array.")
                return []
            return parsed
        except json.JSONDecodeError as e:
            print(f"\n⚠️ JSONDecodeError on attempt {attempt + 1}: {e}")
            print("Raw response (first 1000 chars):\n", content[:1000])
            if attempt == 0:
                print("Retrying...\n")
                time.sleep(1)
            else:
                print("❌ Failed again. Skipping this batch.\n")
                return []

# Normal mode or recovery mode
if not recover_mode:
    # Determine last processed index
    processed_items = 0
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f_out:
            try:
                lines = f_out.readlines()
                if lines:
                    last_line = json.loads(lines[-1])
                    processed_items = last_line.get("index", len(lines))
            except Exception as e:
                print(f"⚠️ Failed to read last index from output file: {e}")

    unprocessed_data = alpaca_data[processed_items:]
    tqdm.write(
        f"Resuming from item {processed_items}, processing {len(unprocessed_data)} items in batches of {batch_size}.")

    with open(output_path, 'a', encoding='utf-8') as f_out, \
            tqdm(total=len(alpaca_data), initial=processed_items, desc="Translating") as pbar:

        for i in range(0, len(unprocessed_data), batch_size):
            batch_start = processed_items + i
            batch_end = min(processed_items + i + batch_size, len(alpaca_data))
            tqdm.write(f"🔄 Translating items {batch_start + 1}–{batch_end}/{len(alpaca_data)}")

            batch = unprocessed_data[i:i + batch_size]
            translated_batch = translate_batch(batch)

            if not isinstance(translated_batch, list):
                tqdm.write(f"⚠️ Skipping batch {batch_start + 1}–{batch_end}: Invalid response format.")
                continue

            for idx, translated in enumerate(translated_batch, start=batch_start + 1):
                if isinstance(translated, dict):
                    translated["index"] = idx
                    f_out.write(json.dumps(translated, ensure_ascii=False) + '\n')
                else:
                    tqdm.write(f"⚠️ Skipping malformed item at batch index {idx}:")
                    tqdm.write(json.dumps(translated, indent=2, ensure_ascii=False))

            pbar.update(len(batch))

else:
    print("🔁 Recovery mode activated...")

    # Get valid output indices and malformed lines
    valid_indices = set()
    malformed_indices = set()
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f_out:
            for line_num, line in enumerate(f_out, 1):
                try:
                    obj = json.loads(line)
                    index = obj.get("index")
                    if isinstance(index, int):
                        valid_indices.add(index)
                    else:
                        malformed_indices.add(line_num)
                except Exception:
                    malformed_indices.add(line_num)

    missing_indices = set(range(1, len(alpaca_data) + 1)) - valid_indices

    # Merge malformed + missing
    to_recover = sorted(list(missing_indices.union(malformed_indices)))
    print(f"Found {len(to_recover)} skipped/malformed items to recover.")

    with open(output_path, 'a', encoding='utf-8') as f_out:
        for idx in tqdm(to_recover, desc="Recovering"):
            try:
                item = alpaca_data[idx - 1]
            except IndexError:
                tqdm.write(f"❌ Invalid index {idx} in input data.")
                continue

            translated = translate_batch([item])
            if translated and isinstance(translated[0], dict):
                translated[0]["index"] = idx
                f_out.write(json.dumps(translated[0], ensure_ascii=False) + '\n')
            else:
                tqdm.write(f"⚠️ Still malformed after retry: index {idx}")
