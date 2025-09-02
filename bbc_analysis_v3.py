"""
BBC News Disability Coverage Analysis - Version 3.0
Author: P.C. O'Brien
Date: July 2025
License: MIT

Purpose: Quantitative analysis of disability representation patterns
         in BBC News disability section headlines using dual methodology.
         
Dataset: Complete scrape of https://www.bbc.co.uk/news/disability
         from January 2025 to July 2025 using Easy Data Scraper
         
Methodology: Implements both multi-category analysis (thematic prevalence)
            and exclusive categorisation (unique article distribution)
            
v3 Changes: Fixed multi_sum/exclusive_sum calculations
           Added optional co-occurrence heatmap visualization
"""

import re
import pandas as pd
import matplotlib.pyplot as plt
import textwrap
import numpy as np
import seaborn as sns

# --- DATA LOADING ---
try:
    # Load CSV, handle potential parsing errors, and define the target column
    df = pd.read_csv('bbc-2025-07-29.csv', on_bad_lines='skip')
    headline_col = 'ssrcss-yjj6jm-LinkPostHeadline'
    
    # Clean the data by dropping rows where the headline might be missing
    df.dropna(subset=[headline_col], inplace=True)
    
    print(f"Loaded {len(df)} articles from CSV\n")
    
except FileNotFoundError:
    print("Error: The file 'bbc-2025-07-29.csv' was not found in the current directory.")
    exit()


# --- REGEX PATTERNS (REFINED WITH PLURAL HANDLING) ---
# Using (?:...) for non-capturing groups to suppress the UserWarning and improve performance.
patterns = {
    # --- CORE DISABILITY CATEGORIES (REFINED) ---
    "SEND/Special Schools": r"(?i)\b(?:SEND|SEN|special needs|special (?:school|education)s?|mainstream schools?|specialist primary|education plans?|teaching assistants?|pupils?|Ofsted|schools?)\b",
    "Deaf/Hearing": r"(?i)\b(?:deaf|BSL|cochlear|hearing loss|hard of hearing|hearing dogs?|sign language|hearing-impaired|ear ?plugs?|bionic ears|lip-read|tinnitus|ringing in.+ears)\b",
    "Blind/Vision": r"(?i)\b(?:blind(?:ness)?|Braille|visually impaired|sight(?: loss| impaired)|vision loss|partially sighted|guide dogs?|lost.+sight|losing sight|blinded)\b",
    "Chronic Illness/Pain": r"(?i)\b(?:chronic (?:pain|illness)|fibromyalgia|ME/CFS|chronic fatigue|pain disorder|invisible illness|long covid|cancer|MS|epilepsy|seizure|stroke|dementia|colitis|cystic fibrosis|terminally ill|arthritis|cannot eat or drink|weighed|scales)\b",
    "Physical & Mobility": r"(?i)\b(?:wheelchair|paraly[sz](?:e|i|ed|ing)|amputee|physical disabilit(?:y|ies)|spinal|limb|stomas?|one-handed|cerebral palsy|muscular dystrophy|mobility (?:aid|scooter)s?|crutch|prosthetic|quadriplegic|paraplegic|no hands|walk again|surfer)\b",
    "Learning Disabilities": r"(?i)\b(?:learning disabilit(?:y|ies)|intellectual disabilit(?:y|ies)|Down['']s? syndrome|cognitive impairment|Makaton|non-verbal)\b",
    "Mental Health & Neuro": r"(?i)\b(?:mental health|anxiety|depression|Tourette['']s?|bipolar|schizophrenia|psychiatric|PTSD|eating disorder|ADHD|attention deficit|toxic|overdosed|isolating)\b",
    "Autism/Neurodiversity": r"(?i)\b(?:autis(?:m|tic)|neurodivers(?:e|ity))\b",

    # --- THEMATIC CATEGORIES (REFINED) ---
    "Benefits, Care & Systemic Issues": r"(?i)\b(?:PIP|DLA|DSA|benefits?|welfare|blue badges?|social care|carers?|council|funding|NHS|Universal Credit|assessment|respite|inquest|ombudsman|care (?:package|home|plan|subsidy|loophole|agency|needs)|day centres?|supported living|telecare|hydrotherapy|Oliver McGowan|foster homes?|hospitals?|policy|government|failures)\b",
    "Accessibility & Inclusion": r"(?i)\b(?:accessib(?:le|ility)|inclusive|inclusion|adapt(?:ed|ive)|passport|ramps?|step-free|accessible toilets?|parking (?:bay|permit)s?|boardwalks?|communication boards?|inaccessible|barriers|priority seats?|quiet spaces?|adapt clothes)\b",
    "Family & Carer Perspective": r"(?i)\b(?:parent|mum|mom|dad|mother|father|family|son|daughter|children|child|husband|wife)\b",
    "Sports, Arts & Culture": r"(?i)\b(?:paralympi(?:an|c|cs)|Special Olympics|Olympic|sports?|football(?:ers)?|rugby|swim|cycl(?:ing)?|ski|race|artist|music|choir|theatre|pianist|actor|model|vogue|Proms|Glastonbury|cheerleading|snooker|goalball|triathlon|cricket|powerchair footballers?|wing walk|culture|gig|circus|Marathon|panto|tennis|para-driver|climbing wall|rower)\b",
    "Charity, People & Community": r"(?i)\b(?:charity|fundrais|donation|volunteer|community|campaigner|trust|foundation|MBE|OBE|BEM|honour(?:ed)?|honorary degrees?|Rose Ayling-Ellis|Grey-Thompson|Billy Monger|Sammi Kinghorn|Rosie Jones|Christine McGuiness|Sally Phillips|Adrian Scarborough|pioneers?|tributes?|awards?|Dragons' Den|blue plaques?)\b",
    "Animals & Well-being": r"(?i)\b(?:(?:guide|hearing|assistance|service|support|therapy) (?:dogs?|puppy|puppies|animals?|cats?|horses?|cockapoo|donkeys?)|Crufts|miniature horses?|emotional support|guinea pigs?|skunks?|canine|trainee guide dogs?|toy squirrel.*guide dogs?)\b",
    "Infrastructure & Transport": r"(?i)\b(?:lifts?|minibus(?:es)?|bus cuts?|footbridges?|pavements?|stations?|TfL|transport|trikes?|housing|home adaptations?)\b",
    "Work, Employment & Enterprise": r"(?i)\b(?:cafe|brewery|garden centres?|farms?|work coach(?:es)?|jobs?|workplace|employees?|working|unemployed|employment)\b",
    
    # --- HUMAN INTEREST STORIES ---
    "Personal Stories & Empowerment": r"(?i)\b(?:inspire|inspirational|dream|journey|thriving|empowered|experience|overcame|making most of life|'s story|life-changing|my life|my face|my GP told me|defies|hopeful|mission|letter of thanks)\b",

    # --- GENERAL CATCH-ALL ---
    "General 'Disability' Keyword": r"(?i)\b(?:disabilit(?:y|ies)|disabled|handicap|impairment|vulnerable|additional needs|enable new experiences)\b"
}


