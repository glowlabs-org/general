from prompts import fill_template, parse_options

def test_fill_template():
    template = "[context]\n\nThis is a voice note recorded on [date] by [author].\n\n[chunk]\n\nPlease write [style] summary of the transcript using [format] format.\nPlease target [audience] audience. Your response should contain only the\nsummary.\n"

    filled = fill_template(template, context="test_context", date="test_date", author="test_author", chunk="test_chunk", style="concise", format="paragraph", audience="internet community")

    assert "[context]" not in filled, "context placeholder was not replaced"
    assert "[date]" not in filled, "date placeholder was not replaced"
    assert "[author]" not in filled, "author placeholder was not replaced"
    assert "[chunk]" not in filled, "chunk placeholder was not replaced"
    assert "[style]" not in filled, "style placeholder was not replaced"
    assert "[format]" not in filled, "format placeholder was not replaced"
    assert "[audience]" not in filled, "audience placeholder was not replaced"

    assert "test_context" in filled, "context value was not inserted"
    assert "test_date" in filled, "date value was not inserted"
    assert "test_author" in filled, "author value was not inserted"
    assert "test_chunk" in filled, "chunk value was not inserted"
    assert "concise" in filled, "style value was not inserted"
    assert "paragraph" in filled, "format value was not inserted"
    assert "internet community" in filled, "audience value was not inserted"

def test_parse_options():
    # Test 1
    test_string = """
    style:
      a concise
      a thorough
      an informal
      a professional
    format:
      a bullet point
      a paragraph
    audience:
      a middle school
      an internet community
      an office worker
    
    ### Instruction:
    """
    expected_output = {
        'style': ['a concise', 'a thorough', 'an informal', 'a professional'],
        'format': ['a bullet point', 'a paragraph'],
        'audience': ['a middle school', 'an internet community', 'an office worker']
    }
    assert parse_options(test_string) == expected_output

    # Test 2
    test_string = """
    parties:
      an employee and their manager
      a community moderator and an annoying internet troll
      a concerned family member and a newly promoted manager
      a concerned regulator and a wise man that is reassuring the regulator
      a small child and an experienced teacher
      a harsh critic and an even tempered executive
      two excited community members
      an excited long time fan and a new community member
      an excited employee and a Glow community member
      a visionary describing a utopian future and an excited listener
      two excited office workers
      a critic and an executive who has good answers to all criticisms
    
    ### Instruction:
      some stuff
      and more stuff
    """
    expected_output = {
        'parties': [
            'an employee and their manager',
            'a community moderator and an annoying internet troll',
            'a concerned family member and a newly promoted manager',
            'a concerned regulator and a wise man that is reassuring the regulator',
            'a small child and an experienced teacher',
            'a harsh critic and an even tempered executive',
            'two excited community members',
            'an excited long time fan and a new community member',
            'an excited employee and a Glow community member',
            'a visionary describing a utopian future and an excited listener',
            'two excited office workers',
            'a critic and an executive who has good answers to all criticisms'
        ]
    }
    assert parse_options(test_string) == expected_output

if __name__ == "__main__":
    test_fill_template()
    test_parse_options()
    print("all tests passed")
