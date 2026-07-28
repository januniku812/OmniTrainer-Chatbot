import sys
from pydantic_ai import Agent
from pydantic_ai.messages import BinaryContent
from multimodal_moderation.types.model_choice import ModelChoice
from multimodal_moderation.types.moderation_result import ImageModerationResult
from multimodal_moderation.tracing import setup_tracing, get_tracer
from openinference.semconv.trace import SpanAttributes 

# implementing tracer logic to integrate open telemetery data from image_agent moderation runs to phoenix 
from opentelemetry.trace import (
    Status, 
    StatusCode 
)

setup_tracing()
tracer = get_tracer(__name__)

# import logging
import logging 
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(), # setting print to console
        logging.FileHandler("image_agent.log") # setting file to direct logs to 
    ]
    
)

MODERATION_INSTRUCTIONS = """
CONTEXT
At ACME enterprise we strive for a friendly but professional interaction with our customers.

ROLE
You are a customer service reviewer at ACME enterprise. You make sure that the customer 
service interactions are friendly and professional.

TASK
You will receive an image. Determine if that image is appropriate for a professional customer service setting
according to the instructions below.

INSTRUCTIONS
Detect if:
- the image is disturbing in any way
- the image contains a person, a part of a person, or any other personally-identifiable information (PII). If yes, set
    contains_pii to True.
- the image is of low quality (blurry, pixelated, underexposed, overexposed, etc.)


OUTPUT
Provide a detailed rationale for your choices.
"""

image_moderation_agent = Agent(
    instructions=MODERATION_INSTRUCTIONS,
    output_type=ImageModerationResult,
)


async def moderate_image(
    model_choice: ModelChoice,
    image_source: bytes,
    media_type: str
) -> ImageModerationResult:

    # Implemented 
    # : Create a BinaryContent object with data=image_source and media_type=media_type
    image_input = BinaryContent(
        data=image_source,
        media_type=media_type
    )

    # Implemented todo: Run the image_moderation_agent with a list containing a prompt and image_input,
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
            "gemini image_moderation_agent call" # specificies inference type as llm for phoenix integration 
        ) as span: 
            span.set_attribute(
                SpanAttributes.OPENINFERENCE_SPAN_KIND, "LLM"
            )
            span.set_attribute(
                SpanAttributes.INPUT_VALUE, [image_input]
            )
            try:
                moderation_prompt=(
                    "Please review this image for (1) whether it contains any personally-identifiable information, including any person or part of person; (2) whether the video is disturbing; and (3) whether the video is low-quality "
                )
                result = await image_moderation_agent.run(
                    user_prompt=[image_input],
                    model=model_choice.model,
                    model_settings=model_choice.model_settings
                )
                structured_output = result.output
                return structured_output

            except Exception as e:
                func = sys._getframe().f_code.co_name
                logging.exception(f"{func} encountered error in running asynchronous call to gemini image moderation model")
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR))
            else: 
                span.set_output(structured_output)
                span.set_status(Status(StatusCode.OK))

    except Exception as e:
        func = sys._getframe().f_code.co_name
        logging.exception(f"{func} encountered error in instantiating tracer span")

