import json
from bs4 import BeautifulSoup


# Function to read HTML from a file, parse, and convert to JSON
def html_to_json(html_file, output_json_file):
    # Read the HTML file content
    with open(html_file, "r") as file:
        html_content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Initialize list to store publications
    publications = []

    # Iterate through each <li> element
    for li in soup.find_all("li"):
        publication = {}

        # Extract the title and link
        title_tag = li.find("a")
        publication["title"] = title_tag.get_text(strip=True)
        publication["id"] = title_tag["href"]

        # Extract the journal or source (next <a> tag)
        source_tag = li.find_all("a")[1]
        publication["container-title"] = source_tag.get_text(strip=True)
        publication["source"] = source_tag["href"]

        # Extract the authors and format as needed
        authors_text = li.get_text(strip=True).split("\n")[-2]
        authors = []
        for author in authors_text.split(","):
            name_parts = author.strip().split(" ")
            authors.append(
                {"family": name_parts[-1], "given": " ".join(name_parts[:-1])}
            )
        publication["author"] = authors

        # Add placeholder for issued date and type
        publication["type"] = "article-journal"
        publication["issued"] = {"date-parts": [["2024"]]}

        # Add the publication to the list
        publications.append(publication)

    # Convert to JSON format
    output = json.dumps(publications, indent=2)

    # Write to the output JSON file
    with open(output_json_file, "w") as json_file:
        json_file.write(output)

    print(f"Conversion successful! JSON saved to {output_json_file}")


# Input and output file paths
html_file = "publication.html"  # Replace with your HTML file path
output_json_file = "publications.json"  # Replace with the desired output file path

# Call the function to convert HTML to JSON
html_to_json(html_file, output_json_file)
