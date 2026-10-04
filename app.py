from google import genai
import streamlit as st

from extractor import extract_receipt
from expense import compute_split
from prompt import WELCOME_MESSAGE

st.set_page_config(page_title="BillMate", page_icon="🧾")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


def build_whatsapp_summary(receipt, result) -> str:
    items_lines = "\n".join(
        f"• {item.name} × {item.quantity} — {result['currency']} {item.line_total}"
        for item in receipt.items
    )
    return (
        f"Merchant: {receipt.merchant or 'Receipt'}\n"
        f"Total: {result['currency']} {result['total']}\n"
        f"Split {result['num_people']} ways:\n"
        f"→ {result['currency']} {result['per_person']} each\n\n"
        f"Items:\n{items_lines}"
    )


# ---------------------------------------------------------------------------
# Onboarding
# ---------------------------------------------------------------------------

if "onboarded" not in st.session_state:
    st.title("🧾 BillMate")
    st.caption("Snap a receipt. Split the bill. Share it.")
    with st.form("onboarding_form"):
        name = st.text_input("Your name")
        whatsapp_number = st.text_input(
            "WhatsApp number (with country code)",
            placeholder="+91XXXXXXXXXX",
        )
        submitted = st.form_submit_button("Let's go 🚀")
    if submitted:
        if not name.strip() or not whatsapp_number.strip():
            st.warning("Please fill in both fields.")
        else:
            st.session_state.name = name.strip()
            st.session_state.whatsapp_number = whatsapp_number.strip()
            st.session_state.onboarded = True
            st.rerun()
    st.stop()


# ---------------------------------------------------------------------------
# Main screen
# ---------------------------------------------------------------------------

st.title("🧾 BillMate")
st.caption(f"Logged in as {st.session_state.name}")
st.info(WELCOME_MESSAGE.format(name=st.session_state.name))

uploaded = st.file_uploader("Upload a receipt", type=["jpg", "jpeg", "png"])

if uploaded is not None:
    if st.button("🔍 Extract receipt", type="primary"):
        with st.spinner("Reading the receipt..."):
            image_bytes = uploaded.getvalue()
            receipt = extract_receipt(image_bytes, uploaded.type)
        st.session_state.receipt = receipt


# ---------------------------------------------------------------------------
# Receipt display + split
# ---------------------------------------------------------------------------

if "receipt" in st.session_state:
    receipt = st.session_state.receipt

    if receipt.status == "unreadable":
        st.error("That image was too blurry to read. Please re-upload a clearer photo.")
        st.stop()

    if receipt.status == "partial":
        st.warning(
            "I could read most of this, but some fields were unclear. "
            "Please check the values below."
        )

    st.subheader(receipt.merchant or "Receipt")
    st.caption(f"Currency: {receipt.currency}")

    st.markdown("**Items**")
    items_data = [
        {
            "Item": item.name,
            "Qty": item.quantity,
            "Unit": item.unit_price,
            "Total": item.line_total,
        }
        for item in receipt.items
    ]
    st.dataframe(items_data, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Subtotal", receipt.subtotal if receipt.subtotal is not None else "—")
    col2.metric("Tax", receipt.tax if receipt.tax is not None else "—")
    col3.metric("Total", f"{receipt.currency} {receipt.total}")

    # Split section
    st.divider()
    st.markdown("### Split the bill")
    num_people = st.number_input(
        "Split between how many people?",
        min_value=1,
        value=2,
        step=1,
    )

    result = compute_split(receipt, num_people)

    st.metric(
        "Each person pays",
        f"{result['currency']} {result['per_person']}",
    )

    # Share section
    st.divider()
    st.markdown("### Share the split")
    summary = build_whatsapp_summary(receipt, result)
    st.code(summary, language=None)
    st.caption("Copy the text above into your WhatsApp group.")