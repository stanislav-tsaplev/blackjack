from dataclasses import dataclass
from typing import List


@dataclass
class VkApiMessage:
    id: int
    from_id: int
    peer_id: int
    text: str
    # date: datetime

    @classmethod
    def from_dict(cls, d):
        return cls(
            id = int(d.get("id")),
            from_id = int(d.get("from_id")),
            peer_id = int(d.get("peer_id")),
            text = d.get("text"),
            # date = datetime.utcfromtimestamp(d.get("date")),
        )

@dataclass
class VkApiUpdateObj:
    message: VkApiMessage
    # client_info: VkApiClientInfo

    @classmethod
    def from_dict(cls, d):
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
    def from_dict(cls, d):
        return cls(
            type = d.get("type"),
            group_id = int(d.get("group_id")),
            object = VkApiUpdateObj.from_dict(d.get("object"))
        )

################

@dataclass
class VkApiMemberProfile:
    id: int
    first_name: str
    last_name: str
    online: bool

    @classmethod
    def from_dict(cls, d):
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
    def from_dict(cls, d):
        return cls(
            count = int(d.get("count")),
            profiles = [
                VkApiMemberProfile.from_dict(profile)
                for profile in d.get("profiles")
            ],
        )
