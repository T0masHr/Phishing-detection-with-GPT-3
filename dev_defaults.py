
API_KEY = "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"  # the key should be loaded from envvar # os.getenv("OPENAI_API_KEY")
DEFAULT_PATH = [r"emailMessages\placeholderMessage.txt"]
demo_response = {
  "choices": [{
      "finish_reason": "stop",
      "index": 0,
      "logprobs": "null",
      "text": "\n\nThis email is a phishing email."
    }],
  "created": 1654170708,
  "id": "cmpl-5EdeeG2J4ZuhMJXjXFJif6iHNkwnK",
  "model": "text-davinci-002",
  "object": "text_completion"
}
