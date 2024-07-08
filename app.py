import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
st.header("Soccer Science: Data-Driven Game Analysis")
st.image("header.jpg", width=800, use_column_width=True)


# Load and preprocess data
df = pd.read_csv("spi_matches.csv")
df['league'] = df['league'].str.strip()
leagues = ['Barclays Premier League', 'Spanish Primera Division', 'French Ligue 1', 'German Bundesliga', 'Italy Serie A']
df = df[df['league'].isin(leagues)]

# Ensure numeric columns are converted properly
numeric_columns = ['proj_score1', 'proj_score2', 'score1', 'score2', 'xg1', 'xg2', 'nsxg1', 'nsxg2', 'adj_score1', 'adj_score2', 'importance1', 'importance2', 'prob1', 'prob2']
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Convert date to datetime with correct format
df['date'] = pd.to_datetime(df['date'])#, format='%d/%m/%Y', dayfirst=True)

# Extract month from date
df['month'] = df['date'].dt.strftime('%B')

# 1. Radar Chart - Comparison of Selected Teams
st.header("Radar Chart - Comparison of Selected Teams")
year1 = st.selectbox("Select Year for Radar Chart", options=df['season'].unique(), key="year1")
league1 = st.selectbox("Select League for Radar Chart", options=leagues, key="league1")
teams_in_league_season1 = pd.concat([df[(df['league'] == league1) & (df['season'] == year1)]['team1'],
                                    df[(df['league'] == league1) & (df['season'] == year1)]['team2']]).unique()
selected_teams1 = st.multiselect("Select Teams for Radar Chart", options=teams_in_league_season1, key="teams1")
home_or_away1 = st.radio("Home or Away for Radar Chart", options=['Home', 'Away'], key="home_or_away1")

if home_or_away1 == 'Home':
    filtered_df1 = df[(df['season'] == year1) & (df['league'] == league1) & (df['team1'].isin(selected_teams1))].copy()
    filtered_df1['team'] = filtered_df1['team1']
    filtered_df1['proj_score'] = filtered_df1['proj_score1']
    filtered_df1['score'] = filtered_df1['score1']
    filtered_df1['xg'] = filtered_df1['xg1']
    filtered_df1['nsxg'] = filtered_df1['nsxg1']
    filtered_df1['adj_score'] = filtered_df1['adj_score1']
else:
    filtered_df1 = df[(df['season'] == year1) & (df['league'] == league1) & (df['team2'].isin(selected_teams1))].copy()
    filtered_df1['team'] = filtered_df1['team2']
    filtered_df1['proj_score'] = filtered_df1['proj_score2']
    filtered_df1['score'] = filtered_df1['score2']
    filtered_df1['xg'] = filtered_df1['xg2']
    filtered_df1['nsxg'] = filtered_df1['nsxg2']
    filtered_df1['adj_score'] = filtered_df1['adj_score2']

# Calculate league averages considering home or away selection
league_df1 = df[(df['season'] == year1) & (df['league'] == league1)].copy()
if home_or_away1 == 'Home':
    league_df1['proj_score'] = league_df1['proj_score1']
    league_df1['score'] = league_df1['score1']
    league_df1['xg'] = league_df1['xg1']
    league_df1['nsxg'] = league_df1['nsxg1']
    league_df1['adj_score'] = league_df1['adj_score1']
else:
    league_df1['proj_score'] = league_df1['proj_score2']
    league_df1['score'] = league_df1['score2']
    league_df1['xg'] = league_df1['xg2']
    league_df1['nsxg'] = league_df1['nsxg2']
    league_df1['adj_score'] = league_df1['adj_score2']

league_avg1 = league_df1[['proj_score', 'score', 'xg', 'nsxg', 'adj_score']].mean()

if not selected_teams1:
    selected_teams1 = ['League Average']

team_avg1 = filtered_df1.groupby('team')[['proj_score', 'score', 'xg', 'nsxg', 'adj_score']].mean()

categories = ['Projected Score', 'Score', 'xG', 'nSxG', 'Adjusted Score']
columns_map = {'Projected Score': 'proj_score', 'Score': 'score', 'xG': 'xg', 'nSxG': 'nsxg', 'Adjusted Score': 'adj_score'}

fig1 = go.Figure()

fig1.add_trace(go.Scatterpolar(
    r=[league_avg1[columns_map[category]] for category in categories],
    theta=categories,
    fill='toself',
    name='League Average',
    line=dict(color='rgba(0,0,0,0.5)', width=2),
    marker=dict(size=8, color='rgba(0,0,0,0.5)')
))

for team in selected_teams1:
    if team == 'League Average':
        continue
    fig1.add_trace(go.Scatterpolar(
        r=[team_avg1.loc[team, columns_map[category]] for category in categories],
        theta=categories,
        fill='toself',
        name=team,
        line=dict(width=2),
        marker=dict(size=8)
    ))

fig1.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True
        )),
    showlegend=True,
    title=f'Comparison of Selected Teams in {year1} - {league1}',
    width=800,
    height=800
)

st.plotly_chart(fig1)

