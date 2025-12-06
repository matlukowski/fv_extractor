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

**Język interfejsu:** Pełna polonizacja - wszystkie teksty UI, komunikaty, etykiety formularzy i przyciski są w języku polskim.

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

- **Widok:** Dwukolumnowy layout (Dane po lewej 75%, Akcje po prawej 25%).
- **Plik:** `faktura_{invoice_number}.xlsx` (MIME: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`).
  - Przykład: `faktura_FV001_2025.xlsx`

---

## 4. Logika i Algorytm (UI Workflow)

1. **Inicjalizacja:**

   - Ustaw `st.set_page_config` (tytuł, ikona).
   - Załaduj zmienne środowiskowe (sprawdź czy API KEY istnieje).

2. **Sekcja Upload:**

   - Wyświetl `st.file_uploader("Wybierz plik faktury (PDF, JPG, PNG)")`.
   - Jeśli plik jest wgrany:
     - Pokaż komunikat sukcesu: `"✅ Plik przesłany: {filename} ({size} KB)"`
     - Dla obrazów (JPG/PNG): Wyświetl rozwijany podgląd w `st.expander("📸 Podgląd Obrazu")`
     - Przycisk: `"🔍 Analizuj Fakturę"`

3. **Sekcja Przetwarzania (po kliknięciu przycisku):**

   - Uruchom `st.spinner("🤖 Grok analizuje Twoją fakturę...")`.
   - Wyświetl statusy: `"📸 Przetwarzanie obrazu..."`, `"🧠 Wyodrębnianie danych za pomocą AI..."`
   - Wywołaj `AIClient.extract_data()`.
   - Jeśli sukces -> zapisz wynik w `st.session_state` (aby nie tracić danych przy odświeżeniu).
   - Komunikat sukcesu: `"✅ Analiza zakończona! Sprawdź i edytuj dane poniżej."`

4. **Sekcja Wyników (Human-in-the-loop):**

   - Nagłówek: `"### 2. Sprawdź i Edytuj Wyodrębnione Dane"`
   - Jeśli dane są w `session_state`:
     - Podziel ekran: `col_data, col_actions = st.columns([3, 1])` (75% dane, 25% akcje).
     - **col_data (lewa kolumna):**
       - `"#### Nagłówek Faktury"`: Wyświetl dane nagłówkowe w 3 kolumnach (`st.text_input`, `st.date_input`)
         - Numer Faktury, Nazwa Sprzedawcy, Data Wystawienia, NIP Sprzedawcy, Nazwa Nabywcy, Waluta
       - `"#### Pozycje Faktury"`: Tabela `st.data_editor` z kolumnami po polsku:
         - Opis, Ilość, Cena Jedn. Netto, VAT %, Wartość Brutto, Kategoria
         - Pozwala dodawać/usuwać wiersze dynamicznie
       - `"#### Sumy"`: Suma Netto, Suma Brutto
     - **col_actions (prawa kolumna):**
       - `"#### Akcje"`
       - Przycisk pobierania Excel (patrz sekcja 5)
       - Przycisk `"🔄 Zacznij Od Nowa"` (czyści session_state)
       - Info box z wskazówkami

5. **Sekcja Eksportu (uproszczony flow):**
   - **Generowanie Excel:** Odbywa się automatycznie przy każdym renderze (poza kliknięciem przycisku).
   - Pobierz aktualne (edytowane) wartości z `st.session_state` (np. `edit_invoice_number`, `edit_items`).
   - Zbuduj obiekt `InvoiceData` z aktualnych wartości formularza.
   - Wygeneruj Excel buffer w pamięci.
   - **Jeden przycisk:** `st.download_button("📥 Pobierz Excel")` - bezpośrednio pobiera gotowy plik (bez dwuetapowego procesu).
   - **Obsługa błędów:** Jeśli generowanie Excel się nie powiedzie, wyświetl `st.error` zamiast przycisku pobierania.

---

## 5. Obsługa Błędów

| Sytuacja                                  | Reakcja UI                                                          |
| ----------------------------------------- | ------------------------------------------------------------------- |
| Brak API Key w `.env`                     | Wyświetl `st.warning("⚠️ **Nie znaleziono XAI_API_KEY!**")` z instrukcją konfiguracji po polsku. |
| Plik uszkodzony                           | Wyświetl `st.error("❌ Uszkodzony plik: {error}")` |
| Nieobsługiwany format                     | Wyświetl `st.error("❌ Nieobsługiwany format pliku: {error}")` |
| Błąd podczas przetwarzania                | Wyświetl `st.error("❌ Błąd podczas przetwarzania: {error}")` wraz z `st.exception(e)` |
| Błąd generowania Excel                    | Wyświetl `st.error("❌ Błąd generowania Excel: {error}")` zamiast przycisku pobierania |

---

## 6. Stack Technologiczny

- **Framework:** `streamlit`
- **Tabelki:** `pandas` (do `st.data_editor`)
- **Eksport:** `openpyxl` / `xlsxwriter`
