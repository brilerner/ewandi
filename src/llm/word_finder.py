import re

def contains_placeholder(sentence):
    if not isinstance(sentence, str):
        return None

    pattern = r"<[A-Za-z]-[A-Za-z0-9]{3}>"
    match = re.search(pattern, sentence)
    if match:
        return match.group(0)  # Return the matched placeholder
    else:
        return None

def test_contains_placeholder():
    test_cases = [
        ("This is a test sentence with a placeholder <F-RW4> in it.", "<F-RW4>"),
        ("No placeholder here.", None),
        ("Invalid placeholder <F_RW4> with underscore.", None),
        ("Invalid placeholder <F-1234> with extra characters.", None),
        ("Invalid placeholder <F-12> with fewer characters.", None),
        ("Invalid placeholder <#-RW4> with a non-letter start.", None),
        ("", None),  # Empty string test
        (None, None),  # Non-string input test
    ]

    for sentence, expected in test_cases:
        result = contains_placeholder(sentence)
        assert result == expected, f"Test failed for: {sentence}. Expected {expected}, got {result}"

    print("All tests passed.")

# Run the test function
test_contains_placeholder()
