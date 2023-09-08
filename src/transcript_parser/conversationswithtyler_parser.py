from bs4 import BeautifulSoup
from . import ParsedExchange
from typing import List, Dict

def conversationswithtyler_parser(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, 'html.parser')
    transcript = []
    current_speaker = None
    current_text = ''

    for p in soup.find_all('p'):
        if p.strong and (p.strong.text.strip() == 'TYLER COWEN:' or p.strong.text.strip() == 'COWEN:'):
            # New speaker
            if current_speaker:
                # Save the previous speaker's text
                transcript.append(ParsedExchange(current_speaker, current_text.strip()))
            current_speaker = p.strong.text.strip()
            current_text = p.text[len(current_speaker):].strip()
        elif p.strong:
            # Continuation of the same speaker's text
            current_text += ' ' + p.text.strip()

    # Save the last speaker's text
    if current_speaker:
        transcript.append({'q': current_speaker, 'a': current_text.strip()})

    return transcript