from typing import Union, List, Mapping
from dataclasses import dataclass


@dataclass
class VkApiMemberProfile:
    id: int
    first_name: str
    last_name: str
    city: str

    @classmethod
    def from_dict(cls, d: Mapping[str, Union[str, list, dict]]) -> "VkApiMemberProfile":
        if d is None:
            return None

        return cls(
            id = d.get("id"),
            first_name = d.get("first_name"),
            last_name = d.get("last_name"),
            city = d.get("city", {}).get("title"),
        )


@dataclass
class VkApiChatSettings:
    title: str
    members_count: int
    active_ids: List[int]

    @classmethod
    def from_dict(cls, d: Mapping[str, Union[str, list, dict]]) -> "VkApiMemberProfile":
        if d is None:
            return None

        return cls(
            title=d.get("title"),
            members_count=int(d.get("members_count")),
            active_ids=d.get("active_ids"),
        )