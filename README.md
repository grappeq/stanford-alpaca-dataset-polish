# 🦙 Alpaca Dataset: Polish Translation 🇵🇱

This repository provides a Polish translation of the [Stanford Alpaca dataset](https://github.com/tatsu-lab/stanford_alpaca), a popular instruction-following dataset derived from OpenAI’s `text-davinci-003` outputs.  
It also includes the scripts used to perform the translation, which may be helpful for anyone translating similar datasets or building datasets based on LLM outputs.



## Overview

- The dataset was translated from English to Polish using **Gemma 3 12B**, running **locally** in **4-bit quantized mode** via [Ollama](https://ollama.com/) on a single **RTX 4070 GPU**. This took around 100h.
- Translation was done in **batches**, using a detailed prompt to ensure consistency and structural fidelity.
- The script supports **resumption and recovery** during translation, but index fields are removed from the final dataset for cleanliness.


## Contents

| File/Directory             | Description                                                                |
|----------------------------|----------------------------------------------------------------------------|
| `data/alpaca_data.json`    | Original Stanford Alpaca dataset (English, JSON format).                   |
| `data/alpaca_data_pl.jsonl`| Translated dataset (Polish, JSON Lines format). |
| `translate_alpaca.py`      | Script for batch-translating the dataset using a local LLM.                |



## How to Use

### Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure your LLM backend (e.g. Ollama) is running and reachable via an OpenAI-compatible endpoint.

### Running the Translation

```bash
python translate_alpaca.py
```

### Translation Script

Run the translation using:

```bash
python scripts/translate_alpaca.py
```

Optional arguments:

| Flag           | Description                                  | Default                      |
|----------------|----------------------------------------------|------------------------------|
| `--input`      | Path to input JSON dataset                   | `data/alpaca_data.json`      |
| `--output`     | Output path (JSONL format)                   | `data/alpaca_data_pl.jsonl`  |
| `--batch-size` | Items to send per request                    | `10`                         |
| `--recover`    | Enable recovery mode to retry failed/skipped items | `False`                 |

Recovery mode is especially useful if:
- The script was interrupted
- The output contains malformed or incomplete entries
- You want to reattempt only the problematic parts



## Translation Prompt Logic

The script sends batches of items (each with `instruction`, `input`, and `output`) to the model using a carefully crafted prompt that:

- Requires *faithful, grammatically correct* Polish translations
- Prohibits summarizing or interpreting
- Enforces structural consistency
- Handles edge cases like empty fields and malformed responses

Example (English → Polish):

```json
{
  "instruction": "What is the capital of France?",
  "input": "",
  "output": "The capital of France is Paris."
}
```

becomes:

```json
{
  "instruction": "Jaka jest stolica Francji?",
  "input": "",
  "output": "Stolicą Francji jest Paryż."
}
```



## License

### Dataset (Polish Translation)

**License**: [CC BY-NC 4.0](DATA_LICENSE.txt)

This dataset is a derivative work based on Stanford Alpaca, which itself was derived from OpenAI model outputs.

> ⚠️ **Commercial use is strictly prohibited.**  
> This dataset is intended for research and educational purposes only.

### Code (Translation Script)

**License**: [MIT License](LICENSE)


## Disclaimers

- This project is **not affiliated with or endorsed by** Stanford, OpenAI, or Meta.
- The dataset is provided **"as is"**, with no guarantees of correctness, completeness, or legality.
- You are responsible for ensuring compliance with **all upstream licenses** and **terms of use**.

