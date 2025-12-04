import pandas as pd

def calculate_stats(csv_path):
    # Read the CSV
    df = pd.read_csv(csv_path)

    wins = {}  # count of 1st‐place finishes
    noms = {}  # count of top‐3 nominations

    # Process each category (skip the first two columns)
    for col in df.columns[2:]:
        counts = df[col].value_counts()
        # Assign ranks (1 = highest count), ties share the same rank
        ranks = {}
        current_rank = 1
        prev_count = None
        for idx, (person, count) in enumerate(counts.items()):
            if idx == 0:
                prev_count = count
                ranks[person] = current_rank
            else:
                if count < prev_count:
                    current_rank = idx + 1
                    prev_count = count
                ranks[person] = current_rank

        # Tally nominations and wins
        for person, rank in ranks.items():
            if rank <= 3:
                noms[person] = noms.get(person, 0) + 1
                if rank == 1:
                    wins[person] = wins.get(person, 0) + 1

    # Print each person’s stats
    print(f"{'Name':<20} {'Wins':>4} {'Noms':>5} {'Win%':>6}")
    print("-" * 37)
    for person in sorted(noms, key=lambda p: wins.get(p, 0), reverse=True):
        w = wins.get(person, 0)
        n = noms[person]
        pct = (w / n * 100) if n else 0
        print(f"{person:<20} {w:>4} {n:>5} {pct:6.1f}%")

if __name__ == "__main__":
    # Hard‑code your CSV file path here:
    csv_path = "./jsc_oscars_spring_25.csv"
    calculate_stats(csv_path)
