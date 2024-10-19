from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

class StateInfo(SQLModel):
    id: int | None = None
    abbreviation: str

class CityInfo(SQLModel):
    id: int | None = None
    name: str

class InitChatRequest(SQLModel):
    state: StateInfo
    city: CityInfo

class InitChatResponse(SQLModel):
    id: UUID
    session_id: UUID
    city: str
    state: str


class ChatListingResponse(SQLModel):
    chats : list["ChatInList"]

class ChatInList(SQLModel):
    id: UUID
    city: str
    state: str

class ChatRequest(SQLModel):
    id: UUID

class ChatResponse(SQLModel):
    id: UUID
    messages : list["MessageResponse"]
    key_indicators : list["KeyIndicatorsResponse"]

class ChatInDB(SQLModel, table = True):
    id: UUID = Field(primary_key=True)
    session_id: UUID
    city : str
    state: str
    messages: list["MessageInDB"] = Relationship(back_populates="chat")
    key_indicators : list["KeyIndicatorsInDB"] = Relationship(back_populates="chat")

    def to_response(self):
        return ChatResponse(
            id=self.id,
            messages=[message.to_response() for message in self.messages],
            key_indicators=[key_indicator.to_response() for key_indicator in self.key_indicators]
        )

    def to_listing(self):
        return ChatInList(
            id=self.id,
            city=self.city,
            state=self.state
        )

class KeyIndicatorsInDB(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    value: float
    name: str
    detail: str
    chat_id: UUID = Field(foreign_key="chatindb.id", ondelete="CASCADE")
    chat: "ChatInDB" = Relationship(back_populates="key_indicators")

    def to_response(self):
        return KeyIndicatorsResponse(
            value=self.value,
            name=self.name,
            detail=self.detail
       )

class KeyIndicatorsResponse(SQLModel):
    value: float
    name: str
    detail: str

class MessageRequest(SQLModel):
    chat_id: UUID
    query: str

class MessageInDB(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    content: str
    is_user : bool
    chat_id : UUID = Field(foreign_key="chatindb.id", ondelete="CASCADE")
    chat : "ChatInDB" = Relationship(back_populates="messages")

    def to_response(self):
        return MessageResponse(
            response=self.content,
            is_user=self.is_user,
            id=self.id
        )

class MessageResponse(SQLModel):
    id: UUID
    response: str
    is_user: bool