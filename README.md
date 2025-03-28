# Metrics classification PoC

Proof of concept for classifying metrics based on data sensitivity.
This uses metrics metadata from Probe-Info service as input and assigns a Fides category to each metric with an LLM. See [categorize.py](categorize.py) for details.

See [categorized_metrics.csv](categorized_metrics.csv) for the output of the classification.

Observations:
* The list has all individual events, but in our case they're bundled in a single column so we probably need a way to choose the most strict category.
* It seems to miscategorize events that describe an action, for example `user.settings.privacy,onboarding.privacy_preferences_modal_crash_reporting_learn_more,"The privacy preferences model usage data "learn more" link used"."` should probably be `user.behavior` instead of `user.settings.privacy`.
* This could probably be improved if we include bug contents and data review in the prompt.
* Is this better than what we get in Fides? I'm not sure :)

How could we use this?
For telemetry tables we can easily map a column in BQ to a metric. We could extract unmapped columns from Fides via api, classify this way, and upload the results back to Fides.


## Notes
### Glean metrics classification stats
```
python metrics.py > metrics_classification_stats.md
```
Total:	8841 metrics with data_sensitivity, 7113 metrics without data_sensitivity
