from typing import Optional, Union, Mapping
from dataclasses import dataclass
import json


@dataclass
class VkApiMessage:
    id: int
    from_id: int
    peer_id: int
    text: str
    # though actually payload is arbitrary json,  
    # in this project it is intentionally
    # assumed to be json containing a plain string
    payload: Optional[str]  # json
    # date: datetime

    @classmethod
    def from_dict(cls, d: Mapping[str, Union[str, list, dict]]) -> "VkApiMessage":
        if d is None:
            return None

        return cls(
            id=int(d.get("id")),
            from_id=int(d.get("from_id")),
            peer_id=int(d.get("peer_id")),
            text=d.get("text"),
            payload=json.loads(d["payload"]) if "payload" in d else None
            # date=datetime.utcfromtimestamp(d.get("date")),
        )

@dataclass
class VkApiUpdateObj:
    message: VkApiMessage
    # client_info: VkApiClientInfo

    @classmethod
    def from_dict(cls, d: Mapping[str, Union[str, list, dict]]) -> "VkApiUpdateObj":
        if d is None:
            return None

        return cls(
            message = VkApiMessage.from_dict(d.get("message")),
            # client_info: VkApiClientInfo.from_dict(d.get("client_info")),
        )

@dataclass
class VkApiUpdate:
    type: str
    group_id: int
    object: VkApiUpdateObj

    @classmethod
    def from_dict(cls, d: Mapping[str, Union[str, list, dict]]) -> "VkApiUpdate":
        if d is None:
            return None

        return cls(
            type = d.get("type"),
            group_id = int(d.get("group_id")),
            object = VkApiUpdateObj.from_dict(d.get("object"))
        )
