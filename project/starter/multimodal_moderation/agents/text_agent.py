import sys
from pydantic_ai import Agent
from multimodal_moderation.types.model_choice import ModelChoice
from multimodal_moderation.types.moderation_result import ModerationResult, TextModerationResult
from multimodal_moderation.tracing import setup_tracing, get_tracer
from openinference.semconv.trace import SpanAttributes 

from opentelemetry.trace import (
    Status,
    StatusCode  
)

# initializing tracer object using Phoenix's convenience wrapper
setup_tracing()
tracer = get_tracer(__name__) 


# instantiating a logger 
import logging 
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(), # setting print to console
        logging.FileHandler("text_agent.log") # setting file to direct logs to 
    ]
    
)


MODERATION_INSTRUCTIONS = """
<context>
At ACME enterprise we strive for a friendly but professional interaction with our customers.
</context>

<role>
You are a customer service reviewer at ACME enterprise. You make sure that the customer
service interactions are friendly and professional.
</role>

<input>
You will receive a message from the customer representative towards the customer.
</input>

<instructions>
Detect if:
- the tone of the message is unfriendly
- the tone of the message is unprofessional
- the message contains any personally-identifiable information (PII)
</instructions>

<output>
Provide a detailed rationale for your choices as well as a confidence score between 0 and 1 on your assessment.
</output>
"""


# Implemented todo: Create a Pydantic AI Agent with:
#   - instructions=MODERATION_INSTRUCTIONS
#   - output_type=TextModerationResult
# Hint: Agent is already imported from pydantic_ai
text_moderation_agent = Agent(
    instructions=MODERATION_INSTRUCTIONS,
    output_type=TextModerationResult,
    name="text-evaluation-moderation-agent" # name of agent for logging
) 
 # Replace with your Agent


async def moderate_text(model_choice: ModelChoice, text: str) -> TextModerationResult: 

    # Implemented todo: Run the text_moderation_agent with a prompt containing the text,
    #       then return result.output
    # NOTE: in the class we used agent.run_sync but here we need to use
    #       await agent.run since this is an async function. They work exactly
    #       the same. Just do:
    #           result = await agent.run([parameters])
    #       instead of:
    #           result = agent.run_sync([parameters])
    #       like we did in the class.
    # Make sure to pass: model=model_choice.model and model_settings=model_choice.model_settings
    try:
        with tracer.start_as_current_span(
            "gemini text_moderation_agent call" # marks the inference type as llm for Pheonix 
        ) as span: 
            span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, "LLM")
            span.set_attribute(SpanAttributes.INPUT_VALUE, text) # input payload
            try: 
                response = await text_moderation_agent.run(
                    text, 
                    model=model_choice.model, 
                    model_settings=(model_choice.model_settings)
                ) 
                structured_output = response.output

                return structured_output # should return valid ModerationResult instance 
            
            # everything time an asynchronous call to gemini agent is called via this async func moderate_text OpenTelemetry span data is udpated with each response turn from the agent with status OK if successful and the exception data with the status ERROR if not 
            except Exception as e:
                func = sys._getframe().f_code.co_name
                logger.exception(f"{func} failed in running asynchronous call to Gemini agent")
                # recording exceptions in running asynchronous calls to gemini agent using gemini-2.5-flash model in span for analysis via Pheonix 
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR))
                raise # re-raising so upstream logic and my own logger sees the exception 
            else:
                span.set_output(structured_output)
                span.set_status(Status(StatusCode.OK))
    except Exception as e: 
        func = sys._getframe().f_code.co_name
        logger.exception(f"{func} encountered error in running asynchronous call to gemini image moderation model")
