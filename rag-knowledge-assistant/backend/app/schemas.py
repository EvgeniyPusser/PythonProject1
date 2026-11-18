from pydantic import BaseModel, Field, field_validator


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Question must not be empty.")
        return value


class SourceInfo(BaseModel):
    source: str
    start_index: int | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]


class DocumentInfo(BaseModel):
    name: str
    size: int


class IndexResponse(BaseModel):
    filename: str
    documents: int
    chunks: int
