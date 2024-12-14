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
    current_parent = None
    multi_line_key = None
    multi_line_buffer = []
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
            if multi_line_key:
                current_dict[current_parent][multi_line_key] = "\n".join(multi_line_buffer)
                multi_line_key = None
                multi_line_buffer = []
            inside_nested = False
        elif ' = ' in line:
            key, value = map(str.strip, line.split(' = ', 1))
            value = value.split('#')[0].strip()

            if value == "[":
                multi_line_key = key
                multi_line_buffer = []
            elif multi_line_key:
                multi_line_buffer.append(value)
            elif inside_nested:
                if current_parent not in current_dict:
                    current_dict[current_parent] = {}
                current_dict[current_parent][key] = make_url_friendly(value)
            else:
                if current_group == "redirects":
                    current_dict[key] = {"_": make_url_friendly(value)}
                    current_parent = key
                else:
                    result[key] = value
        elif multi_line_key:
            multi_line_buffer.append(line)

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
