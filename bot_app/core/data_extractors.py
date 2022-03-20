from typing import Union
import re


def bet_data_extractor(message: str) -> Union[str, list, dict]:
    m = re.search("(\d+)", message)
    if len(m.groups()) == 0:
        raise ValueError(f"bet message must contain number")
    if len(m.groups()) > 1:
        raise ValueError(f"bet message must not contain multiple numbers")

    bet = int(m.group())
    
    return { "bet": bet }

def hit_or_stand_data_extractor(message: str) -> Union[str, list, dict]:
    if message not in ['hit', 'stand']:
        raise ValueError(f"unexpected message on hit or stand choice: {message}")

    return { "choice": message }