# --- MULTI-CATEGORY ANALYSIS (ORIGINAL APPROACH) ---
print("=" * 60)
print("MULTI-CATEGORY ANALYSIS (Headlines can match multiple categories)")
print("=" * 60)

multi_category_results = {}
all_matched_indices = set()

# Loop through each pattern to categorize headlines
for label, pattern in patterns.items():
    # Find all rows where the headline matches the current pattern
    matches = df[headline_col].str.contains(pattern, regex=True, na=False)
    
    # Get the indices of the matched headlines
    matched_indices = df[matches].index
    
    # Add these indices to our master set of all matched headlines
    all_matched_indices.update(matched_indices)
    
    # Store the count and the list of headlines for this category
    matched_headlines = df.loc[matched_indices, headline_col].tolist()
    multi_category_results[label] = {
        "count": len(matched_headlines),
        "headlines": matched_headlines
    }

# Find uncategorized headlines for multi-category approach
unmatched_indices = set(df.index) - all_matched_indices
unmatched_headlines = df.loc[list(unmatched_indices), headline_col].tolist()

multi_category_results["Uncategorized"] = {
    "count": len(unmatched_headlines),
    "headlines": unmatched_headlines
}

# Calculate multi_sum properly (excluding Uncategorized)
multi_sum = sum(res['count'] for label, res in multi_category_results.items() if label != "Uncategorized")

# Print multi-category counts
multi_counts_sorted = dict(sorted(
    {label: res['count'] for label, res in multi_category_results.items() if res['count'] > 0}.items(),
    key=lambda item: item[1], reverse=True
))

