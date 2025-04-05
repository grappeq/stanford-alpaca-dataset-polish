# Alpaca Dataset: Polish Translation

**Still work in progress. About 75% complete.**

This repository provides a Polish translation of the [Alpaca dataset](https://github.com/tatsu-lab/stanford_alpaca) along with the scripts used to perform the translation.

Translation was done using Gemma 3 12b model in 4-bit quantization running locally in Ollama on a single RTX 4070. 

---

## Contents

- **`data/alpaca_data.json`**  
  Original Alpaca dataset in English.

- **`data/alpaca_data_pl.jsonl`**  
  Translated Alpaca dataset in Polish (JSON Lines format).

- **`translate_alpaca.py`**  
  The main script for translating the dataset from English to Polish.

## License

This repository contains two components, each with its own licensing terms:

### Dataset (Polish Translation of Stanford Alpaca)

**License**: [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](DATA_LICENSE.txt)

  The Polish dataset is a derivative work based on the [Stanford Alpaca dataset](https://github.com/tatsu-lab/stanford_alpaca), which in turn is derived from OpenAI's `text-davinci-003` model outputs.  
  
Due to:
  - OpenAI's restrictions on redistribution and training use of its outputs  
  - Stanford’s explicit statement that Alpaca is for research purposes only  
  
  this dataset is released strictly for research and educational use. Commercial use is prohibited.

> **Disclaimer**: This project is not affiliated with or endorsed by Stanford, OpenAI, or Meta.  
> The dataset is provided “as is” with no warranties. Users are responsible for ensuring their usage complies with all relevant upstream licenses and terms of service.

---

### Code (scripts)

**License**: [MIT License](LICENSE)

