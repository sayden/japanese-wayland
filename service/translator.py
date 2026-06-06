import urllib.request
import urllib.parse
import json

def translate_japanese_to_english(text: str) -> str:
    """
    Translates Japanese text to English using the free public Google Translate endpoint.
    Returns the translated string. On error, returns an empty string.
    """
    if not text.strip():
        return ""
        
    try:
        url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=ja&tl=en&dt=t&q=' + urllib.parse.quote(text)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=5).read()
        data = json.loads(response)
        
        # The result is nested: [[["translated_sentence", "original", ...], ...], ...]
        translation = ""
        for sentence in data[0]:
            if sentence[0]:
                translation += sentence[0]
                
        return translation.strip()
    except Exception as e:
        print(f"Translation failed: {e}")
        return ""
