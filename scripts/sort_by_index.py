import json

def sort_jsonl_by_index_inplace(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [json.loads(line) for line in f]

    # Sort by 'index'
    sorted_lines = sorted(lines, key=lambda x: x['index'])

    # Remove 'index' field from each object
    for item in sorted_lines:
        item.pop('index', None)

    # Overwrite the original file
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in sorted_lines:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

# Example usage:
sort_jsonl_by_index_inplace('data/alpaca_data_pl.jsonl')