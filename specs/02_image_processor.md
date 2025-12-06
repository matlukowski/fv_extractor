# 02. Image Processor (Preprocessing)

Moduł odpowiedzialny za przygotowanie plików wejściowych do formatu akceptowanego przez Vision API.

## 1. Funkcjonalności

- Obsługa formatów wejściowych: PDF, JPG, PNG.
- Konwersja PDF wielostronicowego na listę obrazów (1 strona = 1 obraz).

## 2. Wymagania Techniczne

### Funkcja `prepare_image_for_api(file_buffer) -> List[base64_string]`

1. **Detekcja typu:** Sprawdź MIME type pliku.
2. **Ścieżka PDF:**
   - Użyj biblioteki `pdf2image` (wymaga zainstalowanego `poppler-utils` w systemie/kontenerze).
   - Konwertuj pierwszą stronę (i opcjonalnie ostatnią) na obraz.
3. **Optymalizacja Obrazu:**
   - Format wyjściowy: JPEG.
   - Jakość: 85.
   - Max rozmiar: Przeskaluj, jeśli dłuższy bok > 2000px (optymalizacja tokenów i czasu przesyłu).
4. **Encoding:** Zwróć string w formacie Base64 gotowy do wstrzyknięcia w JSON payload.

## 3. Obsługa Błędów

- Rzuć czytelny wyjątek, jeśli plik jest uszkodzony lub zabezpieczony hasłem.
