import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Ścieżka do katalogu, w którym znajdują się pliki
LEAK_DIRECTORY = '.'

def count_lines_in_leak_files():
    """Funkcja liczy łączną liczbę linii we wszystkich plikach zaczynających się na 'leak'."""
    total_lines = 0
    leak_files = [f for f in os.listdir(LEAK_DIRECTORY) if f.startswith("leak")]
    
    for leak_file in leak_files:
        try:
            with open(os.path.join(LEAK_DIRECTORY, leak_file), 'r', encoding='utf-8') as file:
                total_lines += sum(1 for _ in file)
        except FileNotFoundError:
            continue
        except UnicodeDecodeError:
            return jsonify({'error': f'Unable to decode file {leak_file}. The file may have an unsupported encoding.'}), 500
    
    return total_lines

@app.route('/api/leak/', methods=['GET'])
def leak_data():
    # Pobranie parametru z URL
    name = request.args.get('name')
    
    # Prosta walidacja, czy parametr został przekazany
    if not name:
        return jsonify({'error': 'Missing required parameter: name'}), 400

    # Wyszukiwanie plików zaczynających się na "leak" w bieżącym katalogu
    leak_files = [f for f in os.listdir(LEAK_DIRECTORY) if f.startswith("leak")]
    
    if not leak_files:
        return jsonify({'error': 'No files starting with "leak" found in the directory'}), 404
    
    # Przeszukiwanie plików w poszukiwaniu pasującego wpisu
    for leak_file in leak_files:
        try:
            with open(os.path.join(LEAK_DIRECTORY, leak_file), 'r', encoding='utf-8') as file:
                for line in file:
                    if line.startswith(name + ":"):
                        return jsonify({'result': line.strip(), 'status': 'success'}), 200
        except FileNotFoundError:
            continue
        except UnicodeDecodeError:
            return jsonify({'error': f'Unable to decode file {leak_file}. The file may have an unsupported encoding.'}), 500
    
    return jsonify({'error': 'No matching entry found'}), 404

@app.route('/api/leak/linecount', methods=['GET'])
def get_line_count():
    """Endpoint do zwrócenia łącznej liczby linii w plikach zaczynających się na 'leak'."""
    total_lines = count_lines_in_leak_files()
    return jsonify({'total_lines': total_lines, 'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
