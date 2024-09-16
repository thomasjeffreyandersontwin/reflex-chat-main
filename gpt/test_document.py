import pytest
import patch

from document import Heading, SegmentableDocument

@pytest.fixture
def heading():
    return Heading("Main Heading", level=1)

@pytest.fixture
def sub_heading(heading):
    return Heading("Sub Heading", level=2, parent=heading)

def test_add_text_creates_correct_text(heading):
    heading.add_text("This is a test.")
    assert heading.text == "\nThis is a test."

    heading.add_text("First list item", list_level=1)
    assert "First list item->" in heading.text

    heading.add_text("Second list item", list_level=2)
    assert ", Second list item " in heading.text
    
def test_full_text_returns_text_only_of_parent_docv(heading):
    heading.add_text("Simple text")
    assert "Simple text\n" in heading.full_text

def test_token_length_counts_title_and_text(heading):
    # Assuming that each character is treated as a single token for simplicity
    heading.add_text("This is a test.")
    expected_length = 8  # Adjust if encoding is not 1:1
    assert heading.token_length == expected_length

def test_full_text_includes_title_text_and_text_and_title_of_sub_headings(heading, sub_heading):
    heading.add_text("Main text.")
    heading.sub_headings.append(sub_heading)
    sub_heading.add_text("Sub text")
    expected_full_text = "\nMain text.\n**Main Heading.Sub Heading**\nSub text\n"


    assert heading.full_text == expected_full_text

def test_full_title_of_sub_heading_includes_title_of_parent_heading(heading, sub_heading):
    assert heading.full_title == "Main Heading"
    assert sub_heading.full_title == "Main Heading.Sub Heading"

def test_str_returns_text_and_title_of_self_and_sub_heading(heading, sub_heading):
    heading.add_text("Main text")
    sub_heading.add_text("Sub text")
    heading.sub_headings.append(sub_heading)
    expected_str = "Title: Main Heading, Level: 1, Text: \nMain text\n    Title: Main Heading.Sub Heading, Level: 2, Text: \nSub text\n\n\n"
    assert heading.__str__(level=0).strip() == expected_str.strip()

def test_headings_with_sub_headings_return_token_length_based_on_nested_text(heading, sub_heading):
  
    heading.sub_headings.append(sub_heading)
    heading.GLOBAL_HEADING_COLLAPSE_LEVEL(1)
    sub_heading.add_text("Sub heading text")
    sub_heading.title = "Sub Heading"
    
    expected_token_length = len(Heading.ENC.encode("\n**Main Heading.Sub Heading**\n\nSub heading text\n"))
    assert heading.full_text == "\n**Main Heading.Sub Heading**\n\nSub heading text\n"
    assert heading.token_length == expected_token_length


def test_finish_list_updates_text_correctly(heading):
    heading.add_text("Item 1", list_level=1)
    heading.finish_list(0)
    assert "\nItem 1->" in heading.text
    
def test_text_property_of_heading_returns_full_text_of_sub_headings_when_at_collapse_level(heading, sub_heading):
    
    heading.sub_headings.append(sub_heading)
    Heading.GLOBAL_HEADING_COLLAPSE_LEVEL(1)
    sub_heading.add_text("Collapsed text")
    assert "Collapsed text" in heading.text

def test_sub_headings_property_of_heading_return_empty_list_if_heading_level_is_same_as_global_collapse_level(heading, sub_heading):
    heading.sub_headings.append(sub_heading)
    Heading.GLOBAL_HEADING_COLLAPSE_LEVEL(1)
    assert not heading.sub_headings

def test_sub_heading_can_ignore_below_collapse_level_if_combined_text_of_heading_is_longer_than_max_token(heading, sub_heading):
    Heading.GLOBAL_MAX_TOKEN_LENGTH(10)
    heading.add_text("This text is definitely longer than ten tokens. Alot Alot Alot Alot Alot Alot Alot AlotAlot Alot Alot Alot Alot AlotAlot Alot")
    heading.sub_headings.append(sub_heading)
    Heading.GLOBAL_HEADING_COLLAPSE_LEVEL(1)
    assert heading.sub_headings
    
def test_load_document_path():
    doc = SegmentableDocument()
    test_path = 'test'  # Relative to the root folder
    expected_path = f'./data/{test_path}'

    # Execute
    doc.load(test_path)

    # Validate that the constructed file path is as expected
    assert doc.name == expected_path, f"Document path should be {expected_path}, got {doc.name}"

def test_segmentable_document_load():
    # Set up the document
    Heading.GLOBAL_HEADING_COLLAPSE_LEVEL(4)
    doc = SegmentableDocument()
    
    # Load the document
    doc.load('test')  # Assumes the existence of './data/test.docx'

    # Check if the document is loaded correctly by inspecting the headings
    expected_headings = [
        "Agile Adoption Approach",
        "Agile Adoption Approach.Team Design and Adoption",
        "Agile Adoption Approach.Team Design and Adoption.Agree on Outcome",
        "Agile Adoption Approach.Team Design and Adoption.Co-Create Change",
        "Agile Adoption Approach.Team Design and Adoption.Adopt Behavior and Mindset",
        "Agile Adoption Approach.Team Design and Adoption.Adopt Behavior and Mindset FLow",
        "Agile Adoption Approach.Team Design and Adoption.Setup Agile Mgmt System",
        "Agile Jobs and Roles",
        "Agile Jobs and Roles.Jobs and Roles in an Agile World",
        "Agile Jobs and Roles.Jobs and Roles in an Agile World.Roles Define Accountability in a traditional world"
    ]

    actual_headings = [heading.full_title for heading in doc.headings_iterator]
    for i in range(len(expected_headings)):
        assert actual_headings[i] == expected_headings[i], f"Expected {expected_headings[i]}, got {actual_headings[i]}"

    
