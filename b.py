import sys
import json
from urllib.parse import quote

def parse(content, noGroup=False):
    def make_url_friendly(value):
        if isinstance(value, str) and '://' in value:
            before, after = value.split('://', 1)
            return before + '://' + quote(after)
        elif isinstance(value, dict):
            return {quote(str(k)): make_url_friendly(v) for k, v in value.items()}
        return quote(value) if isinstance(value, str) else value

    result = {"redirects": {}} if noGroup else {}
    lines = [line.strip() for line in content.splitlines() if line.strip()]

    current_group = None
    current_dict = result if not noGroup else result["redirects"]
    nested_key = None
    inside_nested = False

    for line in lines:
        if line.startswith('[') and line.endswith(']') and not inside_nested:
            current_group = line.strip('[]')
            if not noGroup:
                result.setdefault(current_group, {})
                current_dict = result[current_group]
            else:
                current_dict = result["redirects"]
        elif line == '[':
            inside_nested = True
        elif line == ']':
            inside_nested = False
            nested_key = None
        elif ' = ' in line:
            key, value = map(str.strip, line.split(' = ', 1))
            value = value.split('#')[0].strip()

            if not noGroup:
                if current_group == "redirects":
                    if inside_nested:
                        if nested_key not in current_dict:
                            current_dict[nested_key] = {}
                        current_dict[nested_key][key] = make_url_friendly(value)
                    else:
                        nested_key = key
                        current_dict[key] = {"_": make_url_friendly(value)}
                else:
                    result[key] = value if current_group is None else current_dict.setdefault(key, value)
            else:
                if inside_nested:
                    if nested_key not in current_dict:
                        current_dict[nested_key] = {}
                    current_dict[nested_key][key] = make_url_friendly(value)
                else:
                    nested_key = key
                    current_dict[key] = {"_": make_url_friendly(value)}

    return result

def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <file.lko> <noGroup (True/False)>")
        sys.exit(1)

    file_path = sys.argv[1]
    noGroup = sys.argv[2].lower() == 'true'

    try:
        with open(file_path, 'r') as file:
            content = file.read()
        parsed_data = parse(content, noGroup)
        print(json.dumps(parsed_data, indent=4))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
