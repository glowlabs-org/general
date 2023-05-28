def parse_options(text: str) -> dict:
    lines = text.strip().split("\n")
    options_dict = {}
    key = None
    for line in lines:
        if line.strip() == '':
            break
        if ':' in line:
            key, _ = line.split(':')
            options_dict[key.strip()] = []
        else:
            options_dict[key.strip()].append(line.strip())
    return options_dict
    
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

# Run the tests
test_parse_options()

