import json
import argparse
from datetime import datetime

def generate_html(error):
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
        <time datetime="{error['date']}" class="error-date">{datetime.strptime(error['date'], '%d-%m-%Y').strftime('%B %d, %Y')}</time>
    </article>
    """

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', type=str, default='build/index.html')

    # Check if build dir exists and error if not
    if not 'build' in os.listdir('.'):
        raise Exception('No build directory found. Please create one first.')

    # Load JSON data
    with open('error_entries.json', 'r') as f:
        data = json.load(f)

    # Generate HTML for all error entries
    error_entries_html = ""
    for error in data['errors']:
        error_entries_html += generate_html(error)

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

    # Write the updated HTML back to index.html
    with open(args.output, 'w') as f:
        f.write(new_index_html)

if __name__ == "__main__":
    main()
