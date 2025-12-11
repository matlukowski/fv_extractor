"""
AI Invoice Extractor - Streamlit Application

Main entry point for the invoice data extraction tool.
Upload invoice images (PDF, JPG, PNG) → AI extracts data → Edit → Export to Excel
"""
import streamlit as st
import streamlit.components.v1 as components
import os
from io import BytesIO
from datetime import date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from src.processors.image_processor import (
    prepare_image_for_api,
    UnsupportedFormatError,
    CorruptedFileError,
    PasswordProtectedPDFError
)
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

# Hide Streamlit default elements (Deploy button, menu)
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def get_stored_password():
    """Get password from browser's localStorage using JavaScript"""
    stored_password_html = """
    <script>
        const savedPassword = localStorage.getItem('fv_extractor_password');
        if (savedPassword) {
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: savedPassword}, '*');
        } else {
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: ''}, '*');
        }
    </script>
    """
    stored = components.html(stored_password_html, height=0)
    return stored if stored else ""


def save_password_to_storage(password):
    """Save password to browser's localStorage"""
    save_html = f"""
    <script>
        localStorage.setItem('fv_extractor_password', '{password}');
    </script>
    """
    components.html(save_html, height=0)


def clear_password_from_storage():
    """Clear password from browser's localStorage"""
    clear_html = """
    <script>
        localStorage.removeItem('fv_extractor_password');
    </script>
    """
    components.html(clear_html, height=0)


def check_authentication():
    """
    Check if user is authenticated with password.
    Returns True if authenticated, False otherwise.
    """
    # Get password from environment or secrets
    correct_password = os.getenv("APP_PASSWORD")
    if not correct_password and hasattr(st, 'secrets') and 'APP_PASSWORD' in st.secrets:
        correct_password = st.secrets["APP_PASSWORD"]

    # If no password is set, allow access (backward compatibility)
    if not correct_password:
        return True

    # Check if user is already authenticated in session
    if st.session_state.get('authenticated', False):
        return True

    # Try to auto-login from stored password
    if 'auto_login_attempted' not in st.session_state:
        st.session_state.auto_login_attempted = True
        stored_password = get_stored_password()
        if stored_password and stored_password == correct_password:
            st.session_state.authenticated = True
            st.rerun()

    # Show login form
    st.title("🔒 Logowanie")
    st.markdown("Wprowadź hasło aby uzyskać dostęp do aplikacji")

    password = st.text_input(
        "Hasło:",
        type="password",
        key="login_password"
    )

    # Remember me checkbox
    remember_me = st.checkbox(
        "💾 Zapamiętaj mnie na tym urządzeniu",
        value=False,
        help="Hasło zostanie zapisane w przeglądarce (localStorage)"
    )

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔓 Zaloguj", type="primary", use_container_width=True):
            if password == correct_password:
                st.session_state.authenticated = True

                # Save password if remember me is checked
                if remember_me:
                    save_password_to_storage(password)
                else:
                    clear_password_from_storage()

                st.success("✅ Zalogowano pomyślnie!")
                st.rerun()
            else:
                st.error("❌ Nieprawidłowe hasło!")
                clear_password_from_storage()

    st.info(
        "**Brak dostępu?**\n\n"
        "Skontaktuj się z administratorem aby otrzymać hasło."
    )

    return False


