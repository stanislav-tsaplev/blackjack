from typing import Union, List, Mapping
from dataclasses import dataclass


@dataclass
class VkApiMemberProfile:
    id: int
    first_name: str
    last_name: str
    online: bool

    @classmethod
    def from_dict(cls, d: Mapping[str, Union[str, list, dict]]) -> "VkApiMemberProfile":
        if d is None:
            return None

        return cls(
            id = int(d.get("id")),
            first_name = d.get("first_name"),
            last_name = d.get("last_name"),
            online = bool(d.get("online")),
        )

@dataclass
class VkApiMembersResponse:
    count: int
    profiles: List[VkApiMemberProfile]

    @classmethod
    def from_dict(cls, d: Mapping[str, Union[str, list, dict]]) -> "VkApiMembersResponse":
        if d is None:
            return None

        return cls(
            count = int(d.get("count")),
            profiles = [
                VkApiMemberProfile.from_dict(profile)
                for profile in d.get("profiles")
            ],
        )
