import os
import time
import litellm
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter


def print_endpoint_info(**kwargs):
    """Callback to print the model and the endpoint URL (api_base)."""
    api_base = kwargs.get("litellm_params", {}).get("api_base")
    model = kwargs.get("model")
    if api_base:
        print(f"\n[Callback] Model: '{model}' was sent to Endpoint: '{api_base}'")


def setup_opentelemetry():
    """Configure OpenTelemetry with Google Cloud Trace exporter."""
    print("--- Step 1: Configuring OpenTelemetry ---")
    provider = TracerProvider()
    cloud_trace_exporter = CloudTraceSpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(cloud_trace_exporter))
    trace.set_tracer_provider(provider)
    print("--- OpenTelemetry configuration is now globally set. ---")


def setup_litellm():
    """Configure LiteLLM with callbacks and OpenTelemetry integration."""
    # Enable detailed debugging (optional)
    os.environ['LITELLM_LOG'] = 'DETAILED_DEBUG'
    
    # Register callback functions
    litellm.success_callback.append(print_endpoint_info)
    litellm.failure_callback.append(print_endpoint_info)
    
    # Enable LiteLLM OpenTelemetry integration
    print("--- Step 2: Activating LiteLLM's OpenTelemetry hook ---")
    litellm.with_opentelemetry = True


def generate_text_with_tracing():
    """Generate text using Gemini model with OpenTelemetry tracing."""
    tracer = trace.get_tracer(__name__)
    unique_span_name = f"gemini-2.5-pro-request-{int(time.time())}"
    
    with tracer.start_as_current_span(unique_span_name) as span:
        try:
            print(f"\nParent span '{unique_span_name}' created.")
            print("Making call to LiteLLM with model gemini/gemini-2.5-pro...")
            messages = [{"role": "user", "content": "What are the key new features in gemini 2.5 pro?"}]
            response = litellm.completion(
                model="gemini/gemini-2.5-pro",
                messages=messages,
                api_key=os.environ.get("GEMINI_API_KEY")
            )
            span.set_attribute("llm.response.summary", str(response.choices[0].message.content)[:100] + "...")
            print("Successfully received response from Gemini.")
            return response
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            print("The error has been recorded in the trace span.")
            raise


def validate_environment():
    """Validate required environment variables."""
    validation_errors = []
    if not os.getenv("GEMINI_API_KEY"):
        validation_errors.append("ERROR: Environment variable GEMINI_API_KEY is not set.")
    if not os.getenv("GOOGLE_CLOUD_PROJECT"):
        validation_errors.append("ERROR: Environment variable GOOGLE_CLOUD_PROJECT is not set.")
    
    if validation_errors:
        print("\nPlease fix the following configuration issues:")
        for error in validation_errors:
            print(f"- {error}")
        return False
    return True


def main():
    """Main function to execute the LiteLLM tracing demo."""
    print("Starting LiteLLM trace demo...")
    
    # Setup OpenTelemetry and LiteLLM
    setup_opentelemetry()
    setup_litellm()
    
    # Validate environment variables
    if not validate_environment():
        return
    
    print("\nEnvironment variables validated. Starting execution...")
    try:
        response = generate_text_with_tracing()
        if response:
            print("\nResponse:")
            print(response.choices[0].message.content)
    except Exception:
        print("\nExecution finished with an error.")
    
    print("\nWaiting for 5 seconds to ensure trace data is exported...")
    time.sleep(5)
    print("Tracing complete. Check the Google Cloud Trace console.")


if __name__ == "__main__":
    main()
