from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MODEL_NAME = "google/flan-t5-base"
DEVICE = "cpu"  # change to "cuda" if available

print(f"Loading Flan-T5 model ({DEVICE})...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(DEVICE)


def generate(prompt: str, max_new_tokens: int = 200) -> str:
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    ).to(DEVICE)

    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        num_beams=4,
        repetition_penalty=1.5
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)