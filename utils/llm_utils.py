from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

MODEL_NAME = "google/flan-t5-base"

_tokenizer = None
_model = None


def load_model():
    global _tokenizer, _model

    if _model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading Flan-T5 model ({device})...")

        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)

    return _tokenizer, _model


def generate(prompt: str, max_new_tokens: int = 200) -> str:
    tokenizer, model = load_model()

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        num_beams=4,
        repetition_penalty=1.5
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)