#import pytest
from GPT_API_Facade import GPTAPIFacade
from document import SegmentableDocument
import json
from document import Heading # Import the Heading class from the document module

#@pytest.fixture
def gpt_api_facade():
    # Initialize with real document source`
    document_source = SegmentableDocument('test')
    document_source.load('test')  # Load the document
    facade = GPTAPIFacade(document_source=document_source)
    return facade

def test_generate_tuning_examples_with_real_service(gpt_api_facade):
    # Execute the method that makes API calls
    Heading.GLOBAL_HEADING_COLLAPSE_LEVEL(4)
    gpt_api_facade.chunk_processing_limit = 3
    results = gpt_api_facade.generate_tuning_examples(overwrite=True)

    # Assert the number of responses matches the headings in tre document
    assert len(results) == gpt_api_facade.chunk_processing_limit + 1

    # Check each response for the correct fields
    for result in results:
        try:
            response = json.loads(result)
            assert 'messages' in response, "The response should have 'messages' key"
            for message in response['messages']:
                assert 'role' in message, "Each message should have a 'role'"
                assert 'content' in message, "Each message should have 'content'"
                # Check if the content is formatted as JSONL if needed
                assert isinstance(message['content'], str), "Content should be a string"
        except json.JSONDecodeError:
            continue

# Run the test
#if __name__ == "__main__":
#    pytest.main(['-v', __file__])  # Verbose output for detailed results



