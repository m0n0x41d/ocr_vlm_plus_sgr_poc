# good_cheap_ocr_with_vlm_and_sgr

This repository represents a minimal POC demonstrating how, based on sufficiently small VLM models and using SoTA i[Schema Guided Reasoning](https://abdullin.com/schema-guided-reasoning/) framework as of fall 2025, quite accurate results in payment document recognition can be achieved.

This project uses the [Qwen/Qwen3-VL-8B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct) model.

The code is written using the [pydantic-ai](https://ai.pydantic.dev/) library for rapid prototyping.

The project represents a minimal but working example of how, using SGR schemas and a single system prompt, you can guide the model's attention along a chain of quite deterministic operation.

Pay attention to [sgt_models.py](receipts_ocr_poc/sgt_models.py) which contains Pydantic BaseModel definitions that define the SGR chain.

## This is poc indeed

The only file type supported by this code snippet currently is JPG. I have started testing the PoC only for the receipts use case. Typically, receipts are sent by end-users as JPG images or other image formats converted to JPG on middleware. Invoice and other images were added as snippets in the `files_to_ocr` directory only to showcase SGR.

For production use cases, such OCR can/should be enhanced in the following ways:

- image polishing and enhancement
- PDF processing without conversion to images but following the SGR chain (invoices)
- a substantial set of evaluation tests on documents of varying quality
- a router for handling special cases, such as documents in different languages (legal features, etc)
- possible fine-tuning if you will gather enough corpus and will have strong need for it.

## Try it out

With this code snippet, you can try the VLM+SGR OCR approach with any VLM model and inference provider supporting Structured Output and serving as an OpenAI-compatible API. The first place to look is [OpenRouter](https://openrouter.ai/), of course.

> But if you have some compute, you can run inference on it (if you have it – you likely know how to do it). If you have GPUs but do not know how to run inference on them, take a look at [llama.cpp](https://github.com/ggml-org/llama.cpp) or [vLLM](https://github.com/vllm-project/vllm).

1. prepare .env, set all three variables.

```bash
cp .env.example .env
```

2. install uv and sync venv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

3. put some jpg files in the `files_to_ocr` directory.

4. Fire in up in terminal with:

```bash
uv run ocr.py
```
