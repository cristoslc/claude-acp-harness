import asyncio
import json
import logging
import time
import uuid
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class ACPCommandType(str, Enum):
    PROMPT = "prompt"
    EDIT = "edit"
    VERIFY = "verify"


class ACPRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: ACPCommandType
    payload: str
    timeout: int = Field(default=120, ge=1, le=3600)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("payload")
    @classmethod
    def payload_not_empty(cls, v):
        if not v.strip():
            raise ValueError("payload must not be empty")
        return v


class ACPStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    ESCALATION_REQUIRED = "escalation_required"
    QUEUED = "queued"


class ACPResponse(BaseModel):
    id: str
    status: ACPStatus
    result: Optional[str] = None
    error: Optional[str] = None
    duration_ms: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


ACP_START_TEMPLATE = "### ACP_START:{id} ###"
ACP_END_TEMPLATE = "### ACP_END:{id} ###"


def wrap_with_sentinels(request: ACPRequest) -> str:
    start = ACP_START_TEMPLATE.format(id=request.id)
    end = ACP_END_TEMPLATE.format(id=request.id)
    return f"{start}\n{request.payload}\n{end}"


def parse_response(raw_output: str, request_id: str) -> ACPResponse:
    start_marker = ACP_START_TEMPLATE.format(id=request_id)
    end_marker = ACP_END_TEMPLATE.format(id=request_id)
    start_idx = raw_output.find(start_marker)
    end_idx = raw_output.find(end_marker)
    if start_idx == -1 or end_idx == -1:
        return ACPResponse(
            id=request_id,
            status=ACPStatus.FAILURE,
            error="Sentinel markers not found in output",
            result=raw_output.strip(),
        )
    content = raw_output[start_idx + len(start_marker) : end_idx].strip()
    return ACPResponse(
        id=request_id,
        status=ACPStatus.SUCCESS,
        result=content,
    )
