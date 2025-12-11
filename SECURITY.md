# 🔒 Bezpieczeństwo Aplikacji

## Autentykacja hasłem

Aplikacja posiada wbudowany system logowania zabezpieczający dostęp do funkcjonalności.

### Jak to działa?

- Przy pierwszym wejściu na stronę użytkownik musi wprowadzić hasło
- Po poprawnym zalogowaniu sesja pozostaje aktywna
- Użytkownik może się wylogować klikając przycisk "Wyloguj" w sidebarze

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

### FAQ

**Q: Co się stanie jeśli zapomnę hasła?**
A: Musisz je zresetować w pliku `.env` (lokalnie) lub w Settings → Secrets (Streamlit Cloud).

**Q: Czy hasło jest bezpieczne?**
A: Tak, hasło nigdy nie jest wysyłane do żadnego serwera poza Twoim. Jest porównywane lokalnie w aplikacji.

**Q: Czy mogę mieć różne hasła dla różnych użytkowników?**
A: Nie w podstawowej wersji. Wszyscy użytkownicy używają tego samego hasła. Jeśli potrzebujesz zarządzania wieloma użytkownikami, rozważ rozbudowę systemu autentykacji.

**Q: Czy sesja wygasa?**
A: Sesja jest aktywna dopóki użytkownik nie zamknie karty przeglądarki lub nie kliknie "Wyloguj". Streamlit może również resetować sesję po pewnym czasie bezczynności.
