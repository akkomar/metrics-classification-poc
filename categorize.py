import textwrap

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
            contents=textwrap.dedent(f"""
                You are given:
                • A JSON list of Fides categories. Each item has a "fides_key" and a "description".
                • One or more worked examples that map a metric (with type and sensitivity) to the correct "fides_key".
                • A new metric to classify.

                When deciding, look at **all** of the metric fields—name, description, metric_type, and data_sensitivity.
                If several categories might apply, pick the most specific or directly relevant one.
                If no category fits, output exactly     N/A

                Return only the chosen category’s fides_key (no extra text).

                ────────────────────────────────────────────────────────
                List of categories
                {categories}

                Examples
                ────────
                Example 1
                Metric: {{'name':'account.delete_complete',
                        'description':'Account successfully deleted',
                        'metric_type':'event',
                        'data_sensitivity':['interaction']}}
                Expected fides_key: system.operations

                Example 2
                Metric: {{'name':'login.attempt',
                        'description':'User attempted to log in',
                        'metric_type':'event',
                        'data_sensitivity':['interaction']}}
                Expected fides_key: user.authorization

                Example 3
                Metric: {{'name':'addresses.autofill_prompt_dismissed',
                        'description':'Address autofill prompt was dismissed.',
                        'metric_type':'event',
                        'data_sensitivity':['interaction']}}
                Expected fides_key: user.behavior

                ────────────────────────────────────────────────────────
                Classify this metric
                {metric}

                Respond with the single best fides_key, or “N/A”.
            """),
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
