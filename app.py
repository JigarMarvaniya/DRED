import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -------------------- CONFIG --------------------
st.set_page_config(
    page_title="Dubai Real Estate Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏙️",
)

# -------------------- LOAD DATA -----------------
@st.cache_data
def load_data():
    df = pd.read_excel("DRED.xlsx", sheet_name=0)
    df["post_date"] = pd.to_datetime(df["post_date"])
    df["year_of_completion"] = pd.to_numeric(df["year_of_completion"], errors='coerce')
    df["price"] = pd.to_numeric(df["price"], errors='coerce')
    df["average_rent"] = pd.to_numeric(df["average_rent"], errors='coerce')
    df["price_per_sqft"] = pd.to_numeric(df["price_per_sqft"], errors='coerce')
    df["rental_yield"] = pd.to_numeric(df["rental_yield"], errors='coerce')
    df["days_on_market"] = pd.to_numeric(df["days_on_market"], errors='coerce')
    df["mortgage_score"] = pd.to_numeric(df["mortgage_score"], errors='coerce')
    return df

df = load_data()

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1464983953574-0892a716854b?auto=format&fit=crop&w=800&q=80",
        use_container_width=True
    )
    st.markdown("""
        <h2 style="color:#003366; font-weight:bold;">Dubai Real Estate Dashboard</h2>
        <p style="font-size: 16px;">
        Analytics & visualizations for Dubai’s property market. Use filters to explore macro & micro trends.
        </p>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.header("🔎 **Filter Data**")

    area = st.multiselect("Area", sorted(df['area_name'].dropna().unique()), default=None)
    type_ = st.multiselect("Type", sorted(df['type'].dropna().unique()), default=None)
    furnishing = st.multiselect("Furnishing", sorted(df['furnishing'].dropna().unique()), default=None)

    price_min, price_max = int(df["price"].min()), int(df["price"].max())
    price_range = st.slider("Price Range (AED)", min_value=price_min, max_value=price_max,
                            value=(price_min, price_max), step=10000)

    beds = sorted(df['beds'].dropna().unique())
    selected_beds = st.multiselect("Bedrooms", beds, default=beds)

    st.markdown("---")
    st.caption("Built by [Your Name] | Powered by Streamlit & Plotly")

# Filter logic
filtered = df.copy()
if area: filtered = filtered[filtered['area_name'].isin(area)]
if type_: filtered = filtered[filtered['type'].isin(type_)]
if furnishing: filtered = filtered[filtered['furnishing'].isin(furnishing)]
filtered = filtered[(filtered['price'] >= price_range[0]) & (filtered['price'] <= price_range[1])]
filtered = filtered[filtered['beds'].isin(selected_beds)]

# -------------------- MAIN LAYOUT --------------------
st.markdown("""
    <style>
    .main .block-container {padding-top:2rem;}
    .stTabs [role="tab"] {font-size:1.12rem; padding:0.5rem 1.2rem;}
    </style>
""", unsafe_allow_html=True)

st.title("🏙️ Dubai Real Estate Analytics Platform")
st.write(
    "A one-stop platform to visualize, filter, and analyze Dubai's real estate market at both macro and micro levels. "
    "Interact with the tabs below for insights. Data is filterable via the left panel."
)

# -------------------- TABS --------------------
tabs = st.tabs([
    "📈 Market Overview",
    "📊 Investor Insights",
    "🏡 Property Features",
    "📍 Map & Hotspots",
    "📋 Listings Table",
])

# ----------------- 1. MARKET OVERVIEW -----------------
with tabs[0]:
    st.subheader("📈 Macro Market Trends")
    st.markdown("> **How are prices and yields distributed? Where are most listings concentrated?**")

    col1, col2 = st.columns(2)
    with col1:
        st.caption("**Property Price Distribution**\n\nShows the spread of property prices across all filtered listings.")
        fig = px.histogram(filtered, x="price", nbins=40, color="price_category",
                           color_discrete_sequence=px.colors.sequential.Blues,
                           labels={'price': "Price (AED)"}, title="Price Distribution by Category")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.caption("**Rental Yield (%) Distribution**\n\nSee where yields cluster, and which price bands deliver best returns.")
        fig = px.histogram(filtered, x="rental_yield", nbins=30, color="type",
                           color_discrete_sequence=px.colors.sequential.Tealgrn,
                           labels={'rental_yield': "Rental Yield (%)"}, title="Rental Yield Distribution by Type")
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.caption("**Listings by Area**\n\nWhere are most properties being listed right now?")
        area_counts = filtered['area_name'].value_counts().head(15)
        fig = px.bar(x=area_counts.index, y=area_counts.values, labels={'x':'Area', 'y':'Listings'},
                     color=area_counts.values, color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.caption("**Average Price by Area**\n\nHighlights the premium vs. affordable regions in Dubai.")
        avg_price = filtered.groupby('area_name')['price'].mean().sort_values(ascending=False).head(15)
        fig = px.bar(x=avg_price.index, y=avg_price.values, labels={'x':'Area', 'y':'Avg Price (AED)'},
                     color=avg_price.values, color_continuous_scale='Teal')
        st.plotly_chart(fig, use_container_width=True)

    st.caption("**Price Category & Completion Status**")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(filtered, names="price_category", title="Price Categories", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.pie(filtered, names="completion_status", title="Completion Status", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

# ----------------- 2. INVESTOR INSIGHTS -----------------
with tabs[1]:
    st.subheader("📊 Investor & Financial Insights")
    st.markdown("> **Which properties offer best returns? Where are the investor hotspots?**")

    col1, col2 = st.columns(2)
    with col1:
        st.caption("**Top 10 Listings by Rental Yield**")
        top_yield = filtered.sort_values("rental_yield", ascending=False).head(10)
        st.dataframe(top_yield[['area_name', 'price', 'average_rent', 'rental_yield', 'type', 'beds', 'address']], height=300)

    with col2:
        st.caption("**Top 10 Most Expensive Listings**")
        top_price = filtered.sort_values("price", ascending=False).head(10)
        st.dataframe(top_price[['area_name', 'price', 'average_rent', 'rental_yield', 'type', 'beds', 'address']], height=300)

    st.caption("**Price per Sqft vs Rental Yield**\n\nCheck if higher cost per sqft correlates to better returns.")
    fig = px.scatter(filtered, x="price_per_sqft", y="rental_yield", color="type",
                     hover_data=["area_name", "price"],
                     title="Price per Sqft vs Rental Yield")
    st.plotly_chart(fig, use_container_width=True)

    st.caption("**Mortgage Score by Price Category**")
    fig = px.box(filtered, x="price_category", y="mortgage_score", color="price_category",
                 points="all", title="Mortgage Score by Price Category")
    st.plotly_chart(fig, use_container_width=True)

    st.caption("**Investment Grade by Area**")
    grade_area = filtered.groupby('area_name')['investment_grade'].value_counts().unstack(fill_value=0)
    st.dataframe(grade_area.style.background_gradient(cmap='Greens'), height=350)

    st.caption("**Year of Completion Trend**\n\nSee how property launches are trending.")
    year_counts = filtered['year_of_completion'].dropna().astype(int).value_counts().sort_index()
    fig = px.line(x=year_counts.index, y=year_counts.values,
                  labels={'x':'Year of Completion', 'y':'Listings'},
                  title="Trend of New Properties")
    st.plotly_chart(fig, use_container_width=True)

# ----------------- 3. PROPERTY FEATURES -----------------
with tabs[2]:
    st.subheader("🏡 Property Features & Micro Analysis")
    st.markdown("> **Drill down into the features that matter for buyers and residents.**")

    col1, col2 = st.columns(2)
    with col1:
        st.caption("**Property Type Distribution**")
        fig = px.pie(filtered, names="type", title="Type of Property", hole=0.5)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.caption("**Furnishing Status**")
        fig = px.bar(filtered["furnishing"].value_counts(), text_auto=True, title="Furnishing Status")
        st.plotly_chart(fig, use_container_width=True)

    st.caption("**Bedrooms & Bathrooms Distribution**")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(filtered, x="beds", nbins=12, color="type", title="Bedrooms Distribution")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.histogram(filtered, x="baths", nbins=12, color="type", title="Bathrooms Distribution")
        st.plotly_chart(fig, use_container_width=True)

    st.caption("**Parking Spaces vs. Price**")
    fig = px.scatter(filtered, x="total_parking_spaces", y="price", color='type',
                     title="Parking Spaces vs. Price", labels={'total_parking_spaces':'Parking Spaces'})
    st.plotly_chart(fig, use_container_width=True)

    st.caption("**Elevators vs. Price (Apartments Only)**")
    apt_df = filtered[filtered['type'] == "Apartment"]
    fig = px.scatter(apt_df, x="elevators", y="price", title="Elevators vs Price (Apartments)")
    st.plotly_chart(fig, use_container_width=True)

    st.caption("**Days on Market by Type**")
    fig = px.box(filtered, x="type", y="days_on_market", points="outliers", title="Days on Market by Type")
    st.plotly_chart(fig, use_container_width=True)

# ----------------- 4. MAP & HOTSPOTS -----------------
with tabs[3]:
    st.subheader("📍 Geographic Distribution & Hotspots")
    st.markdown("> **Where are the listings located? Explore the map and hotspot flags.**")

    st.caption("**Listings Map (Zoomable & Interactive)**")
    map_df = filtered[['Latitude', 'Longitude', 'price', 'area_name', 'type']].dropna()
    st.map(map_df, latitude='Latitude', longitude='Longitude', zoom=11)

    st.caption("**Hotspot Flag Distribution**")
    fig = px.pie(filtered, names="hotspot_flag", title="Hotspot Listings (1=Hotspot, 0=Not)")
    st.plotly_chart(fig, use_container_width=True)

# ----------------- 5. FULL LISTINGS TABLE -----------------
with tabs[4]:
    st.subheader("📋 All Filtered Listings")
    st.markdown(
        "Use the filters on the sidebar to refine this table. Download your results for further analysis."
    )
    st.dataframe(filtered, use_container_width=True)
    st.download_button("Download filtered data as CSV",
        data=filtered.to_csv(index=False), file_name="filtered_DRED.csv")

# ----------------- END -----------------
