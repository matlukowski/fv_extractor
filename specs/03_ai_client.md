# 03. AI Client (Grok-First Architecture)

Moduł odpowiedzialny za komunikację z modelem AI. Obecnie skonfigurowany pod kredyty xAI (Grok), z przygotowanym (zakomentowanym) miejscem na migrację do Claude Haiku 4.5.

## 1. Strategia Implementacji (Dual-Model Strategy)

Kod klienta musi być napisany w sposób umożliwiający zmianę dostawcy poprzez zmianę zmiennych środowiskowych lub odkomentowanie bloku konfiguracyjnego.

### Faza 1 (Active - MVP): xAI Grok

- **Provider:** xAI (via OpenAI SDK compatibility)
- **Model:** `grok-2-vision-1212`
- **Koszt:** Darmowe kredyty ($5 grant).

### Faza 2 (Future - Production): Anthropic Claude

- **Provider:** Anthropic SDK
- **Model:** Claude Haiku 4.5
- **Koszt:** Docelowa optymalizacja kosztów.

## 2. Wymagania Techniczne (Python)

### Biblioteki

Należy zainstalować `openai` (dla Groka) oraz opcjonalnie `anthropic`.

- `pip install openai>=1.58.0 anthropic python-dotenv`

**Uwaga o wersji OpenAI SDK:**
- Minimalna wersja: `openai>=1.58.0`
- Obecnie zainstalowana: `openai==2.9.0`
- **Powód upgrade'u:** Starsza wersja `1.6.1` nie była kompatybilna z nowszym `httpx==0.28.x` (błąd `proxies` parameter). Upgrade do `2.9.0` rozwiązuje problem kompatybilności z zależnościami.

### Klasa `AIClient`

Musi inicjalizować klienta w oparciu o dostępne zmienne środowiskowe.

**Wymagany wzorzec kodu (Code Pattern):**

```python
# --- KONFIGURACJA XAI (AKTYWNA) ---
from openai import OpenAI
# self.client = OpenAI(
#     api_key=os.getenv("XAI_API_KEY"),
#     base_url="[https://api.x.ai/v1](https://api.x.ai/v1)"
# )
# self.model_name = "grok-2-vision-1212"

# --- KONFIGURACJA ANTHROPIC (ZAKOMENTOWANA) ---
# from anthropic import Anthropic
# self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
# self.model_name = "claude-3-5-haiku-20241022"
```
