"""
Title: Investment Behavior Analysis Script
Author: Rene Kachyna, kacr03@vse.cz
Date: 14.4.2025

Description:
This script analyzes survey data related to the investment behavior of Czech middle-income households.
It assumes the input data has already been preprocessed by the `edit_data.py` script.

Key functionalities:
- Filters data to include only middle-income households.
- Computes descriptive statistics and visualizes distributions of investment instruments, motivations, and barriers.
- Applies statistical tests (Mann-Whitney U, Spearman correlation, Chi-square test) to examine relationships between variables.
- Outputs formatted tables and plots for use in reporting.

Required packages:
- pandas
- numpy
- scipy
- matplotlib
- os
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy import stats

# -------------------------------
# Section: Flags
# -------------------------------

# Set to true if you want to plot charts and tables
plot = False

# -------------------------------
# Section: Data Loading
# -------------------------------

# Prompt user for full file path and check if it exists
file_path = input("Enter the full path to your CSV file:\n").strip()
if not os.path.exists(file_path):
    print("File does not exist.")
    exit()

# Load CSV and filter for middle-income households
df = pd.read_csv(file_path)
df = df[df["is_middle_income"] == 1]
df_invests = df[df["investment_frequency"].isin([1, 2])]

# -------------------------------
# Section: Count Dictionaries
# -------------------------------
# Dictionaries used to aggregate multiple-choice variables

# Investment instruments
instrument_counts = {"instrument_stock" : 0,
               "instrument_bonds" : 0,
               "instrument_other" : 0,
               "instrument_commodities" : 0,
               "instrument_crypto" : 0,
               "instrument_reality" : 0,
               "instrument_funds" : 0,
               "instrument_savings_account" : 0
               }

# Investment motivations
reason_counts = {"i_reasons_long_term_appr" : 0,
               "i_reasons_recommend" : 0,
               "i_reasons_hobby" : 0,
               "i_reasons_other" : 0,
               "i_reasons_better_than_savings" : 0,
               "i_reasons_inflation_protection" : 0,
               "i_reasons_get_rich_fast" : 0,
               "i_reasons_future_precaution" : 0
               }

# Investment barriers
barrier_counts = {"i_barriers_other" : 0,
               "i_barriers_capital" : 0,
               "i_barriers_knowledge" : 0,
               "i_barriers_time" : 0,
               "i_barriers_trust" : 0,
               "i_barriers_not_caring" : 0,
               "i_barriers_difficulty" : 0,
               "i_barriers_fear_of_losing_money" : 0,
               "i_barriers_enjoy_present" : 0
               }

# -------------------------------
# Section: Function Definitions
# -------------------------------

# Print a nicely formatted statistic sectio
def printStatistic( name, stat ):
    print( name + ": ")
    print(stat)
    print( "\n ---------- \n")

# Run a Mann-Whitney U test on two groups defined by 'group' variable for 'target' ordinal outcome 
def mann_whitney( name, group, target ):
    print(name + ":")
    group_0 = df[df[group] == 0][target]
    group_1 = df[df[group] == 1][target]
    u_stat, p_mw = stats.mannwhitneyu(group_0, group_1, alternative="two-sided")
    print(f" Mann-Whitney U = {u_stat}, p = {p_mw} \n  group0 mean = {group_0.mean()} \n  group1 mean = {group_1.mean()}")
    print("\n ---------- \n")

# Calculate Spearman correlation between two variables on full dataset
def spearman( name, var1, var2 ):
    print(name + ":")
    rho, p_value = stats.spearmanr(df[var1], df[var2])
    print(f"Spearman ρ = {rho}, p = {p_value}")
    print("\n ---------- \n")

# Calculate Spearman correlation only for respondents who invest
def spearman_invests( name, var1, var2 ):
    print(name + ":")
    rho, p_value = stats.spearmanr(df_invests[var1], df_invests[var2])
    print(f"Spearman ρ = {rho}, p = {p_value}")
    print("\n ---------- \n")

# Perform chi-square test on contingency table of two categorical variables
def chi_sq(name, var1, var2):
    print(name + ":\n")
    contingency_table = pd.crosstab(df[var1], df[var2])
    print(contingency_table, "\n")
    chi2, p, dof, expected = stats.chi2_contingency(contingency_table)
    print("Expected values:\n", expected, "\n")
    print(f"Chi-square = {chi2:.2f}, p-hodnota = {p:.3f}, Stupně volnosti = {dof}")
    print("\n ---------- \n")

# -------------------------------
# Section: Descriptive Statistics
# -------------------------------

# Print distributions and means of key variables
print("\n ------ GENERAL DESCRIPTION ------ \n")

basic_statistics_dist = ["age", "education", "income_range", "invests_periodically", "savings_range"]

for stat in basic_statistics_dist:
    dist = df[stat].value_counts(normalize = True) * 100
    printStatistic(stat + " distribution", dist)

# ------------------- #

basic_statistics_mean = ["household_members_gt13", "household_members_le13", "eq_hs_income"]

for stat in basic_statistics_mean:
    mean = df[stat].mean()
    printStatistic("mean " + stat, mean)

# ------------------- #

household_counts = df.groupby(["household_members_gt13", "household_members_le13"]).size().reset_index(name="count")
household_counts = household_counts.sort_values(by="count", ascending=False)
printStatistic("household counts", household_counts.head(5))

# -------------------------------
# Section: General Investment Behavior
# -------------------------------

# Count how often each investment instrument is used and plot results
print("\n ------ GENERAL INVESTMENT BEHAVIOR ------ \n")

for instrument in instrument_counts:
    instrument_counts[instrument] = df[instrument].sum()

df_instruments = pd.DataFrame(list(instrument_counts.items()), columns=['Instrument', 'Count'])
plt.figure(figsize=(10, 5))
plt.barh(df_instruments['Instrument'], df_instruments['Count'], color='gray')
plt.xlabel("Počet respondentů")
plt.ylabel("Investiční nástroj")
plt.title("Četnost investičních nástrojů mezi respondenty")
plt.gca().invert_yaxis()

# -------------------------------
# Section: Investment Decision Factors
# -------------------------------

# Run correlation and group tests on trust, rating, and skill self-evaluation
print("\n ------ FACTORS IMPACTING INVESTMENT DECISIONS ------ \n")

spearman_invests("rating x losses", "rating_of_investing", "has_encountered_losses")

spearman("frequency x skill rating", "investment_frequency","self_skill_rating")

#Mann-Whitney test for whether people investing in stocks deem themselves as differently skilled from those who do not
mann_whitney("skill x stock:", "instrument_stock", "self_skill_rating" )

spearman_invests("skill x rating", "self_skill_rating", "rating_of_investing")

spearman("trust x investment_frequency", "financial_instits_trust", "investment_frequency")

# -------------------------------
# Section: Risk Tolerance
# -------------------------------

# Mann-Whitney tests for each investment instrument vs. self-rated skill
print("\n ------ RISK TOLERANCE ------ \n")

#Create table of instruments and MW u test

results = []
for instrument in instrument_counts:
    second_var = "self_skill_rating"
    does_invest = df_invests[instrument].sum()
    does_not_invest = len(df) - does_invest
    group1 = df[df[instrument] == 1][second_var]
    group2 = df[df[instrument] == 0][second_var]
    u_stat, p_value = stats.mannwhitneyu(group1, group2, alternative="two-sided")
    mean1 = group1.mean()
    mean2 = group2.mean()
    results.append([instrument, does_invest, mean1, does_not_invest, mean2, u_stat, p_value])

df_results = pd.DataFrame(results, columns=["Instrument", "Investuje", "Mean investuje", "Neinvestuje","Mean neinvestuje", "U hodnota", "p hodnota"])
df_results = df_results.round(3)

fig, ax = plt.subplots(figsize=(8, 3))
ax.axis("tight")
ax.axis("off")

table = ax.table(cellText=df_results.values, 
                 colLabels=df_results.columns,
                 cellLoc="center",
                 loc="center")

table.auto_set_font_size(False)
table.set_fontsize(10)
table.auto_set_column_width([0, 1, 2, 3])

plt.savefig("table_output.png", dpi=300, bbox_inches="tight")


# -------------------------------
# Section: Investment Motivation
# -------------------------------

# Plot motivation counts and run relevant tests
print("\n ------ MOTIVATION ------ \n")

for reason in reason_counts:
    reason_counts[reason] = df[reason].sum()

df_reasons = pd.DataFrame(list(reason_counts.items()), columns=['Motivace', 'Pocet'])
plt.figure(figsize=(10, 5))
plt.barh(df_reasons['Motivace'], df_reasons['Pocet'], color='gray')
plt.xlabel("Počet respondentů")
plt.ylabel("Motivace")
plt.title("Četnost motivaci k investovani mezi respondenty")
plt.gca().invert_yaxis()

#Mann-Whitney testing for whether people with motivation of getting rich have different income than those who do not have such motivation
mann_whitney("get rich fast x income", "i_reasons_get_rich_fast", "avg_income")

chi_sq("Information from books x long term investing strategy", "info_source_books", "i_reasons_long_term_appr")

# Mann-Whitney for testing whether people with future precaution motivation have more kids
mann_whitney("future_precaution x kids", "i_reasons_future_precaution", "household_members_le13")

# -------------------------------
# Section: Investment Barriers
# -------------------------------

# Plot barrier counts and run emotional/risk-related tests
print("\n ------ BARRIERS ------ \n")

for barrier in barrier_counts:
    barrier_counts[barrier] = df[barrier].sum()

df_barriers = pd.DataFrame(list(barrier_counts.items()), columns=['Bariera', 'Pocet'])
plt.figure(figsize=(10, 5))
plt.barh(df_barriers['Bariera'], df_barriers['Pocet'], color='gray')
plt.xlabel("Počet respondentů")
plt.ylabel("Bariera")
plt.title("Četnost bariér pro investovani mezi respondenty")
plt.gca().invert_yaxis()

chi_sq("Emotions of fear x barriers losing money", "emotions_fear","i_barriers_fear_of_losing_money" )

# Mann-Whitney U test for testing correlation between fear emotion and investment frequency

# -------------------------------
# Section: Time and Knowledge Barriers
# -------------------------------

# Analyze how time consumption and knowledge influence behavior
mann_whitney("fear x investment", "emotions_fear", "investment_frequency")
mann_whitney("knowledge barrier x self investing strategy eval", "i_barriers_knowledge", "self_investing_strategy_eval")
mann_whitney("time consuming x self strategy eval", "is_investing_time_consuming", "self_investing_strategy_eval")
mann_whitney("time consuming x skill eval", "is_investing_time_consuming", "self_skill_rating")
mann_whitney("time consuming x investment frequency", "is_investing_time_consuming", "investment_frequency")

# -------------------------------
# Section: Social Influence
# -------------------------------

# Analyze effects of inspiration from social circle or influencers
mann_whitney("inspiration none x investment frequency", "inspiration_none", "investment_frequency")
mann_whitney("inspiration none x investment frequency", "info_source_consulting", "investment_frequency")
mann_whitney("inspiration none x investment frequency", "info_source_consulting", "self_skill_rating")
chi_sq("consulting x calmness", "emotions_calm", "info_source_consulting")

mann_whitney("i_reasons_hobby x risk_encounter frequency", "i_reasons_hobby", "risk_encounter_frequency")
chi_sq("motivation better than savings x motivation inflation protection", "i_reasons_better_than_savings", "i_reasons_inflation_protection")
chi_sq("motivation better than savings x inspiration celebrities", "i_reasons_better_than_savings", "inspiration_celebrities")
mann_whitney("i_reasons_inflation_protection x self_investing_strategy_eval", "i_reasons_inflation_protection", "self_investing_strategy_eval")

if plot : plt.show()