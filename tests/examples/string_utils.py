def clean_string(s):
    """Remove whitespace from string."""
    return s.strip()

def concat_words(word1, word2):
    """Join two words together."""
    return word1 + word2

def reverse_text(text):
    """Reverse a string."""
    output = ""
    for char in text:
        output = char + output
    return output

# Test the functions
result = concat_words("hello", "world")
cleaned = clean_string("  spaces  ")
backwards = reverse_text("code")
print(f"Result: {result}, Cleaned: {cleaned}, Reversed: {backwards}")