def main():
    """Main application logic"""

    # Check authentication first
    if not check_authentication():
        return  # Stop execution if not authenticated

    # Add logout button in sidebar
    with st.sidebar:
        st.markdown("### 🔐 Sesja")

        # Option to clear saved password on logout
        clear_saved = st.checkbox(
            "🗑️ Usuń zapisane hasło przy wylogowaniu",
            value=False,
            help="Wyczyści zapamiętane hasło z przeglądarki"
        )

        if st.button("🚪 Wyloguj", use_container_width=True):
            # Clear saved password if checkbox was checked
            if clear_saved:
                clear_password_from_storage()

            st.session_state.authenticated = False
            st.session_state.clear()
            st.rerun()

    # Header
    st.title("📄 Ekstraktor Faktur AI")
    st.markdown("Automatyczna ekstrakcja danych z faktur przy użyciu AI")

    # Check API key (supports both .env and Streamlit Cloud secrets)
    api_key = os.getenv("XAI_API_KEY")
    if not api_key and hasattr(st, 'secrets') and 'XAI_API_KEY' in st.secrets:
        api_key = st.secrets["XAI_API_KEY"]

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

    # Store API key in session state for use in callbacks
    st.session_state.api_key = api_key

    # Initialize session state for encrypted PDF handling
    if 'encrypted_pdf_buffer' not in st.session_state:
        st.session_state.encrypted_pdf_buffer = None
    if 'encrypted_pdf_filename' not in st.session_state:
        st.session_state.encrypted_pdf_filename = None
    if 'pdf_password_error' not in st.session_state:
        st.session_state.pdf_password_error = None

    # File uploader
    st.markdown("### 1. Prześlij Fakturę")
    uploaded_file = st.file_uploader(
        "Wybierz plik faktury (PDF, JPG, PNG)",
        type=['pdf', 'jpg', 'jpeg', 'png'],
        help="Prześlij zeskanowaną fakturę lub obraz faktury"
    )

    if uploaded_file:
        # Clear encrypted PDF state if user uploads different file
        if (st.session_state.encrypted_pdf_filename and
            st.session_state.encrypted_pdf_filename != uploaded_file.name):
            st.session_state.encrypted_pdf_buffer = None
            st.session_state.encrypted_pdf_filename = None
            st.session_state.pdf_password_error = None

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

        # === PASSWORD PROTECTION HANDLING ===
        if st.session_state.encrypted_pdf_buffer is not None:
            st.markdown("---")
            st.warning("🔒 **Ten PDF jest chroniony hasłem**")

            # Show previous password error if any
            if st.session_state.pdf_password_error:
                st.error(st.session_state.pdf_password_error)

            # Password input
            col_pass1, col_pass2 = st.columns([3, 1])

            with col_pass1:
                pdf_password = st.text_input(
                    "Wpisz hasło do pliku PDF:",
                    type="password",
                    key="pdf_password_input",
                    help="Hasło jest potrzebne do odszyfrowania pliku"
                )

            with col_pass2:
                st.write("")  # Spacing
                st.write("")
                unlock_button = st.button(
                    "🔓 Odszyfruj i Analizuj",
                    type="primary",
                    use_container_width=True,
                    disabled=not pdf_password  # Disable if empty
                )

            # Process with password
            if unlock_button and pdf_password:
                process_encrypted_pdf_with_password(pdf_password)

            # Cancel button
            if st.button("❌ Anuluj i Wyślij Inny Plik"):
                st.session_state.encrypted_pdf_buffer = None
                st.session_state.encrypted_pdf_filename = None
                st.session_state.pdf_password_error = None
                st.rerun()

            # Don't show normal analyze button in password mode
            analyze_button = False
        # Normal flow - no encryption

        # Process button clicked
        if analyze_button:
            process_invoice(uploaded_file)

        # Display results if available
        if 'invoice_data' in st.session_state:
            st.markdown("---")
            display_and_edit_invoice()


def process_invoice(uploaded_file, password=None):
    """Process uploaded invoice through the extraction pipeline"""

    # Update spinner text based on password
    spinner_text = "🤖 Grok analizuje Twoją fakturę..."
    if password:
        spinner_text = "🔓 Odszyfrowywanie PDF i analiza..."

    with st.spinner(spinner_text):
        try:
            # Step 1: Prepare image
            st.write("📸 Przetwarzanie obrazu...")
            file_buffer = BytesIO(uploaded_file.read())
            images_base64 = prepare_image_for_api(file_buffer, password=password)

            # Step 2: Extract data with AI
            st.write("🧠 Wyodrębnianie danych za pomocą AI...")
            api_key = st.session_state.get('api_key') or os.getenv("XAI_API_KEY")
            client = GrokClient(api_key=api_key)
            invoice_data = client.extract_data(images_base64)

            # Step 3: Store in session state
            st.session_state.invoice_data = invoice_data
            st.session_state.uploaded_filename = uploaded_file.name

            # Clear encrypted PDF state on success
            st.session_state.encrypted_pdf_buffer = None
            st.session_state.encrypted_pdf_filename = None
            st.session_state.pdf_password_error = None

            st.success("✅ Analiza zakończona! Sprawdź i edytuj dane poniżej.")
            st.rerun()

        except PasswordProtectedPDFError as e:
            # PDF is encrypted
            if "Invalid password" in str(e):
                # Wrong password - stay in password mode
                st.session_state.pdf_password_error = (
                    "❌ Nieprawidłowe hasło. Spróbuj ponownie."
                )
                st.rerun()
            else:
                # First encounter - enter password mode
                uploaded_file.seek(0)
                st.session_state.encrypted_pdf_buffer = BytesIO(uploaded_file.read())
                st.session_state.encrypted_pdf_filename = uploaded_file.name
                st.session_state.pdf_password_error = None
                st.info("ℹ️ PDF wymaga hasła. Wpisz hasło poniżej.")
                st.rerun()
        except UnsupportedFormatError as e:
            st.error(f"❌ Nieobsługiwany format pliku: {str(e)}")
        except CorruptedFileError as e:
            st.error(f"❌ Uszkodzony plik: {str(e)}")
        except Exception as e:
            st.error(f"❌ Błąd podczas przetwarzania: {str(e)}")
            st.exception(e)


def process_encrypted_pdf_with_password(password: str):
    """Process previously uploaded encrypted PDF with provided password"""
    if st.session_state.encrypted_pdf_buffer is None:
        st.error("❌ Brak zapisanego pliku PDF. Prześlij plik ponownie.")
        return

    # Create fake uploaded_file object
    class FakeUploadedFile:
        def __init__(self, buffer, name):
            self.buffer = buffer
            self.name = name

        def read(self):
            self.buffer.seek(0)
            return self.buffer.read()

        def seek(self, pos):
            self.buffer.seek(pos)

    fake_file = FakeUploadedFile(
        st.session_state.encrypted_pdf_buffer,
        st.session_state.encrypted_pdf_filename
    )

    # Process with password
    process_invoice(fake_file, password=password)


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
