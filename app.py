import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt

# ----------- PAGE CONFIG -----------------
st.set_page_config(page_title="Dubai Real Estate Dashboard", layout="wide")

# ----------- LOAD DATA -------------------
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

# ----------- SIDEBAR FILTERS --------------
st.sidebar.header("Filter Listings")

areas = df['area_name'].dropna().unique()
types = df['type'].dropna().unique()
furnishings = df['furnishing'].dropna().unique()

selected_area = st.sidebar.multiselect("Area", options=areas, default=list(areas)[:5])
selected_type = st.sidebar.multiselect("Type", options=types, default=list(types))
selected_furnishing = st.sidebar.multiselect("Furnishing", options=furnishings, default=list(furnishings))

min_price, max_price = int(df["price"].min()), int(df["price"].max())
price_range = st.sidebar.slider("Price Range (AED)", min_price, max_price, (min_price, max_price))

beds = sorted(df['beds'].dropna().unique())
selected_beds = st.sidebar.multiselect("Bedrooms", options=beds, default=beds)

filtered_df = df[
    (df['area_name'].isin(selected_area)) &
    (df['type'].isin(selected_type)) &
    (df['furnishing'].isin(selected_furnishing)) &
    (df['price'] >= price_range[0]) &
    (df['price'] <= price_range[1]) &
    (df['beds'].isin(selected_beds))
]

# ----------- TABS FOR SECTIONS ------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🏙️ Macro Market Trends",
    "🏘️ Micro & Listing Insights",
    "📊 Correlations & Advanced",
    "📄 Full Listings Table"
])

