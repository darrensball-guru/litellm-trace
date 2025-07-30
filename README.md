# LiteLLM Google Cloud Trace Exporter - Example

This project demonstrates how to use `litellm` to send LLM requests and export traces to Google Cloud Trace using OpenTelemetry.

## Description

The `main.py` script performs the following actions:
1.  Configures OpenTelemetry to use the `CloudTraceSpanExporter`, which sends trace data to your Google Cloud project.
2.  Activates the `litellm.with_opentelemetry` hook to automatically trace `litellm` API calls.
3.  Defines a custom callback function to print the model and endpoint for each successful or failed request.
4.  Makes a call to the `gemini/gemini-2.5-pro` model with a sample prompt.
5.  Includes error handling to record exceptions in the trace span.
6.  Validates that the required environment variables are set before execution.

## Prerequisites

- Python 3.8+
- `uv` installed (see https://github.com/astral-sh/uv)
- A Google Cloud Platform (GCP) project with the Cloud Trace API enabled.
- Authenticated `gcloud` CLI or Application Default Credentials (ADC) configured in your environment.

## Setup

1.  **Clone the repository or download the project files.**

2.  **Activate the Environment:**
    ```bash
    uv sync
    source .venv/bin/activate
    ```
3.  **Set the required environment variables:**
    ```bash
    export GEMINI_API_KEY="your-gemini-api-key"
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    ```

4.  **Run the Project:**
    ```bash
    uv run python main.py 
    ```

    or
    ```bash
    python main.py
    ```



## Where to Find Your Trace: The Google Cloud Trace Explorer

The primary place to view your traces is the Trace explorer in the Google Cloud Console.

### How to Find Your Trace

1. **Navigate to the Trace Explorer:**
   - Open the Google Cloud Console.
   - In the main navigation menu (the "hamburger" icon ☰), scroll down to the Observability section and select **Trace**.
   - Alternatively, use the search bar at the top and type "Trace explorer" to go there directly.

2. **Select the Correct Project:**
   - At the top of the console, ensure the project dropdown is set to your Google Cloud project. The exporter sends traces to the project associated with your credentials.

3. **Find Your Specific Trace:**
   - **Time Range:** The default view shows traces from the last hour. If you just ran the script, your trace should appear shortly. You can adjust the time range if needed. It may take a couple of minutes for the first trace to be ingested and visible.
   - **Filtering by Span Name:** To find the trace from your script, filter by the name of the parent span created in the code. In the "Filter" bar, enter a query to find the span by its name:
     ```
     root:gemini-2.5-pro-request
     ```
     If you want a unique span name, see the comment in the code and add a timestamp (mmdd or something that will break it out)
     Then alter what you are looking for span name wise.

4. **Analyze the Trace View:**
   - Click on your trace in the list to see a detailed "waterfall" graph.
   - **Parent Span:** The top-level span will be named like `gemini-2.5-pro-request`. Clicking on this shows its details, including the `llm.response.summary` attribute added in the code.
   - **Child Span:** Nested underneath, you'll see a span created automatically by LiteLLM, representing the actual call to the Google Generative AI API. Clicking on it reveals details such as the model name, request details, and other metadata added by LiteLLM's instrumentation.

### What You Should See

- A timeline showing how long the entire operation took.
- A hierarchy displaying the parent span initiating the call, and the LiteLLM span as a child operation.
- Detailed metadata for each span, useful for debugging and performance analysis.

### Troubleshooting: If You Don't See Your Trace

If your trace doesn't appear after a few minutes, check the following:

- **Authentication:** Make sure you have authenticated correctly by running `gcloud auth application-default login`. The script needs valid credentials to send data to your project.
- **API Enabled:** Verify that the Cloud Trace API is enabled in your Google Cloud project. If it's not, the exporter will fail to send traces.
- **Permissions:** The service account or user account running the script must have the Cloud Trace Agent (`roles/cloudtrace.agent`) IAM role to write trace data.
- **Project ID:** The script relies on the Google Cloud libraries to automatically detect your project ID. If you encounter issues, you can set it explicitly in your environment: `export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"`.
- **Script Completion:** The `time.sleep(5)` at the end of the script is important. Because the script is short-lived, it needs a moment to ensure the trace data is exported before the program exits. In a long-running application, this would not be necessary.
- **Check Logs:** If traces are still not appearing, there might be errors logged in your terminal that could provide clues as to what is going wrong.

## Dependencies

This project relies on the following main libraries:
- `litellm`: To simplify LLM API calls.
- `opentelemetry-sdk`: For implementing the OpenTelemetry tracing standard.
- `opentelemetry-exporter-gcp-trace`: To export trace data to Google Cloud.
