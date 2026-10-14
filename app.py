
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from google import genai
except ImportError:
    genai = None


# PAGE CONFIGURATION
st.set_page_config(
    page_title="BizFlow AI",
    page_icon="📊",
    layout="wide",
)

# COLOURS
NAVY = "#102A43"
BLUE = "#2864E8"
ORANGE = "#FF8A35"
GREEN = "#20A878"
BG = "#F4F7FC"


# SAMPLE DATA
def sample_data():
    rows = [
        ["2026-10-01", "Sales", "Revenue", 8500],
        ["2026-10-02", "Rent", "Expense", 3200],
        ["2026-10-03", "Consulting", "Revenue", 4500],
        ["2026-10-04", "Marketing", "Expense", 850],
        ["2026-10-05", "Products", "Revenue", 6200],
        ["2026-10-06", "Transport", "Expense", 450],
        ["2026-10-07", "Sales", "Revenue", 3900],
        ["2026-10-08", "Software", "Expense", 650],
        ["2026-10-09", "Consulting", "Revenue", 7200],
        ["2026-10-10", "Utilities", "Expense", 780],
        ["2026-10-11", "Products", "Revenue", 5100],
        ["2026-10-12", "Marketing", "Expense", 1100],
        ["2026-10-13", "Sales", "Revenue", 9400],
        ["2026-10-14", "Stock", "Expense", 2300],
    ]

    frame = pd.DataFrame(
        rows,
        columns=["Date", "Category", "Type", "Amount"],
    )
    frame["Date"] = pd.to_datetime(frame["Date"])
    return frame


if "transactions" not in st.session_state:
    st.session_state.transactions = sample_data()

if "source" not in st.session_state:
    st.session_state.source = "Sample data"