print("\nMulti-category counts:")
for label, count in multi_counts_sorted.items():
    percentage = (count / len(df)) * 100 if label != "Uncategorized" else (count / len(df)) * 100
    print(f"  {label}: {count} articles ({percentage:.1f}%)")
print(f"\nTotal multi-category counts (excluding Uncategorized): {multi_sum}")
print(f"Sum should exceed 707 due to overlaps")


# --- EXCLUSIVE CATEGORY ANALYSIS (FIRST MATCH WINS) ---
print("\n" + "=" * 60)
print("EXCLUSIVE CATEGORY ANALYSIS (First match wins)")
print("=" * 60)

exclusive_category_results = {label: {"count": 0, "headlines": []} for label in patterns.keys()}
exclusive_category_results["Uncategorized"] = {"count": 0, "headlines": []}

# Process each headline once, assigning to first matching category
for idx, row in df.iterrows():
    headline = str(row[headline_col])
    matched = False
    
    # Check patterns in order - first match wins
    for label, pattern in patterns.items():
        if re.search(pattern, headline):
            exclusive_category_results[label]["count"] += 1
            exclusive_category_results[label]["headlines"].append(headline)
            matched = True
            break
    
    # If no pattern matched, it's uncategorized
    if not matched:
        exclusive_category_results["Uncategorized"]["count"] += 1
        exclusive_category_results["Uncategorized"]["headlines"].append(headline)

# Calculate exclusive_sum properly
exclusive_sum = sum(res['count'] for res in exclusive_category_results.values())

# Print exclusive category counts
exclusive_counts_sorted = dict(sorted(
    {label: res['count'] for label, res in exclusive_category_results.items() if res['count'] > 0}.items(),
    key=lambda item: item[1], reverse=True
))

print("\nExclusive category counts:")
for label, count in exclusive_counts_sorted.items():
    percentage = (count / len(df)) * 100
    print(f"  {label}: {count} articles ({percentage:.1f}%)")
print(f"\nTotal exclusive counts: {exclusive_sum}")
print(f"Should equal 707 (actual CSV rows: {len(df)})")


# --- SAMPLE UNCATEGORIZED HEADLINES ---
print("\n" + "=" * 60)
print("SAMPLE UNCATEGORIZED HEADLINES (for regex refinement)")
print("=" * 60)

if exclusive_category_results["Uncategorized"]["headlines"]:
    print(f"\nShowing first 20 of {len(exclusive_category_results['Uncategorized']['headlines'])} uncategorized headlines:")
    for i, headline in enumerate(exclusive_category_results["Uncategorized"]["headlines"][:20], 1):
        print(f"{i:2}. {headline}")
else:
    print("All headlines were successfully categorized!")


# --- VISUALIZATION: SIDE-BY-SIDE COMPARISON ---
print("\n" + "=" * 60)
print("GENERATING VISUALIZATION...")
print("=" * 60)

# Prepare data for plotting - use all categories for consistent comparison
all_categories = list(patterns.keys()) + ["Uncategorized"]
multi_values = [multi_category_results.get(cat, {"count": 0})["count"] for cat in all_categories]
exclusive_values = [exclusive_category_results.get(cat, {"count": 0})["count"] for cat in all_categories]

# Sort by exclusive counts for better readability
sorted_indices = np.argsort(exclusive_values)
all_categories = [all_categories[i] for i in sorted_indices]
multi_values = [multi_values[i] for i in sorted_indices]
exclusive_values = [exclusive_values[i] for i in sorted_indices]

# Create figure with side-by-side bars
fig, ax = plt.subplots(figsize=(16, 12))

# Calculate bar positions
y_pos = np.arange(len(all_categories))
bar_height = 0.35

# Create bars
bars1 = ax.barh(y_pos - bar_height/2, multi_values, bar_height, 
                label='Multi-category', color='#2E86AB', alpha=0.8, edgecolor='black', linewidth=0.5)
bars2 = ax.barh(y_pos + bar_height/2, exclusive_values, bar_height,
                label='Exclusive', color='#A23B72', alpha=0.8, edgecolor='black', linewidth=0.5)

# Customize the plot
ax.set_xlabel('Number of Articles', fontsize=12)
ax.set_title('BBC Disability News Coverage: Multi-category vs Exclusive Counts\n(707 total articles)', 
             fontsize=16, pad=20)
