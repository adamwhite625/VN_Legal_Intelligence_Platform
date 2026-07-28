"""
Voice synthesis API using AWS Polly.
"""

import logging
import boto3
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/synthesize")
async def synthesize_speech(request: Request):
    """
    Convert input text into MP3 audio stream using AWS Polly.
    """
    try:
        body = await request.json()
        text = body.get("text", "").strip()

        if not text:
            raise HTTPException(status_code=400, detail="Text content is required for speech synthesis.")

        region = getattr(settings, "BEDROCK_REGION", "ap-southeast-1")
        polly_client = boto3.client("polly", region_name=region)

        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId="Lucia",
            Engine="neural",
        )

        def stream_audio():
            with response["AudioStream"] as stream:
                while chunk := stream.read(4096):
                    yield chunk

        return StreamingResponse(stream_audio(), media_type="audio/mpeg")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during voice synthesis with AWS Polly: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice synthesis error: {str(e)}")
