from google import genai
from google.genai.types import HttpOptions

from metrics import fetch_apps, fetch_metrics
from fides import load_categories_from_file, extract_simplified_categories


def categorize_metric(client, metric, categories)-> str:
    """
    Categorize a metric using the Google GenAI API.

    Args:
        client: GenAI client instance
        metric: Metric data to classify
        categories: List of Fides categories

    Returns:
        The fides_key of the chosen category or "N/A" if no category fits.
    """
    response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=f"""
You are given a list of Fides categories in JSON format. Each category has a "fides_key" and a "description." You are also given a single metric in JSON format. Your task is to determine the single best Fides category for that metric, based on its name and description. If multiple categories could plausibly apply, choose the one that is most specific or most directly relevant. If you cannot find a suitable category at all, return "N/A."

Return only the chosen category’s "fides_key" as plain text, with no additional commentary or explanation.

Pay attention to metric type and description. For example metric of ty `event`

List of categories:
{categories}

Metric to classify:
{metric}

Respond only with the fides_key of the chosen category, or "N/A" if no category fits.
            """,
        )
    return response.text.strip()
    

if __name__ == "__main__":
    categories = extract_simplified_categories(load_categories_from_file())

    metrics = fetch_metrics("fenix")

    client = genai.Client(
        vertexai=True, project='akomar-sandbox-438914', location='us-central1'
    )

    categorized_metrics = []

    for metric in metrics.values():
        category = categorize_metric(client, metric, categories)
        desc = metric['description'].replace('\n', "")
        categorized_metrics.append({
            'category': category,
            'name': metric['name'],
            'description': desc
        })
        print(categorized_metrics[-1])

    # Write to a CSV file
    with open('categorized_metrics.csv', 'w') as f:
        f.write("category,name,description\n")
        for item in categorized_metrics:
            f.write(f"{item['category']},{item['name']},\"{item['description']}\"\n")