# 2. Bar Chart - Match Statistics
st.header("Bar Chart - Match Statistics")
year2 = st.selectbox("Select Year ", options=df['season'].unique(), key="year2")
league2 = st.selectbox("Select League ", options=leagues, key="league2")
teams_in_league_season2 = pd.concat([df[(df['league'] == league2) & (df['season'] == year2)]['team1'],
                                    df[(df['league'] == league2) & (df['season'] == year2)]['team2']]).unique()

if len(teams_in_league_season2) < 2:
    st.write("Not enough teams in the selected league and year to display comparison.")
else:
    col_team1, col_team2 = st.columns(2)
    with col_team1:
        team1_bar = st.selectbox("Select Team 1 ", options=teams_in_league_season2, key="team1_bar")
    with col_team2:
        team2_bar = st.selectbox("Select Team 2 ", options=[team for team in teams_in_league_season2 if team != team1_bar], key="team2_bar")

    filtered_match_df = df[(df['season'] == year2) & (df['league'] == league2) &
                           (((df['team1'] == team1_bar) & (df['team2'] == team2_bar)) |
                            ((df['team1'] == team2_bar) & (df['team2'] == team1_bar)))]

    if not filtered_match_df.empty:
        metrics_team1 = filtered_match_df[filtered_match_df['team1'] == team1_bar][['score1', 'xg1', 'proj_score1', 'nsxg1']].mean()
        metrics_team2 = filtered_match_df[filtered_match_df['team2'] == team2_bar][['score2', 'xg2', 'proj_score2', 'nsxg2']].mean()

        metrics_team1.index = ['Actual Goals Scored', 'Expected Goals', 'Projected Goals', 'Non-Shot Expected Goals']
        metrics_team2.index = ['Actual Goals Scored', 'Expected Goals', 'Projected Goals', 'Non-Shot Expected Goals']

        col1, col2 = st.columns(2)

        with col1:
            fig2 = go.Figure(data=[
                go.Bar(name=team1_bar, x=['Actual Goals Scored', 'Expected Goals', 'Projected Goals', 'Non-Shot Expected Goals'], y=metrics_team1),
                go.Bar(name=team2_bar, x=['Actual Goals Scored', 'Expected Goals', 'Projected Goals', 'Non-Shot Expected Goals'], y=metrics_team2)
            ])

            fig2.update_layout(
                barmode='group',
                title='Match Statistics',
                xaxis_title='Metric',
                yaxis_title='Goals/nSxG',
                legend_title='Teams'
            )

            st.plotly_chart(fig2)

        with col2:
            pre_match_probabilities = [metrics_team1['Non-Shot Expected Goals'], metrics_team2['Non-Shot Expected Goals']]
            labels = [team1_bar, team2_bar]
            fig3 = go.Figure(data=[go.Pie(labels=labels, values=pre_match_probabilities, hole=.3)])

            fig3.update_layout(
                title='Pre-Match Probabilities'
            )

            st.plotly_chart(fig3)
    else:
        st.write("There were no games between those teams in the selected year.")

# 3. Line Chart - Average Probability to Win over Months
st.header("Line Chart - Average Probability to Win over Months")
year3 = st.selectbox("Select Year for Line Chart", options=df['season'].unique(), key="year3")
league3 = st.selectbox("Select League for Line Chart", options=leagues, key="league3")
teams_in_league_season3 = pd.concat([df[(df['league'] == league3) & (df['season'] == year3)]['team1'],
                                    df[(df['league'] == league3) & (df['season'] == year3)]['team2']]).unique()

# Default to first two teams in the list if none are selected
default_teams3 = teams_in_league_season3[:2] if len(teams_in_league_season3) >= 2 else teams_in_league_season3
selected_teams3 = st.multiselect("Select Teams for Line Chart", options=teams_in_league_season3, default=default_teams3, key="teams3")
home_or_away3 = st.radio("Home or Away for Line Chart", options=['Home', 'Away'], key="home_or_away3")

if home_or_away3 == 'Home':
    filtered_df3 = df[(df['season'] == year3) & (df['league'] == league3) & (df['team1'].isin(selected_teams3))].copy()
    filtered_df3['team'] = filtered_df3['team1']
    filtered_df3['prob'] = filtered_df3['prob1']
else:
    filtered_df3 = df[(df['season'] == year3) & (df['league'] == league3) & (df['team2'].isin(selected_teams3))].copy()
    filtered_df3['team'] = filtered_df3['team2']
    filtered_df3['prob'] = filtered_df3['prob2']

monthly_avg_prob = filtered_df3.groupby(['month', 'team'])['prob'].mean().reset_index()

months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
monthly_avg_prob['month'] = pd.Categorical(monthly_avg_prob['month'], categories=months_order, ordered=True)
monthly_avg_prob = monthly_avg_prob.sort_values('month')

fig4 = px.line(monthly_avg_prob, x='month', y='prob', color='team', markers=True,
               labels={'month': 'Month', 'prob': 'Average Probability to Win'},
               title='Average Probability to Win over Months')

st.plotly_chart(fig4)
