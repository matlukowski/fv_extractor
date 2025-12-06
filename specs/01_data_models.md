# 01. Modele Danych (Data Schema)

Ten moduł definiuje struktury danych (klasy Pydantic), które są używane do walidacji odpowiedzi z AI oraz generowania Excela.

## 1. Obiekt: `InvoiceItem` (Pozycja na fakturze)

Reprezentuje pojedynczy wiersz w tabeli produktów/usług.

| Pole             | Typ    | Opis                                       | Wymagane            |
| ---------------- | ------ | ------------------------------------------ | ------------------- |
| `description`    | string | Nazwa towaru/usługi                        | TAK                 |
| `quantity`       | float  | Ilość                                      | TAK (domyślnie 1.0) |
| `unit_price_net` | float  | Cena jednostkowa netto                     | TAK                 |
| `vat_rate`       | int    | Stawka VAT (np. 23). Jeśli zwolniony: 0.   | TAK                 |
| `total_gross`    | float  | Wartość brutto pozycji                     | TAK                 |
| `category`       | string | Kategoria kosztowa (np. "Paliwo", "Biuro") | NIE (AI wnioskuje)  |

## 2. Obiekt: `InvoiceData` (Główny dokument)

Reprezentuje całą przetworzoną fakturę.

| Pole              | Typ               | Opis                      | Format / Uwagi                 |
| ----------------- | ----------------- | ------------------------- | ------------------------------ |
| `invoice_number`  | string            | Numer faktury             | Znormalizowany (bez spacji)    |
| `issue_date`      | date              | Data wystawienia          | YYYY-MM-DD                     |
| `seller_name`     | string            | Nazwa sprzedawcy          |                                |
| `seller_nip`      | string            | NIP sprzedawcy            | Tylko cyfry (usuń myślniki/PL) |
| `buyer_name`      | string            | Nazwa nabywcy             |                                |
| `items`           | List[InvoiceItem] | Lista pozycji             | Minimum 1 element              |
| `total_net_sum`   | float             | Suma netto z podsumowania | Weryfikacja matematyczna       |
| `total_gross_sum` | float             | Suma do zapłaty           |                                |
| `currency`        | string            | Waluta                    | Kod ISO (PLN, EUR, USD)        |

## 3. Zasady Walidacji (Pydantic Validators)

- **NIP:** Musi składać się z 10 cyfr (usuwanie znaków nieliczbowych).
- **Daty:** Konwersja różnych formatów (np. "12.01.2025") na standard `YYYY-MM-DD`.
- **Sanity Check:** Ostrzeżenie, jeśli suma pozycji nie równa się sumie głównej (ale nie blokada, bo OCR może się mylić).
