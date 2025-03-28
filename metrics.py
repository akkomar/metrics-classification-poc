import requests
import json


API_URL = "https://probeinfo.telemetry.mozilla.org/glean"


def fetch_apps() -> list:
    """
    Fetch the list of apps from Probe-Info Service API.
    """
    url = f"{API_URL}/repositories"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    apps = response.json()
    return apps


def fetch_metrics(app_name: str) -> dict:
    """
    Fetch metrics for a given app name and simplify the output.
    """
    url = f"{API_URL}/{app_name}/metrics"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    metrics = response.json()

    # Simplify the output to include only relevant fields for classification
    simplified_metrics = {
        metric_name: {
            "name": metric_name,
            "type": metric_data.get("type"),
            "description": metric_data['history'][-1].get("description") if 'history' in metric_data and metric_data['history'] else None,
            "data_sensitivity": metric_data['history'][-1].get("data_sensitivity") if 'history' in metric_data and metric_data['history'] else None,
            # "send_in_pings": metric_data['history'][-1].get("send_in_pings") if 'history' in metric_data and metric_data['history'] else None
        }
        for metric_name, metric_data in metrics.items()
    }

    return simplified_metrics


if __name__ == "__main__":

    apps = fetch_apps()


    has_sensitivity_total = 0
    has_no_sensitivity_total = 0   
    for app in apps:
        app_name = app['name']
        metrics = fetch_metrics(app_name)
        has_sensitivity = 0
        has_no_sensitivity = 0        
        for metric in metrics.values():
            if metric['data_sensitivity'] is None:
                has_no_sensitivity += 1
                print(metric)
            else:
                has_sensitivity += 1
        print(f"{app_name}:\t{has_sensitivity} metrics with data_sensitivity, {has_no_sensitivity} metrics without data_sensitivity")
        has_sensitivity_total += has_sensitivity
        has_no_sensitivity_total += has_no_sensitivity
    
    print(f"Total:\t{has_sensitivity_total} metrics with data_sensitivity, {has_no_sensitivity_total} metrics without data_sensitivity")
