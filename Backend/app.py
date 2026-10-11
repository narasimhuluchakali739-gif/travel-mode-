
import base64
import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
from google.genai import errors as genai_errors

# Load environment variables from Backend/.env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)
CORS(app)

# API keys must be stored in Backend/.env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")

MODEL_NAME = "gemini-3.1-flash-lite"

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


PROMPTS = {
    "Summary": """
You are a professional tourist guide.
Provide a high-level overview of "{place}" in {language}.

Focus on:
- The historical significance
- Why the place is famous
- Key architectural or cultural highlights

Keep the explanation concise, engaging, and easy to follow.
Avoid excessive details and dates.
Limit the response to around 200 words.

Respond ONLY in {language}.
""",
    "Detailed": """
You are a professional tourist guide.
Provide a detailed and immersive explanation of "{place}" in {language}.

Cover:
- Historical background and timeline
- Architectural design and unique features
- Cultural importance and notable events
- Interesting facts and visitor insights

Explain concepts clearly and in a storytelling manner.
Include relevant details and examples to create a rich experience.
Limit the response to around 400 words.

Respond ONLY in {language}.
""",
}


# -----------------------------------------
# Generate the tourist guide using Gemini
# -----------------------------------------
def generate_description(place, answer_type, language):
    if not client:
        raise RuntimeError(
            "GEMINI_API_KEY is missing from Backend/.env."
        )

    prompt = PROMPTS[answer_type].format(
        place=place,
        language=language,
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty description.")

    return response.text


# -----------------------------------------
# Generate audio using Murf Falcon 2
# -----------------------------------------
def generate_speech(text, voice_id, locale):
    if not MURF_API_KEY:
        raise RuntimeError(
            "MURF_API_KEY is missing from Backend/.env."
        )

    url = "https://global.api.murf.ai/v1/speech/stream"

    headers = {
        "api-key": MURF_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "voiceId": voice_id,
        "text": text,
        "locale": locale,
        "model": "FALCON",
        "format": "MP3",
        "sampleRate": 24000,
        "channelType": "MONO",
    }

    with requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=120,
        stream=True,
    ) as response:

        if not response.ok:
            try:
                error_data = response.json()
                detail = (
                    error_data.get("error")
                    or error_data.get("message")
                    or error_data.get("detail")
                )

                if isinstance(detail, dict):
                    detail = (
                        detail.get("message")
                        or detail.get("detail")
                    )
            except ValueError:
                detail = response.text

            if not isinstance(detail, str) or not detail.strip():
                detail = "Check the Murf voice ID, locale, and request settings."

            detail = " ".join(detail.split())[:400]

            raise RuntimeError(
                f"Murf API error (HTTP {response.status_code}): {detail}"
            )

        audio_bytes = b"".join(
            response.iter_content(chunk_size=8192)
        )

    if not audio_bytes:
        raise RuntimeError("Murf returned an empty audio stream.")

    return base64.b64encode(audio_bytes).decode("ascii")


# -----------------------------------------
# Backend health check
# -----------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "success",
        "message": "Travel Guide backend is running",
    }), 200


# -----------------------------------------
# Generate description and audio
# -----------------------------------------
@app.route("/generate-audio-guide", methods=["POST"])
def generate_audio_guide():
    try:
        data = request.get_json(silent=True) or {}

        place = data.get("place")
        answer_type = data.get("answerType")
        language = data.get("language")
        voice_id = data.get("voiceId")
        locale = data.get("locale")

        if not all([
            place,
            answer_type,
            language,
            voice_id,
            locale,
        ]):
            return jsonify({
                "error": (
                    "Missing required fields: place, answerType, "
                    "language, voiceId, locale"
                )
            }), 400

        if answer_type not in PROMPTS:
            return jsonify({
                "error": "Invalid answerType. Use Summary or Detailed."
            }), 400

        # Step 1: Generate text with Gemini.
        # Murf is not called if this step fails.
        text_description = generate_description(
            place,
            answer_type,
            language,
        )

        # Step 2: Generate audio with Murf.
        encoded_audio = generate_speech(
            text_description,
            voice_id,
            locale,
        )

        return jsonify({
            "description": text_description,
            "audioBase64": encoded_audio,
        }), 200

    except genai_errors.APIError as e:
        app.logger.warning(
            "Gemini API error: HTTP %s, status %s",
            e.code,
            e.status,
        )

        if e.code == 429:
            message = (
                "Gemini quota or request limit reached. "
                "Check your Google AI Studio usage and rate limits. "
                "Murf was not called."
            )
            status_code = 429

        elif e.code == 503:
            message = (
                "Gemini is temporarily unavailable. "
                "Please try again later. Murf was not called."
            )
            status_code = 503

        else:
            message = (
                f"Gemini could not generate the guide "
                f"(HTTP {e.code}). Check the model and API settings."
            )
            status_code = (
                e.code
                if isinstance(e.code, int) and 400 <= e.code <= 599
                else 502
            )

        return jsonify({"error": message}), status_code

    except requests.RequestException:
        app.logger.exception("Murf API request failed")

        return jsonify({
            "error": (
                "Could not connect to Murf. "
                "Check your internet connection and Murf API settings."
            )
        }), 502

    except RuntimeError as e:
        app.logger.warning("Guide generation failed: %s", e)

        return jsonify({"error": str(e)}), 500

    except Exception:
        app.logger.exception("Unexpected guide generation error")

        return jsonify({
            "error": (
                "An unexpected backend error occurred. "
                "Check the VS Code terminal for details."
            )
        }), 500


# -----------------------------------------
# List Murf voices for selected locales
# -----------------------------------------
@app.route("/murf-voices", methods=["GET"])
def list_murf_voices():
    if not MURF_API_KEY:
        return jsonify({
            "error": "MURF_API_KEY is missing from Backend/.env."
        }), 500

    try:
        response = requests.get(
            "https://api.murf.ai/v1/speech/voices",
            headers={"api-key": MURF_API_KEY},
            params={"model": "falcon-2"},
            timeout=20,
        )

        if not response.ok:
            app.logger.warning(
                "Murf voice list returned HTTP %s",
                response.status_code,
            )

            return jsonify({
                "error": (
                    "Could not retrieve the Murf voice list. "
                    f"HTTP {response.status_code}."
                )
            }), 502

        voices = response.json()

        if not isinstance(voices, list):
            return jsonify({
                "error": "Murf returned an unexpected voice list format."
            }), 502

        requested_locales = {
            item.strip()
            for item in request.args.get("locales", "").split(",")
            if item.strip()
        }

        available_voices = []

        for voice in voices:
            locales_data = voice.get("supportedLocales") or {}

            if isinstance(locales_data, dict):
                locales = list(locales_data.keys())
            elif isinstance(locales_data, list):
                locales = locales_data
            else:
                locales = []

            if not locales and voice.get("locale"):
                locales = [voice["locale"]]

            matching_locales = [
                locale
                for locale in locales
                if not requested_locales or locale in requested_locales
            ]

            if matching_locales:
                available_voices.append({
                    "voiceId": voice.get("voiceId"),
                    "displayName": voice.get("displayName"),
                    "gender": voice.get("gender"),
                    "locales": matching_locales,
                })

        return jsonify(available_voices), 200

    except requests.RequestException:
        app.logger.exception("Murf voice list request failed")

        return jsonify({
            "error": "Could not connect to the Murf API."
        }), 502

    except (ValueError, TypeError):
        app.logger.exception("Unexpected Murf voice list response")

        return jsonify({
            "error": "Murf returned an unexpected voice list format."
        }), 502


if __name__ == "__main__":
    app.run(debug=True)
