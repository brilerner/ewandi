import re
import warnings


def make_placeholder(prefix="P"):
    """
    Make a placeholder in the following format:
    <prefix-3 random letters or numbers>
    """
    import random

    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    numbers = "0123456789"
    placeholder = "<" + prefix + "-"
    for _ in range(3):
        placeholder += random.choice(letters + numbers)
    placeholder += ">"
    return placeholder


def extract_placeholder(sentence):
    if not isinstance(sentence, str):
        return None

    # Pattern for correctly formatted placeholder
    correct_pattern = r"<[A-Za-z]-[A-Za-z0-9]{3}>"

    # Pattern for potential but incorrectly formatted placeholders
    potential_pattern = r"<[A-Za-z0-9-]+>"

    correct_matches = re.findall(correct_pattern, sentence)
    potential_match = re.search(potential_pattern, sentence)

    # Check if any correctly formatted placeholders are found
    if correct_matches:
        # Return the most recent (last) correctly formatted placeholder
        return correct_matches[-1]
    elif potential_match:
        # Warn if a potential but incorrectly formatted placeholder is found
        warnings.warn("Potential incorrectly formatted placeholder found.")
        return None
    else:
        return None


def test_extract_placeholder():
    test_cases = [
        ("Placeholder <A-123> and <B-XYZ> in sentence.", "<B-XYZ>"),
        ("No placeholder here.", None),
        ("Potential placeholder <C_123> with underscore.", None),
        ("Invalid placeholder <D-12345> with extra characters.", None),
        ("Invalid placeholder <E-12> with fewer characters.", None),
        ("Invalid placeholder <#-F23> with a non-letter start.", None),
        ("Multiple placeholders <G-123>, <H-456>, <I-789>.", "<I-789>"),
        ("", None),  # Empty string test
        (None, None),  # Non-string input test
    ]

    for sentence, expected in test_cases:
        result = extract_placeholder(sentence)
        assert (
            result == expected
        ), f"Test failed for: {sentence}. Expected {expected}, got {result}"

    print("All tests passed.")


# Run the test function

if __name__ == "__main__":
    # Run the test function
    test_extract_placeholder()