# ----------- MACRO TRENDS -----------------
with tab1:
    st.title("Dubai Real Estate Market - Macro Analysis")
    st.markdown("A comprehensive view of Dubai's real estate trends, pricing, yields, hotspots, and market composition.")

    st.subheader("1. Price Distribution")
    st.write("This histogram shows the distribution of property prices in AED, giving a sense of market skewness and popular price bands.")
    fig = px.histogram(filtered_df, x="price", nbins=40, title="Price Distribution")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("2. Rental Yield Distribution")
    st.write("See which properties offer the highest rental returns, useful for investors evaluating yield versus price.")
    fig = px.histogram(filtered_df, x="rental_yield", nbins=30, title="Rental Yield (%)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("3. Days on Market")
    st.write("A quick look at how long listings typically remain available. Faster turnover may indicate strong demand.")
    fig = px.histogram(filtered_df, x="days_on_market", nbins=30, title="Days on Market")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("4. Listings by Area")
    st.write("Areas with the highest volume of listings, indicating popular or highly transacted regions.")
    area_counts = filtered_df['area_name'].value_counts().head(20)
    fig = px.bar(area_counts, x=area_counts.index, y=area_counts.values, labels={'x':'Area', 'y':'Count'})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("5. Average Price by Area")
    st.write("The mean price for each area, highlighting premium vs. affordable regions in Dubai.")
    avg_price = filtered_df.groupby('area_name')['price'].mean().sort_values(ascending=False).head(20)
    fig = px.bar(avg_price, x=avg_price.index, y=avg_price.values, labels={'x':'Area', 'y':'Avg Price'})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("6. Average Rental Yield by Area")
    st.write("Shows which areas are most attractive for buy-to-let and yield-focused strategies.")
    avg_yield = filtered_df.groupby('area_name')['rental_yield'].mean().sort_values(ascending=False).head(20)
    fig = px.bar(avg_yield, x=avg_yield.index, y=avg_yield.values, labels={'x':'Area', 'y':'Avg Yield (%)'})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("7. Price Category Distribution")
    st.write("Breakdown of listings by price category for a snapshot of market segmentation.")
    fig = px.pie(filtered_df, names="price_category", title="Price Category Split", hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("8. Property Type Distribution")
    st.write("Understand the mix of apartments, villas, and other property types on the market.")
    fig = px.pie(filtered_df, names="type", title="Type of Property", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("9. Completion Status")
    st.write("Ready vs. off-plan properties for investment or end-user decisions.")
    fig = px.bar(filtered_df["completion_status"].value_counts(), text_auto=True, title="Completion Status")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("10. Furnishing Status")
    st.write("Furnished, semi-furnished, and unfurnished property mix in the Dubai market.")
    fig = px.bar(filtered_df["furnishing"].value_counts(), text_auto=True, title="Furnishing Status")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("11. Listings Map - Hotspot Areas")
    st.write("Visualize where listings are concentrated. Red spots indicate higher listing density ('hotspots').")
    map_df = filtered_df[['Latitude', 'Longitude', 'price', 'area_name', 'type']].dropna()
    st.map(map_df, latitude='Latitude', longitude='Longitude', zoom=11)

# ----------- MICRO & LISTING INSIGHTS -------------
with tab2:
    st.title("Micro Analysis & Stakeholder Insights")
    st.markdown("Drill down into micro-level trends, top properties, and detailed features for buyers, investors, and analysts.")

    st.subheader("12. Top 10 Most Expensive Listings")
    st.write("These are the highest-value properties currently available.")
    st.dataframe(filtered_df.sort_values('price', ascending=False).head(10))

    st.subheader("13. Top 10 Highest Rental Yields")
    st.write("Highest-yielding properties for rental investors.")
    st.dataframe(filtered_df.sort_values('rental_yield', ascending=False).head(10))

    st.subheader("14. Building Age vs. Rental Yield")
    st.write("Are older or newer buildings yielding better returns? Analyze the impact of building age on rental yield.")
    filtered_df['building_age'] = filtered_df['post_date'].dt.year - filtered_df['year_of_completion']
    fig = px.scatter(filtered_df, x='building_age', y='rental_yield', color='type',
                     title="Building Age vs Rental Yield", labels={'building_age':'Building Age (years)', 'rental_yield':'Yield (%)'})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("15. Price per Sqft vs. Rental Yield")
    st.write("See if higher price per sqft means higher or lower yield—a must for value investors.")
    fig = px.scatter(filtered_df, x="price_per_sqft", y="rental_yield", color='type',
                     title="Price per Sqft vs Rental Yield", labels={'price_per_sqft':'Price/Sqft', 'rental_yield':'Yield (%)'})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("16. Mortgage Score by Price Category")
    st.write("Distribution of mortgage scores, segmented by price category (higher is better for financing).")
    fig = px.box(filtered_df, x="price_category", y="mortgage_score", points="all",
                 title="Mortgage Score by Price Category")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("17. Investment Grade by Area")
    st.write("Which areas offer higher investment-grade properties? Useful for risk/return profiling.")
    grade_area = filtered_df.groupby('area_name')['investment_grade'].value_counts().unstack(fill_value=0)
    st.bar_chart(grade_area.head(20))

    st.subheader("18. Parking Spaces vs. Price")
    st.write("Does extra parking space mean higher prices?")
    fig = px.scatter(filtered_df, x="total_parking_spaces", y="price", color='type',
                     title="Parking Spaces vs. Price")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("19. Elevators vs. Price (Apartments Only)")
    st.write("Are apartments with more elevators commanding higher prices?")
    apt_df = filtered_df[filtered_df['type'] == "Apartment"].copy()
    fig = px.scatter(apt_df, x="elevators", y="price", title="Elevators vs Price (Apartments)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("20. Property Type vs. Days on Market")
    st.write("Are some property types selling faster?")
    fig = px.box(filtered_df, x="type", y="days_on_market", points="outliers", title="Property Type vs. Days on Market")
    st.plotly_chart(fig, use_container_width=True)

# ----------- CORRELATIONS & ADVANCED ---------------
with tab3:
    st.title("Correlations & Advanced Analytics")
    st.markdown("Uncover relationships and advanced patterns between key variables.")

    st.subheader("21. Correlation Heatmap")
    st.write("Find out which features are strongly linked (correlated) for deeper statistical insights.")
    corr = filtered_df.select_dtypes(include=[np.number]).corr()
    fig, ax = plt.subplots(figsize=(10,7))
    im = ax.imshow(corr, cmap="coolwarm", aspect="auto")
    ax.set_xticks(np.arange(len(corr.columns)))
    ax.set_yticks(np.arange(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax.set_yticklabels(corr.columns)
    plt.colorbar(im, ax=ax)
    st.pyplot(fig)

    st.subheader("22. Average Rent by Area")
    st.write("See which areas command the highest average annual rent.")
    rent_area = filtered_df.groupby("area_name")["average_rent"].mean().sort_values(ascending=False).head(20)
    fig = px.bar(rent_area, x=rent_area.index, y=rent_area.values, labels={'x':'Area', 'y':'Avg Rent'})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("23. Year of Completion Trend")
    st.write("Track how new vs. old buildings have trended in Dubai market listings over the years.")
    year_counts = filtered_df['year_of_completion'].dropna().astype(int).value_counts().sort_index()
    fig = px.line(x=year_counts.index, y=year_counts.values, labels={'x':'Year of Completion', 'y':'No. of Properties'})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("24. Hotspot Flag Distribution")
    st.write("How many listings are in market hotspot areas?")
    fig = px.pie(filtered_df, names="hotspot_flag", title="Hotspot Listings (1=Hotspot, 0=Not)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("25. Listings by Purpose (Sale vs Rent)")
    st.write("Current purpose mix of available properties in Dubai market.")
    fig = px.pie(filtered_df, names="purpose", title="Listing Purpose")
    st.plotly_chart(fig, use_container_width=True)

# ----------- FULL TABLE VIEW -----------------------
with tab4:
    st.title("All Listings (Filtered)")
    st.write("Below is the full table of filtered listings. Use the filters on the sidebar to customize your view. You can scroll, search, and download the results.")
    st.dataframe(filtered_df)

    st.download_button("Download filtered data as CSV", data=filtered_df.to_csv(index=False), file_name="filtered_DRED.csv")

# ----------- END OF DASHBOARD ----------------------
st.sidebar.markdown("---")
st.sidebar.info("**Made with ❤️ for Dubai Real Estate Analytics**")