def test_heading_iterator_count():
    Heading.GLOBAL_HEADING_COLLAPSE_LEVEL(4)
    doc = SegmentableDocument()
    doc.load('test')  # Load the specific document for testing

    # Gather all headings using the iterator
    headings_count = len(list(doc.headings_iterator))

    # Expected number of headings as described
    expected_count = 10  # Update this count based on your actual document structure

    assert headings_count == expected_count, f"Expected {expected_count} headings, found {headings_count}"

import os

def test_save_to_file():
    doc = SegmentableDocument()
    doc.load('test')  # Load the document with known structure
    output_file_path = './data/output/test_output.txt'
    doc.save_to_file()  # Save the document's headings and their text to a file

    # Check if the file exists
    assert os.path.exists(output_file_path), "Output file does not exist."

    # Read the file and verify its contents
    with open(output_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Generate expected strings from the loaded headings, including full titles and text
    expected_contents = []
    for heading in doc.headings_iterator:
        # Include the full title and the text of each heading
        expected_contents.append(heading.full_title)
        expected_contents.append(heading.text.strip())  # Assuming text needs to be stripped of extra spaces/newlines

    # Check if each expected content piece is found in the file content
    for expected_string in expected_contents:
        assert expected_string in content, f"Expected content '{expected_string}' not found in the output file."

import pandas as pd

def test_save_to_csv():
    doc = SegmentableDocument()
    doc.load('test')  # Load the document with a known structure
    output_csv_path = './data/output/test_output.csv'
    doc.save_to_csv()  # Save the headings to a CSV file

    # Check if the CSV file exists
    assert os.path.exists(output_csv_path), "Output CSV file does not exist."

    # Read the CSV file and verify its contents
    df = pd.read_csv(output_csv_path)
    df.fillna('', inplace=True)
    # Prepare expected data from the loaded document
    expected_data = []
    for heading in doc.headings_iterator:
        # Collect full title and text from each heading
        expected_data.append({
            "Full Title": heading.full_title,
            "Text": heading.text,  # Assuming text is stripped of extra spaces/newlines
            "Token Length": heading.token_length  # If needed for verification
        })

    # Verify that each expected entry is present in the CSV
    for expected_entry in expected_data:
        assert (df['Full Title'] == expected_entry["Full Title"]).any(), f"{expected_entry['Full Title']} not found in the CSV file."
        matching_rows = df[df['Full Title'] == expected_entry["Full Title"]]
        for _, row in matching_rows.iterrows():
            assert row['Text'] == expected_entry['Text'], f"Text does not match for {expected_entry['Full Title']}"
            # Optionally check for token length match
            assert row['Token Length'] == expected_entry['Token Length'], f"Token Length does not match for {expected_entry['Full Title']}"

def test__load_from_csv():
    # Set up the document and load it from a DOCX file
    Heading.GLOBAL_HEADING_COLLAPSE_LEVEL(4)
    original_doc = SegmentableDocument('test')
    original_doc.load('test')  # Assumes the existence of './data/test.docx'
    
    # Save to CSV to create the test data
    original_doc.save_to_csv()

    # Set up a new document and load it from the previously saved CSV
    loaded_doc = SegmentableDocument('test')
    loaded_doc.load_from_csv()

    # Check if the document is loaded correctly by comparing headings from both documents
    original_headings = [(heading.full_title, heading.text) for heading in original_doc.headings_iterator]
    loaded_headings = [(heading.full_title, heading.text) for heading in loaded_doc.headings_iterator]

    # Assert that both lists of headings (title and text) are identical
     # Assert that both lists of headings (title and text) are identical, check each individually
    assert len(original_headings) == len(loaded_headings), "Number of headings mismatch"
    for i, (orig, loaded) in enumerate(zip(original_headings, loaded_headings)):
        assert orig[0] == loaded[0], f"Titles mismatch at index {i}: expected {orig[0]}, got {loaded[0]}"
        assert orig[1] == loaded[1], f"Texts mismatch at index {i}: expected {orig[1]}, got {loaded[1]}"


@pytest.fixture
def setup_document():
    # Create the main document object
    doc = SegmentableDocument()

    # Add top-level headings
    for i in range(2):  # Two top-level headers
        top_heading = Heading(f"Top Heading {i+1}")
        doc.headings.append(top_heading)

        # Add sub-headings to each top-level heading
        for j in range(2):  # Each with 2 sub-headings
            sub_heading = Heading(f"Sub Heading {i+1}.{j+1}", parent=top_heading)
            top_heading.sub_headings.append(sub_heading)

            # Add sub-sub-headings to each sub-heading
            for k in range(3):  # Each sub-heading with 3 sub-sub-headings
                sub_sub_heading = Heading(f"Sub-Sub Heading {i+1}.{j+1}.{k+1}", parent=sub_heading)
                sub_heading.sub_headings.append(sub_sub_heading)

    return doc

def test_heading_iterator(setup_document):
    # Get the list of all headings from the iterator
    all_headings = list(setup_document.headings_iterator)

    # There should be 2 top headers, each with 2 sub-headers, and each sub-header with 3 sub-sub-headers
    expected_count = 2 + (2*2) +(2 * 2 * 3)
    assert len(all_headings) == expected_count, f"Expected {expected_count} headings, got {len(all_headings)}"



# Run the test
if __name__ == "__main__":
    pytest.main()

    