import os
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

# Konfiguracja logowania błędów
logging.basicConfig(level=logging.DEBUG)

LEAK_DIRECTORY = '.'

def get_leak_files():
    """Zwraca listę plików zaczynających się na 'leak'."""
    try:
        return [f for f in os.listdir(LEAK_DIRECTORY) if f.startswith("leak")]
    except Exception as e:
        app.logger.error(f"Error listing files: {e}")
        return []

def count_lines_in_leak_files():
    """Zlicza liczbę linii we wszystkich plikach 'leak'. Jeśli wystąpi błąd, zwraca -1."""
    total_lines = 0
    for leak_file in get_leak_files():
        try:
            with open(os.path.join(LEAK_DIRECTORY, leak_file), 'r', encoding='utf-8') as file:
                total_lines += sum(1 for _ in file)
        except FileNotFoundError:
            app.logger.warning(f"File not found: {leak_file}")
            continue
        except UnicodeDecodeError:
            app.logger.error(f"Unable to decode file: {leak_file}")
            return -1  
    return total_lines

@app.route('/api/leak/', methods=['GET'])
def leak_data():
    """Wyszukuje wpisy pasujące do podanego nicku."""
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Missing required parameter: name'}), 400

    matching_entries = []
    for leak_file in get_leak_files():
        try:
            with open(os.path.join(LEAK_DIRECTORY, leak_file), 'r', encoding='utf-8') as file:
                matching_entries.extend(
                    {"file": leak_file, "data": line.strip()}
                    for line in file if line.startswith(name + ":")
                )
        except FileNotFoundError:
            app.logger.warning(f"File not found: {leak_file}")
            continue  
        except UnicodeDecodeError:
            app.logger.error(f"Unable to decode file: {leak_file}")
            return jsonify({'error': f'Unable to decode file {leak_file}'}), 500

    if matching_entries:
        return jsonify({'results': matching_entries, 'status': 'success'}), 200
    else:
        return jsonify({'error': 'No matching entry found'}), 404

@app.route('/api/leak/linecount', methods=['GET'])
def get_line_count():
    """Zwraca łączną liczbę linii w plikach zaczynających się na 'leak'."""
    total_lines = count_lines_in_leak_files()
    if total_lines == -1:
        return jsonify({'error': 'Error reading files. Some files may have unsupported encoding.'}), 500
    return jsonify({'total_lines': total_lines, 'status': 'success'}), 200

@app.route('/api/leak/filecount', methods=['GET'])
def get_file_count():
    """Zwraca liczbę plików zaczynających się na 'leak'."""
    total_files = len(get_leak_files())
    return jsonify({'total_files': total_files, 'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