ax.set_yticks(y_pos)
ax.set_yticklabels([textwrap.fill(label, 25) for label in all_categories], fontsize=10)
ax.legend(loc='lower right', fontsize=11)
ax.grid(axis='x', alpha=0.3)

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        width = bar.get_width()
        if width > 0:  # Only show label if count > 0
            ax.text(width + 1, bar.get_y() + bar.get_height()/2, f'{int(width)}',
                   ha='left', va='center', fontsize=9)

# Add totals in the title area
ax.text(0.02, 0.98, f'Multi-category total: {multi_sum} (with overlaps)\nExclusive total: {exclusive_sum} (unique articles)', 
        transform=ax.transAxes, fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('bbc_disability_coverage_v3.png', dpi=300, bbox_inches='tight')
plt.show()


# --- CO-OCCURRENCE HEATMAP (NEW IN V3) ---
print("\n" + "=" * 60)
print("GENERATING CO-OCCURRENCE HEATMAP...")
print("=" * 60)

# Create co-occurrence matrix (excluding Uncategorized and General Disability Keyword for clarity)
categories_for_heatmap = [cat for cat in patterns.keys() 
                          if cat not in ["Uncategorized", "General 'Disability' Keyword"]]

co_occurrence_matrix = pd.DataFrame(0, index=categories_for_heatmap, columns=categories_for_heatmap)

# Count co-occurrences
for idx, row in df.iterrows():
    headline = str(row[headline_col])
    matched_cats = []
    
    for label in categories_for_heatmap:
        pattern = patterns[label]
        if re.search(pattern, headline):
            matched_cats.append(label)
    
    # Update co-occurrence matrix
    for i, cat1 in enumerate(matched_cats):
        for cat2 in matched_cats[i:]:
            co_occurrence_matrix.at[cat1, cat2] += 1
            if cat1 != cat2:
                co_occurrence_matrix.at[cat2, cat1] += 1

# Create heatmap
plt.figure(figsize=(14, 12))
sns.heatmap(co_occurrence_matrix, annot=True, fmt='d', cmap='YlOrRd', 
            cbar_kws={'label': 'Number of Co-occurrences'},
            linewidths=0.5, linecolor='gray')
plt.title('Co-occurrence Matrix of Disability Categories in BBC Coverage\n(How often categories appear together)', 
          fontsize=14, pad=20)
plt.xlabel('Category', fontsize=12)
plt.ylabel('Category', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('bbc_cooccurrence_heatmap_v3.png', dpi=300, bbox_inches='tight')
plt.show()


# --- VISIBILITY ANALYSIS ---
print("\n" + "=" * 60)
print("VISIBILITY ANALYSIS")
print("=" * 60)

# Define visibility categories
visible_categories = ["Deaf/Hearing", "Blind/Vision", "Physical & Mobility", "Learning Disabilities"]
invisible_categories = ["Chronic Illness/Pain", "Mental Health & Neuro", "Autism/Neurodiversity"]

# Calculate visibility ratios for exclusive categories
visible_exclusive = sum(exclusive_category_results[cat]["count"] for cat in visible_categories)
invisible_exclusive = sum(exclusive_category_results[cat]["count"] for cat in invisible_categories)

# Calculate visibility ratios for multi-category
visible_multi = sum(multi_category_results[cat]["count"] for cat in visible_categories)
invisible_multi = sum(multi_category_results[cat]["count"] for cat in invisible_categories)

print(f"\nExclusive Category Analysis:")
print(f"  Visible disabilities: {visible_exclusive} articles ({(visible_exclusive/len(df)*100):.1f}%)")
print(f"  Invisible disabilities: {invisible_exclusive} articles ({(invisible_exclusive/len(df)*100):.1f}%)")
print(f"  Ratio (visible:invisible): {visible_exclusive/invisible_exclusive:.1f}:1")

print(f"\nMulti-Category Analysis:")
print(f"  Visible disabilities: {visible_multi} thematic instances")
print(f"  Invisible disabilities: {invisible_multi} thematic instances")
print(f"  Ratio (visible:invisible): {visible_multi/invisible_multi:.1f}:1")


print("\n" + "=" * 60)
print("Analysis complete!")
print(f"Multi-category approach found {multi_sum} category matches across {len(df)} articles")
print(f"Exclusive approach assigned {exclusive_sum} articles uniquely")
print(f"Average categories per article: {multi_sum/len(df):.2f}")
print("\nVisualizations saved as:")
print("  - bbc_disability_coverage_v3.png")
print("  - bbc_cooccurrence_heatmap_v3.png")