# DESIGN
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
    }}

    .stApp {{
        background: {BG};
    }}

    [data-testid="stSidebar"] {{
        background: {NAVY};
    }}

    /* White sidebar navigation text */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
        color: #FFFFFF;
    }}

    /* Keep the CSV uploader light with readable dark text */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {{
        background: #FFFFFF;
        padding: 12px;
        border-radius: 10px;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploader"] * {{
        color: {NAVY} !important;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploader"] button {{
        background: {BLUE} !important;
        border: none !important;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploader"] button * {{
        color: #FFFFFF !important;
    }}

    .hero {{
        background: linear-gradient(120deg, {NAVY}, {BLUE});
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 24px;
    }}

    .hero-label {{
        color: #D8E6FF;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
    }}

    .hero-title {{
        color: #FFFFFF !important;
        font-size: 38px;
        font-weight: 800;
        margin: 12px 0;
    }}

    .hero-title span {{
        color: {ORANGE} !important;
    }}

    .hero-description {{
        color: #FFFFFF;
        font-size: 16px;
        margin-bottom: 0;
    }}

    .metric-card {{
        background: white;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #E5EAF3;
        min-height: 120px;
    }}

    .metric-label {{
        color: #667085;
        font-size: 14px;
        font-weight: 600;
    }}

    .metric-value {{
        color: {NAVY};
        font-size: 26px;
        font-weight: 800;
        margin-top: 10px;
    }}

    .metric-note {{
        color: #667085;
        font-size: 12px;
        margin-top: 6px;
    }}

    .section-title {{
        color: {NAVY};
        font-size: 22px;
        font-weight: 800;
        margin: 14px 0;
    }}

    div.stButton > button[kind="primary"] {{
        background: {BLUE};
        color: white;
        border: none;
        border-radius: 10px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# HEADER
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-label">Your business finance companion</div>
        <div class="hero-title">Your business.<span> Your flow.</span></div>
        <p class="hero-description">
            Understand your numbers, track your performance,
            and make smarter decisions with BizFlow AI.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# SIDEBAR
st.sidebar.title("BizFlow AI")
st.sidebar.caption("Your finances, made clearer.")

page = st.sidebar.radio(
    "NAVIGATION",
    ["Overview", "Transactions", "AI Insights"],
)

st.sidebar.divider()
st.sidebar.markdown("### Data source")

uploaded_file = st.sidebar.file_uploader(
    "Upload financial CSV",
    type=["csv"],
    help="Your CSV must contain Date, Category, Type and Amount columns.",
)

if uploaded_file is not None:
    try:
        upload_df = pd.read_csv(uploaded_file)
        required = ["Date", "Category", "Type", "Amount"]

        if not all(column in upload_df.columns for column in required):
            st.sidebar.error(
                "Required columns: Date, Category, Type, Amount."
            )
        else:
            upload_df = upload_df[required].copy()
            upload_df["Date"] = pd.to_datetime(
                upload_df["Date"], errors="coerce"
            )
            upload_df["Amount"] = pd.to_numeric(
                upload_df["Amount"], errors="coerce"
            )
            upload_df["Type"] = (
                upload_df["Type"].astype(str).str.strip().str.title()
            )
            upload_df = upload_df.dropna(
                subset=["Date", "Category", "Type", "Amount"]
            )
            upload_df = upload_df[
                upload_df["Type"].isin(["Revenue", "Expense"])
                & (upload_df["Amount"] >= 0)
            ]

            if not upload_df.empty:
                st.session_state.transactions = upload_df
                st.session_state.source = uploaded_file.name
                st.sidebar.success("CSV uploaded successfully.")
            else:
                st.sidebar.error("No valid transactions were found.")

    except Exception as error:
        st.sidebar.error("Unable to read this CSV file.")
        st.sidebar.caption(str(error))

if st.sidebar.button("Reset to sample data"):
    st.session_state.transactions = sample_data()
    st.session_state.source = "Sample data"
    st.rerun()

st.sidebar.caption("Current source: " + st.session_state.source)


# DATA PREPARATION
df = st.session_state.transactions.copy()
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df = df.dropna(subset=["Date", "Category", "Type", "Amount"])
df = df[df["Type"].isin(["Revenue", "Expense"])]

st.markdown("### Your financial overview")

if not df.empty:
    first_day = df["Date"].min().date()
    last_day = df["Date"].max().date()

    date_col, category_col, type_col = st.columns([1.4, 1, 1])

    with date_col:
        date_range = st.date_input(
            "Date range",
            value=(first_day, last_day),
            min_value=first_day,
            max_value=last_day,
        )

    with category_col:
        all_categories = sorted(df["Category"].astype(str).unique())
        chosen_categories = st.multiselect(
            "Categories",
            all_categories,
            default=all_categories,
        )

    with type_col:
        chosen_types = st.multiselect(
            "Transaction type",
            ["Revenue", "Expense"],
            default=["Revenue", "Expense"],
        )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = first_day, last_day

    filtered = df[
        (df["Date"].dt.date >= start_date)
        & (df["Date"].dt.date <= end_date)
        & (df["Category"].isin(chosen_categories))
        & (df["Type"].isin(chosen_types))
    ].copy()
else:
    filtered = df.copy()


# FINANCIAL CALCULATIONS
revenue = filtered.loc[
    filtered["Type"] == "Revenue", "Amount"
].sum()

expenses = filtered.loc[
    filtered["Type"] == "Expense", "Amount"
].sum()

net_cash_flow = revenue - expenses
margin = (net_cash_flow / revenue * 100) if revenue else 0


def money(amount):
    return "R{:,.2f}".format(amount)


def show_metric(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# OVERVIEW
if page == "Overview":
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        show_metric("Total revenue", money(revenue), "Recorded money received")

    with c2:
        show_metric("Total expenses", money(expenses), "Recorded money spent")

    with c3:
        show_metric("Net cash flow", money(net_cash_flow), "Revenue minus expenses")

    with c4:
        show_metric("Net margin", "{:.1f}%".format(margin), "Net cash flow / revenue")

    st.write("")
    st.markdown(
        '<div class="section-title">Revenue and expenses over time</div>',
        unsafe_allow_html=True,
    )

    if not filtered.empty:
        daily = (
            filtered.groupby([pd.Grouper(key="Date", freq="D"), "Type"])
            ["Amount"].sum().reset_index()
        )

        trend = px.line(
            daily,
            x="Date",
            y="Amount",
            color="Type",
            markers=True,
            color_discrete_map={
                "Revenue": GREEN,
                "Expense": ORANGE,
            },
            labels={"Amount": "Amount (R)"},
        )
        trend.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font_color=NAVY,
            legend_title_text="",
            hovermode="x unified",
        )
        trend.update_yaxes(tickprefix="R", gridcolor="#E9EEF5")
        st.plotly_chart(trend, use_container_width=True)
    else:
        st.info("No transactions match your filters.")

    left, right = st.columns(2)

    with left:
        st.markdown(
            '<div class="section-title">Spending by category</div>',
            unsafe_allow_html=True,
        )
        expense_data = filtered[filtered["Type"] == "Expense"]

        if not expense_data.empty:
            by_category = (
                expense_data.groupby("Category", as_index=False)["Amount"]
                .sum()
                .sort_values("Amount", ascending=True)
            )

            bars = px.bar(
                by_category,
                x="Amount",
                y="Category",
                orientation="h",
                color="Amount",
                color_continuous_scale=["#BBD0FF", BLUE, NAVY],
                labels={"Amount": "Amount (R)"},
            )
            bars.update_layout(
                paper_bgcolor="white",
                plot_bgcolor="white",
                font_color=NAVY,
                coloraxis_showscale=False,
            )
            bars.update_xaxes(tickprefix="R", gridcolor="#E9EEF5")
            st.plotly_chart(bars, use_container_width=True)
        else:
            st.info("No expenses in this period.")

    with right:
        st.markdown(
            '<div class="section-title">Revenue versus expenses</div>',
            unsafe_allow_html=True,
        )

        comparison = pd.DataFrame({
            "Type": ["Revenue", "Expense"],
            "Amount": [revenue, expenses],
        })

        pie = px.pie(
            comparison,
            names="Type",
            values="Amount",
            hole=0.62,
            color="Type",
            color_discrete_map={
                "Revenue": GREEN,
                "Expense": ORANGE,
            },
        )
        pie.update_layout(
            paper_bgcolor="white",
            font_color=NAVY,
            legend_title_text="",
        )
        st.plotly_chart(pie, use_container_width=True)

    st.markdown(
        '<div class="section-title">Recent transactions</div>',
        unsafe_allow_html=True,
    )

    recent = filtered.sort_values("Date", ascending=False).head(10).copy()
    recent["Date"] = recent["Date"].dt.strftime("%d %b %Y")
    recent["Amount"] = recent["Amount"].map(money)
    st.dataframe(recent, use_container_width=True, hide_index=True)

    st.caption(
        "This dashboard uses recorded transactions only. Net cash flow is "
        "not necessarily accounting profit."
    )


# TRANSACTIONS
elif page == "Transactions":
    st.markdown(
        '<div class="section-title">Add a transaction</div>',
        unsafe_allow_html=True,
    )

    with st.form("add_transaction", clear_on_submit=True):
        transaction_date = st.date_input("Date", value=date.today())
        category = st.text_input(
            "Category",
            placeholder="e.g. Sales, Rent, Transport",
        )
        transaction_type = st.selectbox(
            "Type",
            ["Revenue", "Expense"],
        )
        amount = st.number_input(
            "Amount (R)",
            min_value=0.01,
            value=100.0,
            step=10.0,
        )

        submitted = st.form_submit_button(
            "Add transaction",
            type="primary",
        )

        if submitted:
            if not category.strip():
                st.error("Please enter a category.")
            else:
                new_row = pd.DataFrame([{
                    "Date": pd.to_datetime(transaction_date),
                    "Category": category.strip().title(),
                    "Type": transaction_type,
                    "Amount": float(amount),
                }])

                st.session_state.transactions = pd.concat(
                    [st.session_state.transactions, new_row],
                    ignore_index=True,
                )
                st.session_state.source = "Session transactions"
                st.success("Transaction added.")
                st.rerun()

    st.markdown(
        '<div class="section-title">All transactions</div>',
        unsafe_allow_html=True,
    )

    table = st.session_state.transactions.copy()
    table["Date"] = pd.to_datetime(table["Date"]).dt.strftime("%d %b %Y")
    table["Amount"] = table["Amount"].map(money)
    st.dataframe(table, use_container_width=True, hide_index=True)

    original = st.session_state.transactions.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download transactions as CSV",
        data=original,
        file_name="bizflow_transactions.csv",
        mime="text/csv",
    )

    st.caption(
        "Transactions entered manually are held in session memory. "
        "Download a CSV to keep a copy."
    )


# AI INSIGHTS
elif page == "AI Insights":
    st.markdown(
        '<div class="section-title">Your AI financial assistant</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Ask Gemini to interpret your financial data and identify "
        "patterns, risks and opportunities."
    )

    api_key = st.text_input(
        "Gemini API key",
        type="password",
        help="Keep your API key private. Never commit it to GitHub.",
    )

    question = st.text_area(
        "What would you like to understand?",
        value=(
            "Summarise my revenue and expenses, identify the biggest "
            "expense categories, and suggest three practical ways to "
            "improve cash flow."
        ),
    )

    if st.button("Generate AI insights", type="primary"):
        if not api_key:
            st.warning("Enter your Gemini API key.")
        elif genai is None:
            st.error("Install the Gemini package using: pip install google-genai")
        elif filtered.empty:
            st.warning("There are no transactions to analyse.")
        else:
            with st.spinner("Analysing your data..."):
                try:
                    client = genai.Client(api_key=api_key)

                    summary = (
                        filtered.groupby(["Type", "Category"])["Amount"]
                        .sum()
                        .reset_index()
                        .to_string(index=False)
                    )

                    prompt = f"""
                    You are BizFlow AI, a small-business financial analysis
                    assistant.

                    Revenue: {money(revenue)}
                    Expenses: {money(expenses)}
                    Net cash flow: {money(net_cash_flow)}
                    Net margin: {margin:.1f}%

                    Category summary:
                    {summary}

                    User question:
                    {question}

                    Give practical insights in simple language.
                    Distinguish facts from assumptions.
                    Do not invent missing data. Do not describe net cash
                    flow as accounting profit. This is general analysis,
                    not professional financial advice.
                    """

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                    )

                    st.markdown("### Your insights")
                    st.markdown(response.text or "No response was returned.")

                except Exception as error:
                    st.error(
                        "Gemini could not generate insights. Check your "
                        "API key, internet connection and model access."
                    )
                    st.caption(str(error))

    st.markdown(
        '<div class="section-title">Financial snapshot</div>',
        unsafe_allow_html=True,
    )
    a, b, c = st.columns(3)

    with a:
        st.metric("Revenue", money(revenue))

    with b:
        st.metric("Expenses", money(expenses))

    with c:
        st.metric("Net cash flow", money(net_cash_flow))

    st.caption(
        "AI-generated insights may be inaccurate. Verify information "
        "before making financial decisions. Avoid uploading sensitive data."
    )

