# Deployment Guide - Streamlit Cloud

## Jak wdrożyć aplikację na Streamlit Cloud

### 1. Przygotowanie konta

1. Wejdź na https://share.streamlit.io/
2. Zaloguj się przez GitHub (klikn "Sign up" / "Continue with GitHub")
3. Autoryzuj Streamlit do dostępu do swoich repozytoriów GitHub

### 2. Utworzenie nowej aplikacji

1. Po zalogowaniu kliknij **"New app"**
2. Wypełnij formularz:
   - **Repository**: `matlukowski/fv_extractor` (twoje repo)
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: wybierz własną nazwę (np. `fv-extractor-app`)

3. Kliknij **"Advanced settings"** PRZED deploymentem

### 3. Konfiguracja sekretów (WAŻNE!)

W sekcji **"Secrets"** dodaj swój klucz API i hasło aplikacji:

```toml
XAI_API_KEY = "twoj_prawdziwy_klucz_api_z_xai"
APP_PASSWORD = "twoje_bezpieczne_haslo"
```

⚠️ **Uwaga**:
- Bez `XAI_API_KEY` aplikacja nie będzie działać!
- `APP_PASSWORD` chroni aplikację - tylko osoby z hasłem będą mogły z niej korzystać
- Używaj silnego hasła (min. 12 znaków, małe/wielkie litery, cyfry, znaki specjalne)

### 4. Deploy

1. Kliknij **"Deploy!"**
2. Poczekaj 2-5 minut na zbudowanie i uruchomienie
3. Aplikacja będzie dostępna pod adresem: `https://[twoja-nazwa].streamlit.app/`

### 5. Zarządzanie aplikacją

Po wdrożeniu możesz:

- **Edytować sekrety**: Settings → Secrets
- **Reboot app**: Settings → Reboot app (jeśli coś nie działa)
- **Zobacz logi**: Kliknij "Manage app" → View logs
- **Zmień ustawienia**: Settings (można zmienić URL, branch, itp.)

### 6. Automatyczne aktualizacje

Streamlit Cloud automatycznie:
- Wykrywa zmiany w repo GitHub
- Rebuilds aplikację przy każdym pushu do branch `main`
- Aktualizuje zależności z `requirements.txt`

### Rozwiązywanie problemów

**Problem**: Aplikacja nie uruchamia się
- Sprawdź logi w panelu Streamlit Cloud
- Upewnij się że `XAI_API_KEY` jest poprawnie ustawiony w Secrets
- Sprawdź czy wszystkie zależności są w `requirements.txt`

**Problem**: Brak klucza API
- Dodaj `XAI_API_KEY` w Settings → Secrets
- Format: `XAI_API_KEY = "xai-..."`

**Problem**: Błędy podczas buildu
- Sprawdź czy `requirements.txt` zawiera wszystkie zależności
- Upewnij się że kod działa lokalnie przed deploymentem

### Limity Streamlit Cloud (Free tier)

- ✅ Nielimitowane publiczne aplikacje
- ⚠️ 1 GB RAM (wystarczy dla tej aplikacji)
- ⚠️ Aplikacja "zasypia" po 7 dniach bez użycia
- ⚠️ Ograniczenia CPU/bandwidth

## Alternatywne opcje deploymentu

### Docker + Cloud Run / Railway / Render
Jeśli potrzebujesz więcej zasobów lub prywatności

### Heroku
Podobny proces, ale płatny

### VPS (DigitalOcean, Linode)
Pełna kontrola, wymaga konfiguracji serwera
