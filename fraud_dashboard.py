import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Healthcare Fraud Detection Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Poppins', sans-serif;
}

/* MAIN BACKGROUND */
.main {
    background-color: #f5f5f7;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #722f37 !important;
}

/* SIDEBAR TEXT VISIBILITY */
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* SIDEBAR HEADERS */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label {
    font-weight: 600;
    color: #ffffff !important;
}

/* SIDEBAR INPUTS – UNIFIED STYLE */
[data-testid="stSidebar"] .stSelectbox > div,
[data-testid="stSidebar"] .stMultiselect > div,
[data-testid="stSidebar"] .stDateInput > div {
    background-color: rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
}

/* SELECTED VALUE */
[data-testid="stSidebar"] div[data-baseweb="select"] {
    background-color: rgba(255,255,255,0.15) !important;
    color: #ffffff !important;
}

/* DROPDOWN MENU */
[data-baseweb="popover"] {
    background-color: #ffffff !important;
    color: #333333 !important;
}

/* METRIC CARDS */
.metric-card {
    background: #ffffff;
    padding: 20px;
    border-radius: 12px;
    border-left: 5px solid #722f37;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

/* HEADERS */
.main-header {
    font-size: 2.6rem;
    font-weight: 700;
    text-align: center;
    color: #ffffff;
    padding: 20px;
    background: #722f37;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.sub-header {
    font-size: 1.6rem;
    font-weight: 600;
    color: #722f37;
    border-bottom: 3px solid #722f37;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

/* PLOTLY BACKGROUND FIX - CHANGED TO LIGHT GREY */
.js-plotly-plot,
.plot-container {
    background-color: #e0e0e0 !important; 
    border-radius: 12px;
    padding: 15px;
    border: 1px solid #e0e0e0;
}

/* NAVIGATION TABS STYLING */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background-color: #f0f0f0;
    border-radius: 8px 8px 0 0;
    padding: 10px 20px;
    font-weight: 500;
    color: #722f37;
    border: 1px solid #e0e0e0;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: #333333 !important;
    color: #ffffff !important;
    font-weight: 600;
}

/* GRAPH INSIGHTS CONTAINER */
.graph-insights {
    background-color: #f8f9fa;
    border-left: 4px solid #722f37;
    padding: 15px;
    margin-top: 10px;
    border-radius: 0 8px 8px 0;
    font-size: 0.95rem;
    color: #333333;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.graph-insights h4 {
    color: #722f37;
    margin-top: 0;
    margin-bottom: 10px;
    font-size: 1.1rem;
}

/* KEY INSIGHTS SIDEBAR HEADER */
.key-insights-header {
    font-size: 1.4rem;
    font-weight: 700;
    color: #ffffff;
    text-align: center;
    padding: 10px;
    background: rgba(255,255,255,0.1);
    border-radius: 8px;
    margin-bottom: 20px;
    border: 2px solid rgba(255,255,255,0.2);
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    # Load the CSV file
    df = pd.read_csv('healthcare_fraud_claims_clean.csv')
    
    # Convert date columns with dayfirst=True for DD/MM/YYYY format
    df['AttendingDate'] = pd.to_datetime(df['AttendingDate'], dayfirst=True, errors='coerce')
    df['ClaimEndDate'] = pd.to_datetime(df['ClaimEndDate'], dayfirst=True, errors='coerce')
    
    # Calculate claim duration (using the now-corrected dates)
    df['ClaimDuration'] = (df['ClaimEndDate'] - df['AttendingDate']).dt.days + 1
    
    # Convert Gender to categorical
    df['Gender'] = df['Gender'].map({1: 'Male', 2: 'Female'})
    
    # Convert Race to categorical (simplified)
    df['Race'] = df['Race'].map({1: 'White', 2: 'Black', 3: 'Asian', 4: 'Other', 5: 'Other'})
    
    # Process ChronicConditionList to extract individual conditions
    all_conditions = []
    for condition_list in df['ChronicConditionList'].dropna():
        conditions = condition_list.split(',')
        all_conditions.extend([cond.strip() for cond in conditions])
    
    return df, all_conditions

def add_graph_insights(title, insights):
    """Helper function to add insights below graphs"""
    st.markdown(f"""
    <div class="graph-insights">
        <h4>{title}</h4>
        {insights}
    </div>
    """, unsafe_allow_html=True)

# Create dashboard
def main():
    # Header with updated styling
    st.markdown('<h1 class="main-header">Healthcare Fraud Detection Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    df, all_conditions = load_data()
    
    # Sidebar filters
    with st.sidebar:
        st.markdown('<div class="key-insights-header">Filter Controls</div>', unsafe_allow_html=True)

        # Date range filter
        min_date = df['AttendingDate'].min()
        max_date = df['AttendingDate'].max()
        
        date_range = st.date_input(
            "Select Date Range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            help="Filter claims by attending date"
        )
        
        if len(date_range) == 2:
            start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            df_filtered = df[(df['AttendingDate'] >= start_date) & (df['AttendingDate'] <= end_date)]
        else:
            df_filtered = df
        
        # Provider filter
        all_providers = ['All Providers'] + sorted(df_filtered['Provider'].unique().tolist())
        selected_provider = st.selectbox(
            "Select Provider:",
            all_providers,
            help="Choose a specific provider or view all"
        )
        
        if selected_provider != 'All Providers':
            df_filtered = df_filtered[df_filtered['Provider'] == selected_provider]
        
        # Fraud status filter
        fraud_status = st.multiselect(
            "Filter by Fraud Status:",
            options=['All Claims', 'Potential Fraud', 'No Fraud'],
            default=['Potential Fraud', 'No Fraud']
        )
        
        if 'All Claims' not in fraud_status:
            fraud_mapping = {'Potential Fraud': 'Yes', 'No Fraud': 'No'}
            selected_status = [fraud_mapping[status] for status in fraud_status if status in fraud_mapping]
            df_filtered = df_filtered[df_filtered['PotentialFraud'].isin(selected_status)]
        
        # Claim type filter
        claim_types = st.multiselect(
            "Filter by Claim Type:",
            options=df_filtered['ClaimType'].unique().tolist(),
            default=df_filtered['ClaimType'].unique().tolist(),
            help="Select one or more claim types"
        )
        
        if claim_types:
            df_filtered = df_filtered[df_filtered['ClaimType'].isin(claim_types)]
        
        st.markdown("---")
        st.markdown("""
        <div style='padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px; margin-top: 20px;'>
            <p style='color: rgba(255,255,255,0.9); font-size: 0.85rem;'>
                <strong>Data Summary:</strong><br>
                • Total Claims: {:,}<br>
                • Date Range: {} to {}
            </p>
            <p style='color: rgba(255,255,255,0.9); font-size: 0.85rem;'><strong>Data Source:</strong> <a href='https://data.mendeley.com/datasets/gsn2hyty37/1' target='_blank'>Mendeley Data - Healthcare Provider Fraud Detection Dataset</a></p>
            <p style='color: rgba(255,255,255,0.9); font-size: 0.85rem;'>Dashboard designed for Health Informatics - Fraud Detection Analysis | Last updated: March 2024</p>
        </div>
        """.format(len(df_filtered), df_filtered['AttendingDate'].min().strftime('%Y-%m-%d'), 
                  df_filtered['AttendingDate'].max().strftime('%Y-%m-%d')), unsafe_allow_html=True)
    
    # Main content area
    # Top metrics with custom cards
    st.markdown('<h2 class="sub-header">Key Performance Indicators</h2>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_claims = len(df_filtered)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Total Claims</div>
            <div style="font-size: 2rem; font-weight: 700; color: #2c3e50;">{total_claims:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        fraud_count = len(df_filtered[df_filtered['PotentialFraud'] == 'Yes'])
        fraud_percentage = (fraud_count / total_claims * 100) if total_claims > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Fraud Cases</div>
            <div style="font-size: 2rem; font-weight: 700; color: #e74c3c;">{fraud_count:,}</div>
            <div style="font-size: 0.9rem; color: #e74c3c;">({fraud_percentage:.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_claim_amount = df_filtered['InscClaimAmtReimbursed'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Avg Claim Amount</div>
            <div style="font-size: 2rem; font-weight: 700; color: #2c3e50;">${avg_claim_amount:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_length_of_stay = df_filtered['LengthOfStay'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Avg Length of Stay</div>
            <div style="font-size: 2rem; font-weight: 700; color: #2c3e50;">{avg_length_of_stay:.1f} days</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content tabs 
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview Dashboard", 
        "Financial Analysis", 
        "Provider Insights", 
        "Temporal Trends", 
        "Medical Analysis"
    ])
    
    with tab1:
        st.markdown('<h2 class="sub-header">Comprehensive Data Overview</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Fraud distribution pie chart
            fraud_dist = df_filtered['PotentialFraud'].value_counts()
            colors = ['#e74c3c' if x == 'Yes' else '#2ecc71' for x in fraud_dist.index]
            
            fig1 = go.Figure(data=[go.Pie(
                labels=['Potential Fraud' if x == 'Yes' else 'No Fraud' for x in fraud_dist.index],
                values=fraud_dist.values,
                hole=0.3,
                marker_colors=colors,
                textinfo='percent+label',
                textfont=dict(family='Poppins', size=14)
            )])
            fig1.update_layout(
                title=dict(
                    text='Fraud Distribution Analysis',
                    font=dict(family='Poppins', size=20, color='#2c3e50')
                ),
                font_color='#2c3e50',
                showlegend=True,
                height=400,
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='#f8f9fa'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Add insights for graph 1
            add_graph_insights(
                "Fraud Distribution Insights",
                "• Fraud cases represent {:.1f}% of total claims<br>• {} out of {} claims flagged as potential fraud<br>• This ratio helps assess overall fraud risk level".format(
                    fraud_percentage, fraud_count, total_claims
                )
            )
        
        with col2:
            # Claim type distribution 
            claim_dist = df_filtered['ClaimType'].value_counts()
            fig2 = px.bar(
                x=claim_dist.index,
                y=claim_dist.values,
                title="Claim Type Distribution",
                labels={'x': 'Claim Type', 'y': 'Number of Claims'},
                color=claim_dist.values,
                color_continuous_scale=['#f8d7da', '#dc3545', '#722f37']
            )
            fig2.update_layout(
                font_family="Poppins",
                title_font_size=20,
                title_font_color="#2c3e50",
                showlegend=False,
                height=400,
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='#f8f9fa'
            )
            fig2.update_xaxes(tickangle=45)
            st.plotly_chart(fig2, use_container_width=True)
            
            # Add insights for graph 2
            top_claim_type = claim_dist.index[0]
            top_claim_count = claim_dist.iloc[0]
            add_graph_insights(
                "Claim Type Analysis",
                f"• {top_claim_type} claims are most frequent ({top_claim_count:,})<br>• Distribution helps identify service patterns<br>• Certain claim types may have higher fraud propensity"
            )
        
        # Gender and Race distribution
        col3, col4 = st.columns(2)
        
        with col3:
            gender_dist = df_filtered['Gender'].value_counts()
            fig3 = px.pie(
                values=gender_dist.values,
                names=gender_dist.index,
                title="Gender Distribution",
                color_discrete_sequence=['#722f37', '#f8d7da']
            )
            fig3.update_layout(
                font_family="Poppins",
                title_font_size=18,
                title_font_color="#2c3e50",
                height=350,
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='#f8f9fa'
            )
            st.plotly_chart(fig3, use_container_width=True)
            
            # Add insights for graph 3
            gender_ratio = (gender_dist.get('Male', 0) / gender_dist.sum() * 100) if gender_dist.sum() > 0 else 0
            add_graph_insights(
                "Gender Distribution Insights",
                f"• Male/Female ratio: {gender_ratio:.1f}% male<br>• Gender distribution may correlate with specific conditions<br>• Helps in demographic pattern analysis"
            )
        
        with col4:
            race_dist = df_filtered['Race'].value_counts()
            fig4 = px.bar(
                x=race_dist.index,
                y=race_dist.values,
                title="Race Distribution",
                labels={'x': 'Race', 'y': 'Count'},
                color=race_dist.values,
                color_continuous_scale=['#f8d7da', '#722f37']
            )
            fig4.update_layout(
                font_family="Poppins",
                title_font_size=18,
                title_font_color="#2c3e50",
                showlegend=False,
                height=350,
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='#f8f9fa'
            )
            st.plotly_chart(fig4, use_container_width=True)
            
            # Add insights for graph 4
            dominant_race = race_dist.index[0]
            dominant_count = race_dist.iloc[0]
            add_graph_insights(
                "Race Distribution Insights",
                f"• {dominant_race} represents largest demographic group<br>• Understanding demographic patterns aids in fraud detection<br>• Helps identify potential disparities in healthcare access"
            )
    
    with tab2:
        st.markdown('<h2 class="sub-header">Financial Claims Analysis</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Graph 1: Claim Amount Distribution (Box Plot)
            fig5 = px.box(
                df_filtered,
                x='ClaimType',
                y='InscClaimAmtReimbursed',
                color='PotentialFraud',
                title="Claim Amount Distribution by Type",
                labels={'InscClaimAmtReimbursed': 'Claim Amount ($)', 'ClaimType': 'Claim Type'},
                color_discrete_map={'Yes': '#e74c3c', 'No': '#2ecc71'}
            )
            fig5.update_layout(
                font_family="Poppins",
                title_font_size=20,
                title_font_color="#2c3e50",
                height=500,
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='#f8f9fa'
            )
            fig5.update_layout(yaxis_title="Claim Amount ($)")
            st.plotly_chart(fig5, use_container_width=True)
            
            # Add insights for graph 5
            fraud_claims = df_filtered[df_filtered['PotentialFraud'] == 'Yes']
            no_fraud_claims = df_filtered[df_filtered['PotentialFraud'] == 'No']
            
            if not fraud_claims.empty and not no_fraud_claims.empty:
                avg_fraud_amount = fraud_claims['InscClaimAmtReimbursed'].mean()
                avg_no_fraud_amount = no_fraud_claims['InscClaimAmtReimbursed'].mean()
                diff_percentage = ((avg_fraud_amount - avg_no_fraud_amount) / avg_no_fraud_amount * 100) if avg_no_fraud_amount > 0 else 0
                
                add_graph_insights(
                    "Claim Amount Analysis",
                    f"• Fraud claims average ${avg_fraud_amount:,.0f} vs ${avg_no_fraud_amount:,.0f} for non-fraud<br>• Difference: {diff_percentage:+.1f}%<br>• Higher claim amounts may indicate potential fraud patterns"
                )
        
        with col2:
            # Graph 2: Average Claim Amount by Provider (Top 15)
            provider_avg = df_filtered.groupby(['Provider', 'PotentialFraud'])['InscClaimAmtReimbursed'].mean().reset_index()
            provider_avg = provider_avg.sort_values('InscClaimAmtReimbursed', ascending=False).head(15)
            
            fig6 = px.bar(
                provider_avg,
                y='Provider',
                x='InscClaimAmtReimbursed',
                color='PotentialFraud',
                title="Top 15 Providers by Avg Claim Amount",
                labels={'InscClaimAmtReimbursed': 'Average Claim Amount ($)', 'Provider': 'Provider'},
                orientation='h',
                color_discrete_map={'Yes': '#e74c3c', 'No': '#2ecc71'}
            )
            fig6.update_layout(
                font_family="Poppins",
                title_font_size=20,
                title_font_color="#2c3e50",
                yaxis={'categoryorder': 'total ascending'},
                height=500,
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='#f8f9fa'
            )
            st.plotly_chart(fig6, use_container_width=True)
            
            # Add insights for graph 6
            top_provider = provider_avg.iloc[0]['Provider'] if not provider_avg.empty else "N/A"
            top_amount = provider_avg.iloc[0]['InscClaimAmtReimbursed'] if not provider_avg.empty else 0
            add_graph_insights(
                "Provider Financial Insights",
                f"• Top provider by claim amount: {top_provider} (${top_amount:,.0f})<br>• High-value providers should be monitored closely<br>• Look for outliers in claim amounts"
            )
        
        # Graph 3: Length of Stay vs Claim Amount
        st.markdown("Inpatient Claim Analysis")
        inpatient_data = df_filtered[df_filtered['ClaimType'] == 'Inpatient']
        
        if not inpatient_data.empty:
            fig7 = px.scatter(
                inpatient_data,
                x='LengthOfStay',
                y='InscClaimAmtReimbursed',
                color='PotentialFraud',
                title="Length of Stay vs Claim Amount (Inpatient Claims)",
                labels={'LengthOfStay': 'Length of Stay (days)', 'InscClaimAmtReimbursed': 'Claim Amount ($)'},
                opacity=0.7,
                color_discrete_map={'Yes': '#e74c3c', 'No': '#2ecc71'},
                size_max=15
            )
            fig7.update_layout(
                font_family="Poppins",
                title_font_size=20,
                title_font_color="#2c3e50",
                height=500,
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='#f8f9fa'
            )
            fig7.update_traces(marker=dict(size=8))
            st.plotly_chart(fig7, use_container_width=True)
            
            # Add insights for graph 7
            correlation = inpatient_data[['LengthOfStay', 'InscClaimAmtReimbursed']].corr().iloc[0,1]
            add_graph_insights(
                "Inpatient Stay Analysis",
                f"• Correlation between stay length and claim amount: {correlation:.2f}<br>• Longer stays typically associated with higher costs<br>• Watch for unusually high costs relative to stay length"
            )
        else:
            st.info("No inpatient claims found with the current filters.")
    
    with tab3:
        st.markdown('<h2 class="sub-header">Provider Performance & Risk Assessment</h2>', unsafe_allow_html=True)
        
        # Graph 4: Inpatient vs Outpatient Ratio per Provider (Top 10)
        claim_type_by_provider = df_filtered.groupby(['Provider', 'ClaimType']).size().unstack(fill_value=0)
        claim_type_by_provider['Total'] = claim_type_by_provider.sum(axis=1)
        top_providers = claim_type_by_provider.nlargest(10, 'Total').drop('Total', axis=1)
        
        fig8 = px.bar(
            top_providers.reset_index().melt(id_vars='Provider', var_name='ClaimType', value_name='Count'),
            x='Provider',
            y='Count',
            color='ClaimType',
            title="Claim Type Distribution by Provider (Top 10)",
            barmode='stack',
            color_discrete_sequence=['#722f37', '#e74c3c', '#2ecc71']
        )
        fig8.update_layout(
            font_family="Poppins",
            title_font_size=20,
            title_font_color="#2c3e50",
            xaxis={'categoryorder': 'total descending'},
            height=500,
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='#f8f9fa'
        )
        st.plotly_chart(fig8, use_container_width=True)
        
        # Add insights for graph 8
        add_graph_insights(
            "Provider Service Mix",
            "• Understanding provider service mix helps identify specialization<br>• Providers with unusual claim type ratios may require further investigation<br>• High inpatient volumes may indicate different risk profiles"
        )
        
        # Provider risk assessment
        st.markdown("Provider Risk Assessment Matrix")
        
        # Calculate fraud indicators
        provider_stats = df_filtered.groupby('Provider').agg({
            'PotentialFraud': lambda x: (x == 'Yes').mean() * 100,
            'InscClaimAmtReimbursed': ['mean', 'sum', 'count'],
            'LengthOfStay': 'mean'
        }).round(2)
        
        provider_stats.columns = ['Fraud_Rate_%', 'Avg_Claim_$', 'Total_Claims_$', 'Claim_Count', 'Avg_LOS_days']
        provider_stats = provider_stats.sort_values('Fraud_Rate_%', ascending=False)
        
        # Apply conditional formatting to the dataframe
        def color_fraud_rate(val):
            color = '#e74c3c' if val > 30 else ('#f39c12' if val > 15 else '#2ecc71')
            return f'color: {color}; font-weight: bold;'
        
        styled_df = provider_stats.head(15).style.map(color_fraud_rate, subset=['Fraud_Rate_%'])
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=600
        )
        
        # Add insights for provider matrix
        add_graph_insights(
            "Risk Assessment Insights",
            "• High fraud rate providers (>30%): Red flag for investigation<br>• Moderate risk (15-30%): Enhanced monitoring recommended<br>• Low risk (<15%): Standard monitoring procedures"
        )
    
    with tab4:
        st.markdown('<h2 class="sub-header">Temporal Trends & Patterns</h2>', unsafe_allow_html=True)
        
        # Graph 5: Claim Volume Over Time
        claims_over_time = df_filtered.groupby(['ClaimYear', 'PotentialFraud']).size().reset_index(name='Count')
        
        fig9 = px.line(
            claims_over_time,
            x='ClaimYear',
            y='Count',
            color='PotentialFraud',
            title="Claim Volume Over Time",
            markers=True,
            color_discrete_map={'Yes': '#e74c3c', 'No': '#2ecc71'},
            line_shape='spline'
        )
        fig9.update_layout(
            font_family="Poppins",
            title_font_size=20,
            title_font_color="#2c3e50",
            xaxis_title="Year",
            yaxis_title="Number of Claims",
            height=450,
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='#f8f9fa'
        )
        st.plotly_chart(fig9, use_container_width=True)
        
        # Add insights for graph 9
        if not claims_over_time.empty:
            fraud_trend = claims_over_time[claims_over_time['PotentialFraud'] == 'Yes']
            if not fraud_trend.empty:
                latest_year = fraud_trend['ClaimYear'].max()
                latest_count = fraud_trend[fraud_trend['ClaimYear'] == latest_year]['Count'].iloc[0] if not fraud_trend[fraud_trend['ClaimYear'] == latest_year].empty else 0
                add_graph_insights(
                    "Temporal Trend Analysis",
                    f"• Latest year ({latest_year}) fraud cases: {latest_count:,}<br>• Monitor for seasonal or yearly patterns in fraud detection<br>• Increasing trends may indicate emerging fraud schemes"
                )
        
        # Monthly trends
        st.markdown("Monthly Trends Analysis")
        df_filtered['Month'] = df_filtered['AttendingDate'].dt.to_period('M').astype(str)
        monthly_trends = df_filtered.groupby(['Month', 'PotentialFraud']).agg({
            'InscClaimAmtReimbursed': 'sum',
            'ClaimID': 'count'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig10 = px.line(
                monthly_trends,
                x='Month',
                y='InscClaimAmtReimbursed',
                color='PotentialFraud',
                title="Monthly Claim Amount Trend",
                color_discrete_map={'Yes': '#e74c3c', 'No': '#2ecc71'},
                line_shape='spline'
            )
            fig10.update_layout(
                font_family="Poppins",
                title_font_size=18,
                title_font_color="#2c3e50",
                xaxis_title="Month",
                yaxis_title="Total Claim Amount ($)",
                height=400,
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='#f8f9fa'
            )
            st.plotly_chart(fig10, use_container_width=True)
            
            # Add insights for graph 10
            add_graph_insights(
                "Monthly Financial Patterns",
                "• Look for unusual spikes in claim amounts<br>• Seasonal patterns may indicate legitimate variations<br>• Sudden increases could signal coordinated fraud activity"
            )
        
        with col2:
            fig11 = px.line(
                monthly_trends,
                x='Month',
                y='ClaimID',
                color='PotentialFraud',
                title="Monthly Claim Volume Trend",
                color_discrete_map={'Yes': '#e74c3c', 'No': '#2ecc71'},
                line_shape='spline'
            )
            fig11.update_layout(
                font_family="Poppins",
                title_font_size=18,
                title_font_color="#2c3e50",
                xaxis_title="Month",
                yaxis_title="Number of Claims",
                height=400,
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='#f8f9fa'
            )
            st.plotly_chart(fig11, use_container_width=True)
            
            # Add insights for graph 11
            add_graph_insights(
                "Monthly Volume Analysis",
                "• Monitor for unusual claim volume patterns<br>• Consistent fraud volume may indicate systemic issues<br>• Volume spikes require investigation into specific providers or services"
            )
    
    with tab5:
        st.markdown('<h2 class="sub-header">Medical Conditions Analysis</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Graph: Chronic Condition Count vs Claim Amount
            fig12 = px.scatter(
                df_filtered,
                x='ChronicConditionCount',
                y='InscClaimAmtReimbursed',
                color='PotentialFraud',
                title="Chronic Condition Count vs Claim Amount",
                labels={
                    'ChronicConditionCount': 'Number of Chronic Conditions',
                    'InscClaimAmtReimbursed': 'Claim Amount ($)'
                },
                opacity=0.6,
                color_discrete_map={'Yes': '#e74c3c', 'No': '#2ecc71'},
                trendline="ols"
            )
            fig12.update_layout(
                font_family="Poppins",
                title_font_size=20,
                title_font_color="#2c3e50",
                height=500,
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='#f8f9fa'
            )
            st.plotly_chart(fig12, use_container_width=True)
            
            # Add insights for graph 12
            correlation_conditions = df_filtered[['ChronicConditionCount', 'InscClaimAmtReimbursed']].corr().iloc[0,1]
            add_graph_insights(
                "Chronic Conditions Impact",
                f"• Correlation between conditions and claim amount: {correlation_conditions:.2f}<br>• Patients with more conditions typically have higher claims<br>• Watch for claims with many conditions but low supporting documentation"
            )
        
        with col2:
            # Graph: Frequency of Chronic Conditions
            from collections import Counter
            condition_counts = Counter(all_conditions)
            top_conditions = pd.DataFrame(condition_counts.most_common(10), columns=['Condition', 'Count'])
            
            fig13 = px.bar(
                top_conditions,
                x='Count',
                y='Condition',
                title="Top 10 Chronic Conditions",
                orientation='h',
                color='Count',
                color_continuous_scale=['#f8d7da', '#722f37']
            )
            fig13.update_layout(
                font_family="Poppins",
                title_font_size=20,
                title_font_color="#2c3e50",
                yaxis={'categoryorder': 'total ascending'},
                height=500,
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='#f8f9fa'
            )
            st.plotly_chart(fig13, use_container_width=True)
            
            # Add insights for graph 13
            top_condition = top_conditions.iloc[0]['Condition'] if not top_conditions.empty else "N/A"
            top_condition_count = top_conditions.iloc[0]['Count'] if not top_conditions.empty else 0
            add_graph_insights(
                "Common Conditions Analysis",
                f"• Most common condition: {top_condition} ({top_condition_count:,} occurrences)<br>• Understanding prevalent conditions helps with resource allocation<br>• Common conditions may have established fraud patterns"
            )
        
        # Condition analysis by fraud status
        st.markdown("Condition Patterns by Fraud Status")
        
        # Extract conditions and create a matrix
        condition_data = []
        for idx, row in df_filtered.iterrows():
            if pd.notna(row['ChronicConditionList']):
                conditions = row['ChronicConditionList'].split(',')
                for condition in conditions:
                    condition_data.append({
                        'Condition': condition.strip(),
                        'PotentialFraud': row['PotentialFraud'],
                        'Provider': row['Provider']
                    })
        
        if condition_data:
            condition_df = pd.DataFrame(condition_data)
            condition_fraud_rate = condition_df.groupby('Condition')['PotentialFraud'].apply(
                lambda x: (x == 'Yes').mean() * 100
            ).sort_values(ascending=False).head(15)
            
            fig14 = px.bar(
                x=condition_fraud_rate.values,
                y=condition_fraud_rate.index,
                title="Conditions with Highest Fraud Rate",
                labels={'x': 'Fraud Rate (%)', 'y': 'Condition'},
                orientation='h',
                color=condition_fraud_rate.values,
                color_continuous_scale='Reds'
            )
            fig14.update_layout(
                font_family="Poppins",
                title_font_size=20,
                title_font_color="#2c3e50",
                height=500,
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='#f8f9fa'
            )
            st.plotly_chart(fig14, use_container_width=True)
            
            # Add insights for graph 14
            if not condition_fraud_rate.empty:
                high_risk_condition = condition_fraud_rate.index[0]
                high_risk_rate = condition_fraud_rate.iloc[0]
                add_graph_insights(
                    "High-Risk Condition Analysis",
                    f"• Highest fraud rate: {high_risk_condition} ({high_risk_rate:.1f}%)<br>• Conditions with high fraud rates require focused review<br>• May indicate over-diagnosis or billing for unperformed services"
                )


if __name__ == "__main__":
    main()