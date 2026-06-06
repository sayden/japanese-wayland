import xml.etree.ElementTree as ET
import os
import sys
from typing import List

class Definition:
    def __init__(self, reading: str, meanings: List[str], part_of_speech: str):
        self.reading = reading
        self.meanings = meanings
        self.part_of_speech = part_of_speech

class Dictionary:
    def lookup(self, text: str) -> List[Definition]:
        raise NotImplementedError()

class JMdictDictionary(Dictionary):
    def __init__(self, dict_path: str):
        self.dict_map = {}
        self._load_dict(dict_path)

    def _load_dict(self, dict_path: str):
        print(f"Loading JMdict from {dict_path}...")
        context = ET.iterparse(dict_path, events=("end",))
        
        for event, elem in context:
            if elem.tag == "entry":
                k_eles = [k.text for k in elem.findall("k_ele/keb") if k.text]
                r_eles = [r.text for r in elem.findall("r_ele/reb") if r.text]
                
                meanings = []
                pos_list = []
                for sense in elem.findall("sense"):
                    glosses = sense.findall("gloss")
                    eng_glosses = [g.text for g in glosses if g.get("{http://www.w3.org/XML/1998/namespace}lang", "eng") == "eng" and g.text]
                    if eng_glosses:
                        meanings.extend(eng_glosses)
                    
                    for pos in sense.findall("pos"):
                        if pos.text:
                            pos_list.append(pos.text)
                
                if not meanings:
                    elem.clear()
                    continue
                
                pos_str = pos_list[0] if pos_list else "unknown"
                reading = r_eles[0] if r_eles else ""
                
                def_obj = Definition(reading, meanings, pos_str)
                
                for key in k_eles + r_eles:
                    if key not in self.dict_map:
                        self.dict_map[key] = []
                    self.dict_map[key].append(def_obj)
                    
                elem.clear()
        print(f"JMdict loaded with {len(self.dict_map)} unique words.")

    def lookup(self, text: str) -> List[Definition]:
        text = "".join(text.split())
        
        results = []
        seen = set()
        
        i = 0
        n = len(text)
        
        while i < n:
            match_found = False
            max_len = min(15, n - i)
            for length in range(max_len, 0, -1):
                sub = text[i:i+length]
                if sub in self.dict_map:
                    defs = self.dict_map[sub]
                    for d in defs:
                        key = (d.reading, tuple(d.meanings))
                        if key not in seen:
                            seen.add(key)
                            # Prepend the matched substring to the reading for display clarity
                            # (so the user knows which part of the OCR text was matched)
                            display_reading = f"[{sub}] {d.reading}" if d.reading != sub else d.reading
                            results.append(Definition(display_reading, d.meanings, d.part_of_speech))
                    
                    i += length
                    match_found = True
                    break
            
            if not match_found:
                i += 1
                
        return results
