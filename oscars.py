import pandas as pd

def print_top3_from_nominations(csv_path):
    """
    Reads a CSV of Oscar nominations (one nominee per category per row),
    counts votes per category, and prints the top 3 winners (with ties).
    """
    df = pd.read_csv(csv_path)
    # For each award category (skip Timestamp & Name columns)
    for col in df.columns[2:]:
        # Count how many times each person was nominated
        counts = df[col].value_counts()
        # Assign ranks (1 = highest count), ties share the same rank
        ranks = {}
        sorted_items = counts.items()
        current_rank = 1
        prev_count = None
        for idx, (person, vote_count) in enumerate(sorted_items):
            if idx == 0:
                prev_count = vote_count
                ranks[person] = current_rank
            else:
                if vote_count < prev_count:
                    current_rank = idx + 1
                    prev_count = vote_count
                ranks[person] = current_rank

        # Print results for ranks 1, 2, and 3
        print(f"{col}:")
        for rank in [1, 2, 3]:
            # Find all names with this rank
            names = [p for p, r in ranks.items() if r == rank]
            if not names:
                continue
            # All tied names have the same vote count
            vote_count = counts[names[0]]
            # Format names with “(tie)” if needed
            if len(names) > 1:
                name_str = ", ".join(names) + " (tie)"
            else:
                name_str = names[0]
            print(f"  {rank}. {name_str}: {vote_count} votes")
        print()  # blank line between categories

# Hardcoded path to your CSV file:
csv_path = "./csv/jsc_oscars_fall_25.csv"

# To execute, uncomment the following line and ensure the CSV path is correct:
print_top3_from_nominations(csv_path)
