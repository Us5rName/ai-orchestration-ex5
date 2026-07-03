from airllm import AutoModel

MODEL= "Qwen/Qwen2.5-7B-Instruct"
MAX_LENGTH = 128
QUANT = "4bit"
# just pass a hugging face repo id — works with almost any popular model:
# model = AutoModel.from_pretrained("Qwen/Qwen3-32B")
model = AutoModel.from_pretrained(MODEL,  compression=QUANT)
# model = AutoModel.from_pretrained("meta-llama/Llama-3.2-1B")
# go bigger with the exact same one line:
#model = AutoModel.from_pretrained("Qwen/Qwen3-235B-A22B")     # 235B, runs in ~3GB
#model = AutoModel.from_pretrained("deepseek-ai/DeepSeek-V3")  # 671B, runs in ~12GB

# or use a model's local path...
#model = AutoModel.from_pretrained("/home/ubuntu/.cache/huggingface/hub/models--Qwen--Qwen3-32B/snapshots/...")

input_text = [
        'What is the capital of United States?',
        #'I like',
    ]

input_tokens = model.tokenizer(input_text,
    return_tensors="pt",
    return_attention_mask=False,
    truncation=True,
    max_length=MAX_LENGTH,
    padding=False)

generation_output = model.generate(
    input_tokens['input_ids'].cuda(),
    max_new_tokens=20,
    use_cache=True,
    return_dict_in_generate=True)

output = model.tokenizer.decode(generation_output.sequences[0])

print(output)

