"""llama.cpp provider configuration and loading helpers.

Separates model-source resolution, device-to-offload mapping, and the
gatekeeper-wrapped HF Hub / disk load call from the provider service
(LlamaCppProvider). Follows the same split pattern as
transformers_helpers.py / transformers_provider.py.

Per modular-design: Single Responsibility — model resolution/loading
vs. inference service.
"""

from __future__ import annotations

from llama_cpp import Llama

from airllm_benchmark.shared.gatekeeper import call_with_rate_limit

# Separator distinguishing "<hf_repo_id>::<gguf_filename>" identifiers from
# plain local filesystem paths in the `model_id` argument accepted by
# LlamaCppProvider.load_model(). Chosen because it never appears in a
# HuggingFace repo id or in a POSIX/Windows filesystem path.
_HF_SEPARATOR = "::"


def split_model_id(model_id: str) -> tuple[str, str] | None:
    """Split a ``"<repo_id>::<filename>"`` identifier into its parts.

    Args:
        model_id: Either a local path to a ``.gguf`` file, or a
            HuggingFace-Hub identifier of the form ``"repo_id::filename"``.

    Returns:
        ``(repo_id, filename)`` tuple when *model_id* uses the HF-Hub form,
        or ``None`` when it should be treated as a local file path.
    """
    if _HF_SEPARATOR in model_id:
        repo_id, filename = model_id.split(_HF_SEPARATOR, 1)
        return repo_id, filename
    return None


def resolve_n_gpu_layers(device: str) -> int:
    """Map a ``device`` string to llama.cpp's ``n_gpu_layers`` parameter.

    Args:
        device: Target device string (e.g. ``"cpu"``, ``"cuda"``, ``"mps"``).

    Returns:
        ``0`` for CPU-only inference; ``-1`` (offload every layer) for any
        GPU-capable target, matching how ``TransformersProvider`` maps
        ``device`` onto ``.to(target)``.
    """
    return 0 if device.lower() == "cpu" else -1


def load_llama_model(model_id: str, n_gpu_layers: int) -> Llama:
    """Load a ``Llama`` instance from a local path or the HuggingFace Hub.

    Only the HF-Hub fetch path is an external network call, so only that
    branch is routed through the API Gatekeeper per ``CLAUDE.md`` §3.

    Args:
        model_id: Local ``.gguf`` path, or ``"repo_id::filename"``.
        n_gpu_layers: Number of layers to offload to GPU (``0`` = CPU-only,
            ``-1`` = all layers).

    Returns:
        A loaded ``llama_cpp.Llama`` instance, not yet used for generation.

    Raises:
        ValueError: If the local model file does not exist.
    """
    hf_parts = split_model_id(model_id)
    if hf_parts is not None:
        repo_id, filename = hf_parts
        return call_with_rate_limit(
            "huggingface",
            lambda: Llama.from_pretrained(
                repo_id=repo_id, filename=filename, n_gpu_layers=n_gpu_layers, verbose=False
            ),
        )

    return Llama(model_path=model_id, n_gpu_layers=n_gpu_layers, verbose=False)


def count_completion_tokens(llm: Llama, generated_text: str, usage: dict | None) -> int:
    """Determine the actual number of tokens generated.

    Prefers the ``usage.completion_tokens`` field returned by
    ``create_completion()``; falls back to re-tokenizing the generated text
    when usage accounting is unavailable (e.g. older bindings).

    Args:
        llm: The loaded ``Llama`` instance (used for the tokenizer fallback).
        generated_text: The text returned by the completion call.
        usage: The ``"usage"`` dict from the completion response, if present.

    Returns:
        Actual token count, at least 1.
    """
    if usage and "completion_tokens" in usage:
        return max(1, usage["completion_tokens"])
    return max(1, len(llm.tokenize(generated_text.encode("utf-8"), add_bos=False)))
