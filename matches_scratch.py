from ScraperFC import Sofascore
import pandas as pd
import time

scraper = Sofascore()

print("Pobieram harmonogram La Liga 2024/2025...")
schedule = scraper.get_match_dicts(year="24/25", league="Spain La Liga")

print(f"Pobrano {len(schedule)} meczów – testujemy na pierwszych 5")

test_matches = schedule[:5]

all_stats = []

for idx, match_dict in enumerate(test_matches):
    match_id = match_dict.get('id')
    home_team = match_dict.get('homeTeam', {}).get('name', 'Unknown')
    away_team = match_dict.get('awayTeam', {}).get('name', 'Unknown')
    print(f"Pobieram statystyki meczu {idx+1}/5: {home_team} vs {away_team} (ID: {match_id})")

    try:
        # Statystyki drużynowe
        team_stats_df = scraper.scrape_team_match_stats(match_id)

        # Wyciągnij statystyki po nazwie (z Twojego printu – kolumna 'name')
        def get_stat(df, stat_name):
            row = df[df['name'] == stat_name]
            if not row.empty:
                return row.iloc[0]['homeValue'], row.iloc[0]['awayValue']
            return 0, 0

        home_corners, away_corners = get_stat(team_stats_df, 'Corner kicks')
        home_yellow, away_yellow = get_stat(team_stats_df, 'Yellow cards')
        home_shots_on_target, away_shots_on_target = get_stat(team_stats_df, 'Shots on goal')

        # Strzelcy i minuty (z get_match_dict – incidents)
        full_match = scraper.get_match_dict(match_id)
        incidents = full_match.get('incidents', [])
        goals = []
        for incident in incidents:
            if incident.get('type') == 'goal':
                scorer = incident.get('player', {}).get('name', 'Unknown')
                minute = incident.get('time', 0)
                team = 'home' if incident.get('home') else 'away'
                goals.append(f"{scorer} ({team}) w {minute}'")

        stats_row = {
            'home_team': home_team,
            'away_team': away_team,
            'home_goals': match_dict.get('homeScore', {}).get('normaltime', 0),
            'away_goals': match_dict.get('awayScore', {}).get('normaltime', 0),
            'home_corners': home_corners,
            'away_corners': away_corners,
            'home_yellow_cards': home_yellow,
            'away_yellow_cards': away_yellow,
            'home_shots_on_target': home_shots_on_target,
            'away_shots_on_target': away_shots_on_target,
            'goals_details': ', '.join(goals) or 'Brak goli'
        }
        all_stats.append(stats_row)
    except Exception as e:
        print(f"Błąd przy meczu {match_id}: {e}")

    time.sleep(1)

df = pd.DataFrame(all_stats)
df.to_csv("test_5_matches.csv", index=False)

print("Gotowe! Plik test_5_matches.csv")
print(df)