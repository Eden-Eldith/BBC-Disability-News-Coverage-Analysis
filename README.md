# BBC Disability News Coverage Analysis

A quantitative analysis of disability representation patterns in BBC News' dedicated disability section (January-July 2025).


## Academic Paper

[Full Academic Paper (PDF)](The%20Range%20of%20Disability%20Diversity%20in%20BBC%20News%20Reporting%202.pdf)
#### Note: GitHub's PDF viewer removes clickable links. Please download the PDF for full functionality including clickable TOC and references

## Key Findings

Analysis of 707 headlines from [BBC's disability section](https://www.bbc.co.uk/news/disability) reveals:

- **3.9:1 ratio** between visible and invisible disability coverage
- **Mental health receives 0.8%** of coverage despite affecting 1 in 4 people
- **SEND/Special Schools dominates at 17%** of all coverage
- **Diagonal pattern in co-occurrence matrix** shows disabilities presented in isolation rather than as intersectional experiences

![Coverage Distribution](bbc_disability_coverage_v3.png)

![Co-occurrence Heatmap](bbc_cooccurrence_heatmap_v3.png)

## Methodology

This analysis employs a dual methodology:

1. **Multi-category analysis**: Measures thematic prevalence (articles can match multiple categories)
2. **Exclusive categorization**: Provides unique article distribution for statistical validity

The approach reveals that BBC disability coverage averages 1.42 category matches per article, yet the co-occurrence heatmap shows minimal intersection between different disability experiences in how stories are framed.

## Dataset

- **Source**: Complete scrape of https://www.bbc.co.uk/news/disability
- **Period**: January 1 - July 29, 2025
- **Size**: 707 articles
- **File**: `bbc-2025-07-29.csv`

## Usage

```bash
# Clone the repository
git clone https://github.com/[username]/bbc-disability-analysis
cd bbc-disability-analysis
```

# Install requirements
pip install pandas matplotlib seaborn numpy

# Run analysis
python bbc_analysis_v3.py

## Replication Guide

### Data Collection

1. **Install [Easy Scraper - One Click Web Scraper](https://chromewebstore.google.com/detail/easy-scraper-one-click-we/cljbfnedccphacfneigoegkiieckjndh) Chrome extension**
2. **Navigate to** https://www.bbc.co.uk/news/disability
3. **Configure columns to extract:**
   - `ssrcss-gfjuy9-Timestamp` - Date/time (e.g., "16:02" or "15:16 28 July")
   - `visually-hidden` - Full publication timestamp with accessibility text
   - `ssrcss-yjj6jm-LinkPostHeadline` - Main headline text (this is what we analyze)
   - `ssrcss-61mhsj-MetadataText` - Location/region metadata
4. **Scroll to load all articles** for your target date range
5. **Export as CSV** using the extension's export function

Note: BBC's CSS class names may change over time. If columns appear empty, inspect the page source for updated class names.

### Running the Analysis

#### Prerequisites
```bash
pip install pandas matplotlib seaborn numpy
```

#### Basic Usage
```bash
python bbc_analysis_v3.py
```

The script expects a file named `bbc-2025-07-29.csv` in the same directory. To use a different filename, modify line 27 in the script.

#### Output Files
- `bbc_disability_coverage_v3.png` - Comparative bar chart showing multi-category vs exclusive counts
- `bbc_cooccurrence_heatmap_v3.png` - Heatmap revealing category intersection patterns
- Console output with detailed statistics and sample uncategorized headlines

### Understanding the Methodology

#### Dual Methodology Explained
This analysis uses two complementary approaches:

1. **Multi-category Analysis**: 
   - Articles can match multiple categories
   - Shows thematic prevalence across the corpus
   - Total will exceed article count due to overlaps
   - Reveals compound framing in journalism

2. **Exclusive Category Analysis**:
   - Each article assigned to first matching category only
   - Provides true distribution percentages
   - Total equals exactly the number of articles
   - Enables statistical validity

#### Key Metrics to Track
- **Visibility Ratio**: Visible disabilities (sensory/physical) vs invisible (mental health/chronic pain)
- **Diagonal Dominance**: Strong diagonal in co-occurrence matrix = categories presented in isolation
- **Compound Framing**: Average categories per article (multi-category total ÷ article count)
- **Uncategorized Rate**: Below 10% indicates comprehensive category coverage

### Interpreting Results

#### Reading the Co-occurrence Heatmap
- **Diagonal values**: How often a category appears alone
- **Off-diagonal values**: How often two categories appear together
- **Dark red cells**: High co-occurrence (categories often linked)
- **Light/white cells**: Rare or no co-occurrence

A dominant diagonal pattern (as found in BBC coverage) indicates compartmentalized reporting rather than intersectional coverage.

#### Statistical Significance
- Chi-square test evaluates if distribution differs from random
- p < 0.001 indicates editorial selection patterns
- Compare your results against expected distributions based on disability prevalence

### Adapting the Framework

#### For Different News Sites
1. **Update the CSV filename** (line 27)
2. **Modify column name** for headlines:
   ```python
   headline_col = 'your-headline-column-name'  # line 28
   ```
3. **Adjust regex patterns** for terminology differences
4. **Consider regional variations** (e.g., "mom" vs "mum")

#### Adding New Categories
Add patterns to the `patterns` dictionary (starting line 43):
```python
"Your Category Name": r"(?i)\b(?:keyword1|keyword2|phrase with spaces|abbreviation)\b",
```

Tips for pattern writing:
- Use `(?i)` for case-insensitive matching
- Use `\b` for word boundaries
- Use `(?:...)` for non-capturing groups
- Test patterns at regex101.com

#### Time Period Analysis
To analyze specific date ranges, add after line 31:
```python
# Convert timestamp to datetime
df['date'] = pd.to_datetime(df['ssrcss-gfjuy9-Timestamp'], format='mixed')
# Filter for specific period
df = df[(df['date'] >= '2025-01-01') & (df['date'] <= '2025-07-29')]
```

### Troubleshooting

#### Common Issues and Solutions

**High Uncategorized Rate (>15%)**
- Review uncategorized headlines for patterns
- Check for BBC-specific terminology
- Consider metaphorical/indirect references
- Add edge cases to relevant categories

**Empty CSV Columns**
- BBC may have updated their CSS classes
- Inspect page source for new class names
- Update Easy Data Scraper configuration

**Memory Error with Large Datasets**
- Process in chunks:
  ```python
  chunk_size = 1000
  for chunk in pd.read_csv('file.csv', chunksize=chunk_size):
      # process chunk
  ```

**Regex Pattern Conflicts**
- Order patterns from most specific to least specific
- Use negative lookahead to exclude false matches:
  ```python
  r"(?i)\b(?:special school)(?!s? of thought)\b"
  ```

### Research Applications

#### Cross-Outlet Comparison
Apply the same categories to multiple news sources:
```python
bbc_results = analyze('bbc_data.csv')
guardian_results = analyze('guardian_data.csv')
compare_outlets(bbc_results, guardian_results)
```

#### Temporal Tracking
Monitor changes over time:
```python
results_2024 = analyze('data_2024.csv')
results_2025 = analyze('data_2025.csv')
plot_temporal_changes(results_2024, results_2025)
```

#### International Adaptation
- Translate categories for non-English analysis
- Adjust for cultural differences in disability discourse
- Consider local terminology and policy contexts

### Performance Optimization

For large datasets (>10,000 articles):
```python
# Use compiled regex for better performance
import re
compiled_patterns = {
    label: re.compile(pattern) 
    for label, pattern in patterns.items()
}

# Use vectorized operations where possible
df['matched'] = df[headline_col].str.contains(
    pattern, regex=True, na=False
).astype(int)
```

### Citation

If you use this methodology in your research:

**Academic Citation:**
```
O'Brien, P.C. (2025). The Range of Disability Diversity in BBC News Reporting: 
A Quantitative Content Analysis of the BBC's Dedicated Disability Section. 
GitHub. https://github.com/Eden-Eldith/BBC-Disability-News-Coverage-Analysis
```

**BibTeX:**
```bibtex
@misc{obrien2025bbc,
  author = {O'Brien, P.C.},
  title = {BBC Disability News Coverage Analysis},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/Eden-Eldith/BBC-Disability-News-Coverage-Analysis}
}
```

### Support & Consulting

For questions about implementation, custom adaptations, or consultation on diversity monitoring frameworks:

**Contact:** pcobrien@hotmail.co.uk  
**ORCID:** 0009-0007-3961-1182

I'm available for:
- Adapting this framework to your organization
- Custom analysis of media representation patterns

