from typing import Union


def bet_data_extractor(message: str) -> Union[str, list, dict]:
    try:
        bet = int(message.strip())
    except ValueError as e:
        raise ValueError(f"cannot extract bet from message: {message}") from e
    
    if bet <= 0:
        raise ValueError(f"bet must be positive but equals: {bet}")
    
    return { "bet": bet }

def hit_or_stand_data_extractor(message: str) -> Union[str, list, dict]:
    if message not in ['hit', 'stand']:
        raise ValueError(f"unexpected message on hit or stand choice: {message}")

    return { "choice": message }
