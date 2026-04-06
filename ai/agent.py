"""ai/agent.py - AI Agent lokal untuk toko-ai-agent

Fungsi:
- Load model GGUF lokal
- Tanya jawab data toko
- Integrasi laporan
- Error handling aman
"""

from pathlib import Path
from typing import Optional

from llama_cpp import Llama

from config import (
    MODEL_PATH,
    AI_MAX_TOKENS,
    AI_TEMPERATURE,
    AI_CONTEXT_LENGTH,
)

from laporan import hitung_total_harian


# =========================================================
# GLOBAL MODEL
# =========================================================

llm: Optional[Llama] = None


# =========================================================
# LOAD MODEL
# =========================================================

def load_model() -> bool:
    """Load model AI lokal"""
    global llm
    try:
        if not Path(MODEL_PATH).exists():
            print(f"[ERROR] Model tidak ditemukan: {MODEL_PATH}")
            return False
        print("Memuat model AI...")
        llm = Llama(
            model_path=str(MODEL_PATH),
            n_ctx=AI_CONTEXT_LENGTH,
            verbose=False,
        )
        print("Model AI siap")
        return True
    except Exception as exc:
        print(f"[ERROR] Gagal load model: {exc}")
        return False


# =========================================================
# GENERATE RESPONSE
# =========================================================

def generate_response(prompt: str) -> str:
    """Generate jawaban dari AI"""
    global llm
    try:
        if llm is None:
            if not load_model():
                return "AI belum siap"
        response = llm.create_completion(
            prompt=prompt,
            max_tokens=AI_MAX_TOKENS,
            temperature=AI_TEMPERATURE,
        )
        text = response["choices"][0]["text"]
        return text.strip()
    except Exception as exc:
        return f"[ERROR] AI gagal merespons: {exc}"


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """Anda adalah AI kasir dan analis toko.

Tugas Anda:
- Menjawab pertanyaan tentang stok
- Menjawab pertanyaan tentang pendapatan
- Memberi saran bisnis
- Menjawab dengan singkat dan jelas
"""


# =========================================================
# TANYA AI
# =========================================================

def tanya_ai(pertanyaan: str) -> None:
    """Tanya AI dengan konteks data toko"""
    try:
        if not pertanyaan:
            print("Pertanyaan kosong")
            return
        pendapatan, biaya, laba = hitung_total_harian()
        context = f"""
DATA TOKO HARI INI
------------------
Pendapatan: Rp {pendapatan:,.0f}
Biaya:      Rp {biaya:,.0f}
Laba:       Rp {laba:,.0f}
"""
        full_prompt = (
            SYSTEM_PROMPT + "\n" +
            context + "\n" +
            "PERTANYAAN USER:\n" +
            pertanyaan + "\n" +
            "JAWABAN:"
        )
        jawaban = generate_response(full_prompt)
        print()
        print("AI:")
        print(jawaban)
    except Exception as exc:
        print(f"[ERROR] Gagal menjalankan AI: {exc}")


# =========================================================
# CLI MODE
# =========================================================

def start_ai_cli() -> None:
    """Mode interaktif AI"""
    try:
        print("AI siap. Ketik 'exit' untuk keluar.")
        while True:
            pertanyaan = input("Anda: ").strip()
            if pertanyaan.lower() in ("exit", "quit"):
                print("Keluar dari AI")
                break
            tanya_ai(pertanyaan)
    except KeyboardInterrupt:
        print()
        print("AI dihentikan user")
    except Exception as exc:
        print(f"[ERROR] AI CLI error: {exc}")


# =========================================================
# TEST MANUAL
# =========================================================

if __name__ == "__main__":
    print("TEST AI AGENT")
    if load_model():
        start_ai_cli()