# 04. User Interface (Streamlit) - Specyfikacja Techniczna

**Plik:** `04_user_interface.md`
**Status:** Final
**Zależności:** `01_data_models.md`, `03_ai_client.md`

---

## 1. Cel i Odpowiedzialność

Ten moduł odpowiada za warstwę prezentacji (GUI). Służy do:

1. Wgrywania plików przez użytkownika.
2. Wizualizacji postępu prac AI.
3. Prezentacji wyników (obraz faktury vs odczytane dane).
4. **Edycji danych** (korekta błędów AI przez człowieka).
5. Eksportu zatwierdzonych danych do Excela.

---

## 2. Wymagania Funkcjonalne

- [ ] System **musi** wyświetlać widget wgrywania plików (obsługa PDF, JPG, PNG).
- [ ] System **musi** pokazywać podgląd pierwszej strony wgranego dokumentu.
- [ ] System **powinien** posiadać wskaźnik ładowania (spinner) podczas komunikacji z API Groka.
- [ ] System **musi** wyświetlać formularz edytowalny (`st.data_editor`) wstępnie wypełniony danymi z AI.
- [ ] System **musi** umożliwiać pobranie pliku `.xlsx` zawierającego **poprawione** (edytowane) dane, a nie surowe z AI.
- [ ] System **musi** wyświetlać komunikaty błędów w czytelnych ramkach (`st.error`).

---

## 3. Struktury Danych (Data Flow)

### Wejście (User Input)

- **Plik:** Obiekt `UploadedFile` (Streamlit).
- **Interakcja:** Kliknięcie przycisku "Analizuj fakturę".
- **Korekta:** Zmiany wartości w tabeli interfejsu.

### Wyjście (Display & Export)

- **Widok:** Dwukolumnowy layout (Obraz po lewej, Dane po prawej).
- **Plik:** `raport_faktura.xlsx` (MIME: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`).

---

## 4. Logika i Algorytm (UI Workflow)

1. **Inicjalizacja:**

   - Ustaw `st.set_page_config` (tytuł, ikona).
   - Załaduj zmienne środowiskowe (sprawdź czy API KEY istnieje).

2. **Sekcja Upload:**

   - Wyświetl `st.file_uploader`.
   - Jeśli plik jest wgrany -> Pokaż obraz (użyj modułu `02_image_processor` do wygenerowania podglądu).

3. **Sekcja Przetwarzania (po kliknięciu przycisku):**

   - Uruchom `st.spinner("Grok analizuje fakturę...")`.
   - Wywołaj `AIClient.extract_data()`.
   - Jeśli sukces -> zapisz wynik w `st.session_state` (aby nie tracić danych przy odświeżeniu).

4. **Sekcja Wyników (Human-in-the-loop):**

   - Jeśli dane są w `session_state`:
     - Podziel ekran: `col1, col2 = st.columns(2)`.
     - `col1`: Wyświetl obraz faktury.
     - `col2`: Wyświetl dane nagłówkowe (Data, NIP, Kwoty) w polach input (`st.text_input`, `st.date_input`).
     - `col2`: Wyświetl tabelę pozycji (`items`) w `st.data_editor` (pozwala dodawać/usuwać wiersze).

5. **Sekcja Eksportu:**
   - Pobierz aktualne (edytowane) wartości z widgetów.
   - Przycisk `st.download_button`:
     - Konwertuj dane do DataFrame (Pandas).
     - Zapisz do bufora pamięci jako Excel.

---

## 5. Obsługa Błędów

| Sytuacja                                  | Reakcja UI                                                          |
| ----------------------------------------- | ------------------------------------------------------------------- |
| Brak API Key w `.env`                     | Wyświetl `st.warning` z instrukcją konfiguracji.                    |
| Plik nie jest fakturą (błąd walidacji AI) | Wyświetl `st.error` z treścią błędu, ale pozwól spróbować ponownie. |
| Błąd połączenia (Grok down)               | Wyświetl `st.error` "Błąd API. Spróbuj za chwilę."                  |

---

## 6. Stack Technologiczny

- **Framework:** `streamlit`
- **Tabelki:** `pandas` (do `st.data_editor`)
- **Eksport:** `openpyxl` / `xlsxwriter`
