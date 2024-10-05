import zipfile
import os
import re
import pandas as pd

# Define patterns for analysis
patterns = {
    'stunned': r'You are momentarily stunned!',
    'hit_by_spell': r'You are hit for \d+ damage!',
    'hit_by_attack': r'attacks you for \d+ damage!',
    'breath_damage': r'is hit for (\d+) damage!'  # Captures the numeric damage value
}


def count_occurrences_in_file(file_path):
    stunned_by_spells = 0
    stunned_by_attacks = 0
    total_attacks = 0
    total_spells = 0
    breath_damage_values = []

    with open(file_path, 'r') as file:
        lines = file.readlines()

        for i, line in enumerate(lines):
            # Count total occurrences of attacks and spells
            if re.search(patterns['hit_by_attack'], line):
                total_attacks += 1
            if re.search(patterns['hit_by_spell'], line):
                total_spells += 1

            # Look for stunned line and check the line above
            if re.search(patterns['stunned'], line) and i > 0:
                previous_line = lines[i - 1]
                if re.search(patterns['hit_by_spell'], previous_line):
                    stunned_by_spells += 1
                elif re.search(patterns['hit_by_attack'], previous_line):
                    stunned_by_attacks += 1

            # Track breath damage values
            breath_match = re.search(patterns['breath_damage'], line)
            if breath_match:
                damage_value = int(breath_match.group(1))
                breath_damage_values.append(damage_value)

    return {
        'stunned_by_spells': stunned_by_spells,
        'stunned_by_attacks': stunned_by_attacks,
        'total_attacks': total_attacks,
        'total_spells': total_spells,
        'breath_damage_values': breath_damage_values
    }


def analyze_zip(zip_file_path):
    # Extract the zip file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        extract_path = zip_file_path.replace('.zip', '')
        zip_ref.extractall(extract_path)

    # Initialize counters
    overall_counts = {
        'stunned_by_spells': 0,
        'stunned_by_attacks': 0,
        'total_attacks': 0,
        'total_spells': 0,
        'breath_damage_values': []
    }

    # Analyze each extracted file
    for file_name in os.listdir(extract_path):
        file_path = os.path.join(extract_path, file_name)
        if os.path.isfile(file_path):
            file_counts = count_occurrences_in_file(file_path)
            for key in overall_counts:
                if key == 'breath_damage_values':
                    overall_counts[key].extend(file_counts[key])  # Aggregate damage values
                else:
                    overall_counts[key] += file_counts[key]

    # Calculate stun rates after all data is aggregated
    total_attacks = overall_counts['total_attacks']
    total_spells = overall_counts['total_spells']
    stunned_by_attacks = overall_counts['stunned_by_attacks']
    stunned_by_spells = overall_counts['stunned_by_spells']

    attack_stun_rate = round((stunned_by_attacks / total_attacks) * 100, 3) if total_attacks > 0 else 0.0
    spell_stun_rate = round((stunned_by_spells / total_spells) * 100, 3) if total_spells > 0 else 0.0
    overall_stun_rate = round(((stunned_by_attacks + stunned_by_spells) / (total_attacks + total_spells)) * 100, 3) if total_attacks > 0 else 0.0

    # Calculate average breath damage
    breath_damage_values = overall_counts['breath_damage_values']
    avg_breath_damage = round(sum(breath_damage_values) / len(breath_damage_values), 3) if breath_damage_values else 0.0
    breath_count = len(breath_damage_values)  # Count the number of breaths

    # Add stun rates, breath damage, and breath count to the final output
    overall_counts['attack_stun_rate (%)'] = attack_stun_rate
    overall_counts['spell_stun_rate (%)'] = spell_stun_rate
    overall_counts['Breath damage (avg)'] = avg_breath_damage
    overall_counts['Number of breaths'] = breath_count
    overall_counts['overall_stun_rate (%)'] = overall_stun_rate

    # Remove raw breath damage values from final output
    overall_counts.pop('breath_damage_values')

    return overall_counts


# Analyze both the WITH and WITHOUT zip files
with_counts = analyze_zip('WITH.zip')
without_counts = analyze_zip('WITHOUT.zip')

# Convert results to pandas DataFrame for table display
data = {
    "Stat": [
        "Stunned by Spells",
        "Stunned by Attacks",
        "Total Attacks",
        "Total Spells",
        "Attack Stun Rate (%)",
        "Spell Stun Rate (%)",
        "Overall Stun Rate (%)",
        "Breath Damage (avg)",
        "Number of Breaths"
    ],
    "WITH": [
        with_counts['stunned_by_spells'],
        with_counts['stunned_by_attacks'],
        with_counts['total_attacks'],
        with_counts['total_spells'],
        with_counts['attack_stun_rate (%)'],
        with_counts['spell_stun_rate (%)'],
        with_counts['overall_stun_rate (%)'],
        with_counts['Breath damage (avg)'],
        with_counts['Number of breaths']
    ],
    "WITHOUT": [
        without_counts['stunned_by_spells'],
        without_counts['stunned_by_attacks'],
        without_counts['total_attacks'],
        without_counts['total_spells'],
        without_counts['attack_stun_rate (%)'],
        without_counts['spell_stun_rate (%)'],
        without_counts['overall_stun_rate (%)'],
        without_counts['Breath damage (avg)'],
        without_counts['Number of breaths']
    ]
}

df = pd.DataFrame(data)

# Format the output by removing decimals for integer-like columns
df['WITH'] = df['WITH'].apply(lambda x: f'{x:.0f}' if isinstance(x, (int, float)) and x.is_integer() else x)
df['WITHOUT'] = df['WITHOUT'].apply(lambda x: f'{x:.0f}' if isinstance(x, (int, float)) and x.is_integer() else x)

# Print the DataFrame as a table
print(df)
