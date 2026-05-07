import os
import time
import pandas as pd
import plotly.graph_objects as go
from pytrends.request import TrendReq


CSV_FILENAME = "kendrick_vs_cole_dma_4wk.csv"
HTML_FILENAME = "kendrick_vs_cole_map.html"

# DMA and Album Data 
dmas = {
    "Los Angeles": {"geo": "US-CA-803", "pop": 13_201_000, "lat": 34.05, "lon": -118.24},
    "Raleigh-Durham": {"geo": "US-NC-560", "pop": 2_079_000, "lat": 35.78, "lon": -78.64},
    "New York": {"geo": "US-NY-501", "pop": 19_979_000, "lat": 40.71, "lon": -74.01},
    "Atlanta": {"geo": "US-GA-524", "pop": 6_145_000, "lat": 33.75, "lon": -84.39},
    "Chicago": {"geo": "US-IL-602", "pop": 9_459_000, "lat": 41.88, "lon": -87.63},
    "Houston": {"geo": "US-TX-618", "pop": 7_123_000, "lat": 29.76, "lon": -95.37},
    "Miami-Ft. Lauderdale": {"geo": "US-FL-528", "pop": 6_139_000, "lat": 25.76, "lon": -80.19},
    "Seattle-Tacoma": {"geo": "US-WA-819", "pop": 4_019_000, "lat": 47.61, "lon": -122.33},
}

albums = {
    "Kendrick Lamar GNX": {
        "keyword": "GNX + Kendrick GNX + Kendrick Lamar GNX",
        "timeframe": "2024-11-22 2024-12-20",
    },
    "J Cole Fall Off": {
        "keyword": "The Fall Off + J Cole Fall Off + J. Cole Fall Off",
        "timeframe": "2026-02-06 2026-03-06",
    },
}



def generate_map(df):
    print("🎨 Generating High-Contrast Interactive Map...")
    fig = go.Figure()

    # --- 1. KENDRICK MAP (Visible by default) ---
    fig.add_trace(go.Scattergeo(
        lat=df["lat"], lon=df["lon"], text=df["DMA"],
        customdata=list(zip(df["population"].apply(lambda x: f"{x/1e6:.1f}M"), df["kendrick_per_1m"])),
        marker=dict(
            size=df["kendrick_avg_interest"].fillna(0) / 2 + 12,
            color=df["kendrick_avg_interest"],
            colorscale="YlOrRd", 
            cmin=20, cmax=80, # Forces bold reds even at lower values
            colorbar=dict(title="Kendrick Interest", x=1.02),
            line=dict(width=1.5, color="white")
        ),
        hovertemplate="<b>%{text}</b><br>Interest: %{marker.color:.1f}<br>Pop: %{customdata[0]}<br>Per 1M: %{customdata[1]:.1f}<extra></extra>",
        name="Kendrick — GNX", visible=True
    ))

    # 2. COLE MAP (Hidden)
    fig.add_trace(go.Scattergeo(
        lat=df["lat"], lon=df["lon"], text=df["DMA"],
        customdata=list(zip(df["population"].apply(lambda x: f"{x/1e6:.1f}M"), df["cole_per_1m"])),
        marker=dict(
            size=df["cole_avg_interest"].fillna(0) / 2 + 12,
            color=df["cole_avg_interest"],
            colorscale="Blues", 
            cmin=20, cmax=80, # Forces deep blues
            colorbar=dict(title="Cole Interest", x=1.02),
            line=dict(width=1.5, color="white")
        ),
        hovertemplate="<b>%{text}</b><br>Interest: %{marker.color:.1f}<br>Pop: %{customdata[0]}<br>Per 1M: %{customdata[1]:.1f}<extra></extra>",
        name="J. Cole — The Fall-Off", visible=False
    ))

    # 3. DIFFERENCE MAP (Hidden) 
    fig.add_trace(go.Scattergeo(
        lat=df["lat"], lon=df["lon"], text=df["DMA"],
        customdata=list(zip(df["kendrick_avg_interest"].fillna(0), df["cole_avg_interest"].fillna(0), df["leader"])),
        marker=dict(
            size=df["diff_per_1m"].fillna(0).abs() * 5 + 18,
            color=df["diff_per_1m"],
            colorscale="RdBu_r", 
            cmid=0, cmin=-15, cmax=15, # Tight range for Raleigh-Durham type differences
            colorbar=dict(title="Diff (K-C)", x=1.02),
            line=dict(width=1.8, color="white")
        ),
        hovertemplate="<b>%{text}</b><br>Kendrick: %{customdata[0]:.1f} · Cole: %{customdata[1]:.1f}<br>Diff per 1M: %{marker.color:+.1f}<br>Leader: %{customdata[2]}<extra></extra>",
        name="Difference", visible=False
    ))

    # DROPDOWN LOGIC 
    fig.update_layout(
        updatemenus=[dict(
            type="dropdown", direction="down", x=0.01, y=1.12, showactive=True,
            buttons=[
                dict(label="View: Kendrick — GNX", method="update", 
                     args=[{"visible": [True, False, False]}, {"title.text": "Kendrick Lamar — GNX Search Interest"}]),
                dict(label="View: J. Cole — The Fall-Off", method="update", 
                     args=[{"visible": [False, True, False]}, {"title.text": "J. Cole — The Fall-Off Search Interest"}]),
                dict(label="View: Head-to-Head Difference", method="update", 
                     args=[{"visible": [False, False, True]}, {"title.text": "Who Leads Each Market? (Interest per 1M Pop)"}]),
            ]
        )],
        title=dict(text="Kendrick Lamar — GNX Search Interest", x=0.5, y=0.95),
        geo=dict(
            scope="usa", projection_type="albers usa", 
            showland=True, landcolor="#f4f4f4", subunitcolor="white"
        ),
        margin=dict(l=0, r=0, t=80, b=0),
        height=750
    )

    fig.show()
    fig.write_html("kendrick_vs_cole_comparison.html")
    print(f"✨ Interactive map saved to {HTML_FILENAME}")

# main
if __name__ == "__main__":
    # If the CSV exists, we load it. If not, we run the scraper.
    # if os.path.exists(CSV_FILENAME):
    #     print(f"📂 Found existing data: {CSV_FILENAME}. Loading...")
    #     df_trends = pd.read_csv(CSV_FILENAME)
        
    #     # TIP: To FORCE a rerun even if the file exists, 
    #     # just uncomment the line below:
    #     # df_trends = fetch_trends_data() 
    # else:
    #     df_trends = fetch_trends_data()

    # Always generate the graph from whatever data we have
    df_trends = pd.read_csv("kendrick_vs_cole_dma_4wk.csv")
    generate_map(df_trends)