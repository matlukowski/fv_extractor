# 🔒 Bezpieczeństwo Aplikacji

## Autentykacja hasłem

Aplikacja posiada wbudowany system logowania zabezpieczający dostęp do funkcjonalności.

### Jak to działa?

- Przy pierwszym wejściu na stronę użytkownik musi wprowadzić hasło
- Po poprawnym zalogowaniu sesja pozostaje aktywna
- **Opcja "Zapamiętaj mnie"** - hasło zapisuje się w przeglądarce (localStorage)
- Przy kolejnym wejściu użytkownik jest automatycznie zalogowany
- Użytkownik może się wylogować klikając przycisk "Wyloguj" w sidebarze
- Możliwość usunięcia zapisanego hasła z przeglądarki (checkbox w sidebarze)

### Konfiguracja hasła

#### Dla użytku lokalnego:

1. Skopiuj `.env.example` do `.env`
2. Ustaw hasło w pliku `.env`:
   ```env
   APP_PASSWORD=TwojeSuper$ilneHasło123!
   ```
3. Uruchom aplikację: `streamlit run app.py`

#### Dla Streamlit Cloud:

1. W panelu Streamlit Cloud wejdź w Settings → Secrets
2. Dodaj hasło:
   ```toml
   APP_PASSWORD = "TwojeSuper$ilneHasło123!"
   ```
3. Zapisz i zrestartuj aplikację

### Zalecenia dotyczące hasła

✅ **Dobre praktyki:**
- Minimum 12 znaków
- Kombinacja: wielkie litery, małe litery, cyfry, znaki specjalne
- Unikalne hasło (nie używane nigdzie indziej)
- Przykład: `Fv@Ekstr4kt0r#2025!`

❌ **Czego unikać:**
- Proste słowa (`haslo`, `password123`)
- Daty urodzenia, imiona
- Krótkie hasła (< 8 znaków)

### Wyłączenie autentykacji (NIE ZALECANE dla aplikacji publicznych)

Jeśli chcesz wyłączyć logowanie:

**Lokalnie:** Usuń lub zostaw puste `APP_PASSWORD` w `.env`
```env
# APP_PASSWORD=
```

**Streamlit Cloud:** Usuń `APP_PASSWORD` z Secrets

⚠️ **Ostrzeżenie:** Bez hasła każdy będzie mógł korzystać z Twojej aplikacji i zużywać Twój limit API!

### Udostępnianie hasła innym użytkownikom

Jeśli chcesz dać komuś dostęp do aplikacji:

1. **Bezpiecznie przekaż hasło:**
   - Nie wysyłaj przez email/SMS w czystej postaci
   - Użyj szyfrowanego komunikatora (Signal, WhatsApp)
   - Przekaż osobiście lub przez telefon

2. **Poinformuj o adresie aplikacji:**
   - Lokalnie: `http://localhost:8501`
   - Streamlit Cloud: `https://twoja-nazwa.streamlit.app/`

### Zmiana hasła

1. Zmień wartość `APP_PASSWORD` w `.env` (lokalnie) lub Secrets (cloud)
2. Uruchom ponownie aplikację
3. Wszyscy użytkownicy będą musieli zalogować się ponownie z nowym hasłem

### Funkcja "Zapamiętaj mnie"

Aplikacja posiada opcję **"💾 Zapamiętaj mnie na tym urządzeniu"**:

**Jak działa:**
- Hasło jest zapisywane w localStorage przeglądarki (lokalnie na Twoim komputerze)
- Przy kolejnym wejściu na stronę użytkownik jest automatycznie zalogowany
- Hasło NIE jest wysyłane do żadnego serwera - pozostaje tylko w Twojej przeglądarce

**Bezpieczeństwo:**
- ✅ Wygodne na prywatnym komputerze/laptopie
- ⚠️ NIE używaj na komputerach publicznych/współdzielonych!
- 🗑️ Możesz usunąć zapisane hasło w każdej chwili (checkbox w sidebarze)

**Usunięcie zapisanego hasła:**
1. Zaloguj się do aplikacji
2. W sidebarze zaznacz "🗑️ Usuń zapisane hasło"
3. Kliknij "🚪 Wyloguj"
4. Hasło zostanie usunięte z przeglądarki

### FAQ

**Q: Co się stanie jeśli zapomnę hasła?**
A: Musisz je zresetować w pliku `.env` (lokalnie) lub w Settings → Secrets (Streamlit Cloud).

**Q: Czy hasło jest bezpieczne?**
A: Tak, hasło nigdy nie jest wysyłane do żadnego serwera poza Twoim. Jest porównywane lokalnie w aplikacji.

**Q: Czy "Zapamiętaj mnie" jest bezpieczne?**
A: Hasło jest zapisane w localStorage przeglądarki (lokalnie na Twoim urządzeniu). Jest to bezpieczne na prywatnym komputerze, ale NIE używaj tej opcji na komputerach publicznych.

**Q: Czy mogę mieć różne hasła dla różnych użytkowników?**
A: Nie w podstawowej wersji. Wszyscy użytkownicy używają tego samego hasła. Jeśli potrzebujesz zarządzania wieloma użytkownikami, rozważ rozbudowę systemu autentykacji.

**Q: Czy sesja wygasa?**
A: Sesja jest aktywna dopóki użytkownik nie zamknie karty przeglądarki lub nie kliknie "Wyloguj". Jeśli zaznaczyłeś "Zapamiętaj mnie", będziesz automatycznie zalogowany przy kolejnym wejściu.

**Q: Jak całkowicie wyczyścić zapisane hasło?**
A:
1. Zaloguj się → w sidebarze zaznacz "Usuń zapisane hasło" → Wyloguj
2. LUB wyczyść localStorage przeglądarki (F12 → Application/Storage → Local Storage → usuń `fv_extractor_password`)
