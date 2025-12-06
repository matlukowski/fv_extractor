"""
AI Invoice Extractor - Streamlit Application

Main entry point for the invoice data extraction tool.
Upload invoice images (PDF, JPG, PNG) → AI extracts data → Edit → Export to Excel
"""
import streamlit as st
import os
from io import BytesIO
from datetime import date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from src.processors.image_processor import prepare_image_for_api, UnsupportedFormatError, CorruptedFileError
from src.ai.grok_client import GrokClient
from src.exporters.excel_exporter import export_to_excel
from src.models.invoice_data import InvoiceData

# Page configuration
st.set_page_config(
    page_title="Ekstraktor Faktur AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def main():
    """Main application logic"""

    # Header
    st.title("📄 Ekstraktor Faktur AI")
    st.markdown("Automatyczna ekstrakcja danych z faktur przy użyciu AI")

    # Check API key
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        st.warning(
            "⚠️ **Nie znaleziono XAI_API_KEY!**\n\n"
            "Ustaw swój klucz API Grok w pliku `.env`:\n"
            "```\nXAI_API_KEY=twoj_klucz_api\n```"
        )
        st.info(
            "Pobierz klucz API z: https://console.x.ai/\n\n"
            "Po dodaniu klucza, uruchom ponownie aplikację."
        )
        return

    # File uploader
    st.markdown("### 1. Prześlij Fakturę")
    uploaded_file = st.file_uploader(
        "Wybierz plik faktury (PDF, JPG, PNG)",
        type=['pdf', 'jpg', 'jpeg', 'png'],
        help="Prześlij zeskanowaną fakturę lub obraz faktury"
    )

    if uploaded_file:
        # Display file info
        col1, col2 = st.columns([2, 1])

        with col1:
            st.success(f"✅ Plik przesłany: **{uploaded_file.name}** ({uploaded_file.size // 1024} KB)")

        with col2:
            analyze_button = st.button("🔍 Analizuj Fakturę", type="primary", use_container_width=True)

        # Show image preview
        if uploaded_file.type in ['image/jpeg', 'image/png', 'image/jpg']:
            with st.expander("📸 Podgląd Obrazu", expanded=False):
                st.image(uploaded_file, use_container_width=True)

        # Process button clicked
        if analyze_button:
            process_invoice(uploaded_file)

        # Display results if available
        if 'invoice_data' in st.session_state:
            st.markdown("---")
            display_and_edit_invoice()


def process_invoice(uploaded_file):
    """Process uploaded invoice through the extraction pipeline"""

    with st.spinner("🤖 Grok analizuje Twoją fakturę..."):
        try:
            # Step 1: Prepare image
            st.write("📸 Przetwarzanie obrazu...")
            file_buffer = BytesIO(uploaded_file.read())
            images_base64 = prepare_image_for_api(file_buffer)

            # Step 2: Extract data with AI
            st.write("🧠 Wyodrębnianie danych za pomocą AI...")
            client = GrokClient()
            invoice_data = client.extract_data(images_base64)

            # Step 3: Store in session state
            st.session_state.invoice_data = invoice_data
            st.session_state.uploaded_filename = uploaded_file.name

            st.success("✅ Analiza zakończona! Sprawdź i edytuj dane poniżej.")
            st.rerun()

        except UnsupportedFormatError as e:
            st.error(f"❌ Nieobsługiwany format pliku: {str(e)}")
        except CorruptedFileError as e:
            st.error(f"❌ Uszkodzony plik: {str(e)}")
        except Exception as e:
            st.error(f"❌ Błąd podczas przetwarzania: {str(e)}")
            st.exception(e)


def display_and_edit_invoice():
    """Display extracted invoice data with editing capabilities"""

    invoice_data = st.session_state.invoice_data

    st.markdown("### 2. Sprawdź i Edytuj Wyodrębnione Dane")

    # Two-column layout
    col_data, col_actions = st.columns([3, 1])

    with col_data:
        # Header section
        st.markdown("#### Nagłówek Faktury")

        header_col1, header_col2, header_col3 = st.columns(3)

        with header_col1:
            invoice_number = st.text_input(
                "Numer Faktury",
                value=invoice_data.invoice_number,
                key="edit_invoice_number"
            )
            seller_name = st.text_input(
                "Nazwa Sprzedawcy",
                value=invoice_data.seller_name,
                key="edit_seller_name"
            )

        with header_col2:
            issue_date = st.date_input(
                "Data Wystawienia",
                value=invoice_data.issue_date,
                key="edit_issue_date"
            )
            seller_nip = st.text_input(
                "NIP Sprzedawcy",
                value=invoice_data.seller_nip,
                key="edit_seller_nip"
            )

        with header_col3:
            buyer_name = st.text_input(
                "Nazwa Nabywcy",
                value=invoice_data.buyer_name,
                key="edit_buyer_name"
            )
            currency = st.selectbox(
                "Waluta",
                options=["PLN", "EUR", "USD"],
                index=["PLN", "EUR", "USD"].index(invoice_data.currency),
                key="edit_currency"
            )

        # Items section
        st.markdown("#### Pozycje Faktury")

        # Convert items to DataFrame for editing
        import pandas as pd
        items_df = pd.DataFrame([
            {
                "Opis": item.description,
                "Ilość": item.quantity,
                "Cena Jedn. Netto": item.unit_price_net,
                "VAT %": item.vat_rate,
                "Wartość Brutto": item.total_gross,
                "Kategoria": item.category or ""
            }
            for item in invoice_data.items
        ])

        edited_items = st.data_editor(
            items_df,
            use_container_width=True,
            num_rows="dynamic",  # Allow adding/removing rows
            key="edit_items"
        )

        # Totals section
        st.markdown("#### Sumy")

        total_col1, total_col2 = st.columns(2)

        with total_col1:
            total_net = st.number_input(
                "Suma Netto",
                value=float(invoice_data.total_net_sum),
                format="%.2f",
                key="edit_total_net"
            )

        with total_col2:
            total_gross = st.number_input(
                "Suma Brutto",
                value=float(invoice_data.total_gross_sum),
                format="%.2f",
                key="edit_total_gross"
            )

    with col_actions:
        st.markdown("#### Akcje")

        # Export to Excel - single button that downloads directly
        try:
            # Build updated invoice data from edited fields
            updated_invoice = build_updated_invoice(
                invoice_number, issue_date, seller_name, seller_nip,
                buyer_name, currency, edited_items, total_net, total_gross
            )

            # Generate Excel
            excel_buffer = export_to_excel(updated_invoice)

            # Single download button
            st.download_button(
                label="📥 Pobierz Excel",
                data=excel_buffer,
                file_name=f"faktura_{invoice_number.replace('/', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"❌ Błąd generowania Excel: {str(e)}")

        # Reset button
        if st.button("🔄 Zacznij Od Nowa", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        # Info box
        st.info(
            "**Wskazówki:**\n"
            "- Sprawdź dane wyodrębnione przez AI\n"
            "- Edytuj nieprawidłowe pola\n"
            "- Dodaj/usuń pozycje faktury\n"
            "- Pobierz Excel gdy gotowe"
        )


def build_updated_invoice(
    invoice_number, issue_date, seller_name, seller_nip,
    buyer_name, currency, items_df, total_net, total_gross
):
    """Build InvoiceData object from edited form fields"""

    # Convert DataFrame back to items list
    items = []
    for _, row in items_df.iterrows():
        items.append({
            "description": row["Opis"],
            "quantity": float(row["Ilość"]),
            "unit_price_net": float(row["Cena Jedn. Netto"]),
            "vat_rate": int(row["VAT %"]),
            "total_gross": float(row["Wartość Brutto"]),
            "category": row["Kategoria"] if row["Kategoria"] else None
        })

    # Create InvoiceData object
    return InvoiceData(
        invoice_number=invoice_number,
        issue_date=issue_date,
        seller_name=seller_name,
        seller_nip=seller_nip,
        buyer_name=buyer_name,
        items=items,
        total_net_sum=total_net,
        total_gross_sum=total_gross,
        currency=currency
    )


if __name__ == "__main__":
    main()
