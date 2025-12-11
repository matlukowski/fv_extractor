# 02. Image Processor (Preprocessing)

Moduł odpowiedzialny za przygotowanie plików wejściowych do formatu akceptowanego przez Vision API.

## 1. Funkcjonalności

- Obsługa formatów wejściowych: PDF, JPG, PNG.
- Konwersja PDF wielostronicowego na listę obrazów (1 strona = 1 obraz).
- **Obsługa PDF chronionych hasłem** - automatyczne wykrywanie i uwierzytelnianie.

## 2. Wymagania Techniczne

### Funkcja `prepare_image_for_api(file_buffer, max_size=2000, jpeg_quality=85, password=None) -> List[base64_string]`

#### Parametry:
- `file_buffer` - BytesIO buffer z plikiem (PDF/JPG/PNG)
- `max_size` - maksymalny wymiar w pikselach (domyślnie: 2000)
- `jpeg_quality` - jakość kompresji JPEG 0-100 (domyślnie: 85)
- `password` - hasło do encrypted PDF (domyślnie: None)

#### Proces przetwarzania:

1. **Detekcja typu:** Sprawdź magic bytes pliku (nie MIME type).
2. **Ścieżka PDF:**
   - Użyj biblioteki `PyMuPDF` (fitz) - nie wymaga systemowych zależności.
   - Konwertuj WSZYSTKIE strony na osobne obrazy (każda strona = osobny obraz dla AI).
   - DPI: 300 dla wysokiej jakości OCR.
   - **Obsługa encrypted PDF:**
     - Automatyczne próbowanie pustego hasła (edge case dla niektórych PDF-ów)
     - Jeśli `password=None` i PDF encrypted → rzuć `PasswordProtectedPDFError`
     - Jeśli hasło podane → authenticate i przetwórz
     - Jeśli błędne hasło → rzuć `PasswordProtectedPDFError` z komunikatem "Invalid password"
3. **Optymalizacja Obrazu:**
   - Format wyjściowy: JPEG.
   - Jakość: 85.
   - Max rozmiar: Przeskaluj, jeśli dłuższy bok > 2000px (optymalizacja tokenów i czasu przesyłu).
   - Konwersja RGBA → RGB z białym tłem.
4. **Encoding:** Zwróć string w formacie Base64 gotowy do wstrzyknięcia w JSON payload.

## 3. Obsługa Błędów

### Wyjątki:
- **`UnsupportedFormatError`** - nieobsługiwany format pliku (np. pliki tekstowe)
- **`CorruptedFileError`** - uszkodzony plik lub błąd przetwarzania
- **`PasswordProtectedPDFError`** - PDF zabezpieczony hasłem (wymaga uwierzytelniania)

### Hierarchia błędów dla PDF:
```
PDF upload
    ↓
is_encrypted?
    ├─ NO → Process normally
    └─ YES → Try authenticate("")
            ├─ Success → Continue
            └─ Failed → password is None?
                       ├─ YES → PasswordProtectedPDFError("PDF is password-protected. Please provide password.")
                       └─ NO → authenticate(password)
                               ├─ Success → Continue
                               └─ Failed → PasswordProtectedPDFError("Invalid password. Please try again.")
```

## 4. Testy

### Test coverage:
- ✅ JPEG processing (2 testy)
- ✅ PNG processing (2 testy)
- ✅ Image resizing (3 testy)
- ✅ JPEG quality (2 testy)
- ✅ Base64 encoding (2 testy)
- ✅ Error handling (3 testy)
- ✅ PDF processing (6 testów):
  - Single-page PDF
  - Multi-page PDF (3 strony)
  - Password-protected PDF bez hasła (error)
  - Password-protected PDF z poprawnym hasłem (success)
  - Password-protected PDF z błędnym hasłem (error)
  - Password-protected PDF z pustym hasłem (error)
- ✅ Edge cases (3 testy)

**Wszystkie testy: 23/23 PASS**
