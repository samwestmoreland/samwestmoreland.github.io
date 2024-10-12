import json
import hashlib
import argparse
import os
from datetime import datetime

CACHE_DIR = '.cache'

def generate_html(error):
    error = render_code_tags(error)
    tags = ', '.join(error['tags'])

    # The 'updated' field may or may not be present
    updated = error['updated'] if 'updated' in error else None

    date_html = generate_date_html(error['date'], updated)

    return f"""
    <article class="error-entry">
        <h2>{error['title']}</h2>
        <p>{error['context']}</p>
        <div class="solution">
            <h3>Explanation:</h3>
            <p>{error['explanation']}</p>
            <h3>Solution:</h3>
            <p>{error['solution']}</p>
        </div>
        <p>{tags}</p>
        {date_html}
    </article>
    """


def generate_date_html(date, updated) -> str:
    ret = "<p class='error-date'>"
    ret += f"Created: <time datetime='{date}'>{datetime.strptime(date, '%d-%m-%Y').strftime('%B %d, %Y')}</time>"

    if updated:
        ret += f"; Updated: <time datetime='{updated}'>{datetime.strptime(updated, '%d-%m-%Y').strftime('%B %d, %Y')}</time>"

    ret += "</p>"

    return ret


def render_code_tags(error) -> dict:
    """Check error entry for code (strings surrounded by backticks), and replace with <code> tags"""
    ret = {}
    fields_to_check = ['context', 'explanation', 'solution']
    for field in error:
        if field in fields_to_check:
            ret[field] = render_code_tags_in_string(error[field])
        else:
            ret[field] = error[field]

    return ret


def render_code_tags_in_string(string) -> str:
    """Replace backticks in the given string with <code> tags."""
    open = True
    ret = ""
    for i in range(len(string)):
        if string[i] == '`':
            if open:
                ret += "<code>"
                open = False
            else:
                ret += "</code>"
                open = True
        else:
            ret += string[i]

    return ret


def md5(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()


def main():
    print('Converting error entries to HTML...')
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', type=str, default='build/index.html')

    args = parser.parse_args()

    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    # Check if build dir exists and error if not
    if not 'build' in os.listdir('.'):
        raise Exception('No build directory found. Please create one first.')

    # Load JSON data
    with open('error_entries.json', 'r') as f:
        data = json.load(f)

    print('Found ' + str(len(data['errors'])) + ' entries')

    # Generate HTML for all error entries
    error_entries_html = ""
    count = 0
    for entry in data['errors']:
        print('Processing entry ' + str(count + 1) + ' of ' + str(len(data['errors'])))

        entry_hash = md5(json.dumps(entry, sort_keys=True))
        cache_file = os.path.join(CACHE_DIR, entry_hash)

        if os.path.exists(cache_file):
            print('Cache hit ' + entry_hash)
            with open(cache_file, 'r') as f:
                processed_entry = json.load(f)
        else:
            processed_entry = generate_html(entry)
            with open(cache_file, 'w') as f:
                json.dump(processed_entry, f)

        error_entries_html += processed_entry
        count += 1

    # Read the existing index.html
    with open('index.html', 'r') as f:
        index_html = f.read()

    start_marker = "<!-- ERROR_ENTRIES_START -->"
    end_marker = "<!-- ERROR_ENTRIES_END -->"
    start_index = index_html.index(start_marker) + len(start_marker)
    end_index = index_html.index(end_marker)

    new_index_html = (
        index_html[:start_index] +
        "\n" + error_entries_html + "\n" +
        index_html[end_index:]
    )

    # Write the updated HTML to the output file
    print('Writing updated HTML to ' + args.output)
    with open(args.output, 'w') as f:
        f.write(new_index_html)

    print('Done!')


if __name__ == "__main__":
    main()
