# 00. Wizja Produktu: AI Invoice Extractor

## 1. Cel Biznesowy

Narzędzie typu "Micro-SaaS" służące do automatycznej ekstrakcji danych strukturalnych z plików faktur (PDF, JPG, PNG). Rozwiązanie ma eliminować ręczne przepisywanie danych, zamieniając obraz dokumentu w ustrukturyzowany Excel/JSON.

## 2. Architektura Wysokopoziomowa

System działa w architekturze modularnej, bezstanowej (stateless):

1. **Frontend (Streamlit):** Przyjmuje plik od użytkownika.
2. **Preprocessor:** Zamienia plik (PDF/IMG) na zoptymalizowany obraz (Base64).
3. **AI Engine (Grok MVP):** Wysyła obraz do modelu Vision LLM i odbiera JSON.
4. **Parser:** Waliduje otrzymany JSON ze ścisłym modelem danych (Pydantic).
5. **Exporter:** Generuje plik wynikowy (.xlsx).

## 3. Stack Technologiczny

- **Język:** Python 3.10+
- **UI:** Streamlit
- **AI Provider (MVP):** xAI Grok (`grok-2-vision-1212`) - via OpenAI SDK.
- **AI Provider (Docelowy):** Anthropic Claude (`claude-3-5-haiku`) - via Anthropic SDK (obecnie wyłączony).
- **Walidacja Danych:** Pydantic (Strict Mode)
- **Przetwarzanie obrazu:** `pdf2image`, `Pillow`

## 4. Wymagania Niefunkcjonalne

- **Prywatność:** Pliki są przetwarzane w pamięci RAM i usuwane natychmiast po ekstrakcji.
- **Odporność:** System musi obsłużyć błędy API i "halucynacje" formatu JSON.
- **Język:** Pełna polonizacja interfejsu użytkownika.

## 5. Deployment & Hosting

Aplikacja jest przygotowana do deployment na następujących platformach:

### Opcja 1: Streamlit Community Cloud (Rekomendowana dla MVP/Demo)
- **Koszt:** Darmowy tier
- **Deployment:** Automatyczny z GitHub repo
- **URL:** `https://{app-name}.streamlit.app`
- **Wymagania:**
  - Publiczne GitHub repository
  - Plik `requirements.txt`
  - Secrets configuration (XAI_API_KEY)
- **Zalety:** Najprostszy deployment, idealny do testów z użytkownikami

### Opcja 2: Render / Railway (Docker)
- **Koszt:** Free tier dostępny
- **Deployment:** Docker container
- **Zalety:** Większa kontrola, więcej zasobów
- **Wymagania:** Dockerfile, environment variables

### Opcja 3: Własny serwer
- **Koszt:** Zależy od providera
- **Wymagania:** Python 3.10+, poppler-utils (dla PDF processing)
