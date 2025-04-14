"""
Title: Investment Behavior Analysis - Data Cleaning Script
Author: Rene Kachyna, kacr03@vse.cz
Date: 14.4.2025

Description:
This script loads raw survey CSV data, applies cleaning and transformation,
adds derived variables, splits multi-choice questions, and outputs a cleaned dataset.

Required packages:
- pandas
- numpy
- os
"""

# === Data Preprocessing Script for Survey Dataset ===
# Author: Rene Kachyna, kacr03@vse.cz
# Description: This script loads raw survey CSV data, applies cleaning and transformation,
# adds derived variables, splits multi-choice questions, and outputs a cleaned dataset.

import pandas as pd
import os

# === Constants ===

# Median equalized income used to define middle-income households (OECD method)
EQUALIZED_INCOME_MEDIAN = 25968
MIDDLE_INCOME_LOWER_BOUND = 0.75
MIDDLE_INCOME_UPPER_BOUND = 2


# === Mapping Functions ===

# Maps income ranges (string) to average monthly values
def getAvgForIncomeRange(input):
    # Estimate midpoint values for income ranges
    if input == "< 20 000 Kč": return 10000
    if input == "20 000 Kč – 30 000 Kč": return 25000
    if input == "30 000 Kč – 40 000 Kč": return 35000
    if input == "40 000 Kč – 50 000 Kč": return 45000
    if input == "50 000 Kč – 70 000 Kč": return 60000
    if input == "70 000 Kč – 90 000 Kč": return 80000
    if input == "90 000 Kč – 120 000 Kč" : return 105000
    else: return 140000

# Maps savings range to estimated numeric value
def getAvgForSavingRange(input):
    if input == "Vytváříme deficit (výdaje znatelně převyšují příjmy)": return -1000
    if input == "Nespoříme (výdaje se přibližně rovnají příjmům, ± 500 Kč)": return 0
    if input == "500 až 1 000 Kč": return 750
    if input == "1000 až 3 000 Kč": return 2000
    if input == "3 000 až 5 000 Kč": return 4000
    if input == "5 000 až 7 000 Kč": return 6000
    else: return 9000

# Map frequency of investing into numeric scale
def investmentFrequencyMapping(input):
    if input == "Ano, pravidelně": return 2
    if input == "Ano, příležitostně": return 1
    else: return 0

# Map severity of past investment losses
def encounteredLossesMapping(input):
    if input == "Ano, výraznými": return 2
    if input == "Ano, menší ztráty": return 1
    else: return 0

# Maps subjective risk-taking behavior
def riskEncounterFrequencyMapping(input):
    if input == "Často (vyhledávám nové příležitosti, i když jsou rizikové)": return 3
    if input == "Občas (pokud mám pocit, že riziko stojí za to)": return 2
    if input == "Zřídka (jen pokud je to nezbytné)": return 1
    else: return 0

# Maps decision-making strategy for big financial decisions
def decisionStrategyMapping(input):
    if input == "Dělám rychlá rozhodnutí na základě prvních dojmů": return 3
    if input == "Rozhoduji se uvážlivě, ale nepotřebuji dlouhou dobu": return 1
    if input == "Zřídka (jen pokud je to nezbytné)": return 0
    else: return 2


# Maps tolerance towards risk into scale
def riskToleranceMapping(input):
    if input == "Rozhodně ano, jsem otevřený výzvám i riziku samotnému": return 3
    if input == "Občas ano, pokud věřím v potenciální přínosy": return 2
    if input == "Spíše ne, riskuji jen minimálně": return 1
    else: return 0

# === Utilities ===

# Expands a semicolon-delimited multiple-choice column into binary dummy variables
def splitMultipleChoice(mult_choice_col_name, dataframe):
    new_col_name = mult_choice_col_name + "_split"
    dataframe[new_col_name] = dataframe[mult_choice_col_name].str.split(";")
    exploded = dataframe.explode(new_col_name)
    dummies = pd.get_dummies(exploded[new_col_name])
    binary_matrix = dummies.groupby(dataframe["id"]).sum()
    return dataframe.merge(binary_matrix, left_on = "id", right_index = True )
    

# === Main Execution ===

# Ask user for full path to the file
file_path = input("Enter the full path to your CSV file:\n").strip()

# Check if the file exists
if not os.path.exists(file_path):
    print("File does not exist.")
    exit()

# Create backup in the same directory
directory, filename = os.path.split(file_path)
backup_path = os.path.join(directory, f"backup_{filename}")
os.popen(f"cp \"{file_path}\" \"{backup_path}\"")
print(f"Created a backup: {backup_path}")

# Load CSV
df = pd.read_csv(file_path, encoding='utf-8')
#Add unique respondent ID
df["id"] = df.index + 1

# === Cleaning and transformation ===

# Rename columns for easier handling
df.rename(columns=
    {"Časová značka" : "timestamp",
     "Spoříte část svých příjmů pravidelně?" : "invests_periodically",
     "Kolik vaše domácnost průměrně měsíčně uspoří?" : "savings_range",
     "Do jaké míry považujete spoření za důležitou část finančního plánování?" : "importance_of_savings",
     "Kde obvykle získáváte informace o správě osobních financí?" : "information_sources",
     "Ukládáte své úspory do nějakého finančního produktu nebo investičního nástroje?" : "investment_frequency",
     "Do jakých aktiv obvykle investujete?" : "investment_instrument",
     "Jaký je váš investiční horizont?" : "investment_planned_length",
     "Setkali jste se v minulosti s finančními ztrátami v důsledku investic, i kdyby jen dočasnými?" : "has_encountered_losses",
     "Jaké jsou vaše dosavadní zkušenosti s investováním?" : "rating_of_investing",
     "Jak často se ve svém životě pouštíte do aktivit, které zahrnují určité riziko?" : "risk_encounter_frequency",
     "Když se rozhodujete o velkých finančních výdajích, jaký přístup obvykle volíte?" : "decision_strategy",
     "Jste ochotni podstoupit riziko, pokud představuje možnost osobního růstu, profesního růstu nebo výdělku?" : "risk_tolerance",
     "Z jakých důvodů investujete, nebo byste investovat začali?" : "investment_reasons",
     "Do jaké míry se považujete za finančně gramotné?" : "self_skill_rating",
     "Myslíte si, že je investování časově náročné?" : "is_investing_time_consuming",
     "Jaké hlavní důvody vám brání v tom, abyste investovali více, nebo s investováním začali?" : "investment_barriers",
     "Jak dobré máte povědomí o investičních strategiích (např. pasivní vs aktivní)?" : "self_investing_strategy_eval",
     "Máte v okolí někoho, kdo vás inspiruje k investování nebo finančnímu plánování?" : "investment_inspiration",
     "Vnímáte obecně nedostatek finančního vzdělání jako překážku pro investování?" : "barrier_problem_rating",
     "Jaké emoce u vás převládají, když přemýšlíte o investování?" : "investment_emotions",
     "Jak velký vliv má obecná ekonomická situace (inflace, úrokové sazby) na vaše rozhodování ohledně správy prostředků?" : "economy_importance",
     "Do jaké míry máte důvěru ve finanční instituce (banky, investiční společnosti, fondy)?" : "financial_instits_trust",
     "Jaký je váš věk?" : "age",
     "Jaké je vaše nejvyšší dosažené vzdělání?" : "education",
     "Jaký je je obvykle čistý měsíční příjem vaší domácnosti (v Kč)?" : "income_range",
     "Kolik osob nad 13 let žije ve vaší domácnosti (včetně vás)?" : "household_members_gt13",
     "Kolik 13letých nebo mladších osob žije ve vaší domácnosti?" : "household_members_le13",
     "Jaký je váš hlavní pracovní status?" : "work_status",
     "Otevřená odpověď" : "open_commentary"
     },
    inplace = True)

# Fix known issues in value encoding
df["income_range"] = df["income_range"].replace("70 000 Kč – 120 000 Kč", "90 000 Kč – 120 000 Kč")
df["household_members_gt13"] = df["household_members_gt13"].replace(0, 1)

# Convert binary yes/no response into 0/1
df["is_investing_time_consuming"] = df["is_investing_time_consuming"].replace("Ano", 1)
df["is_investing_time_consuming"] = df["is_investing_time_consuming"].replace("Ne", 0)

# Add average numeric income/savings
df['avg_income'] = df['income_range'].apply(lambda x : getAvgForIncomeRange(x))
df['avg_savings'] = df['savings_range'].apply(lambda x : getAvgForSavingRange(x))

# Apply mappings to qualitative survey questions
df['investment_frequency'] = df['investment_frequency'].apply(lambda x : investmentFrequencyMapping(x))
df["has_encountered_losses"] = df["has_encountered_losses"].apply(lambda x : encounteredLossesMapping(x))
df["risk_encounter_frequency"] = df["risk_encounter_frequency"].apply(lambda x : riskEncounterFrequencyMapping(x))
df["decision_strategy"] = df["decision_strategy"].apply(lambda x : decisionStrategyMapping(x))
df["risk_tolerance"] = df["risk_tolerance"].apply(lambda x : riskToleranceMapping(x))

# Calculate consumption unit based on OECD method
df['cons_unit'] = df.apply( lambda row: 1 + 0.5 * ( row["household_members_gt13"] - 1 ) + 0.3 * ( row["household_members_le13"] ), axis = 1 )

# Calculate equalized household income
df['eq_hs_income'] = df.apply( lambda row: row['avg_income'] / row['cons_unit'], axis = 1 )

# Determine if household is middle-income according to OECD definition
df['is_middle_income'] = df['eq_hs_income'].apply(
    lambda x : 1 if x > MIDDLE_INCOME_LOWER_BOUND * EQUALIZED_INCOME_MEDIAN
        and x < 2 * MIDDLE_INCOME_UPPER_BOUND * EQUALIZED_INCOME_MEDIAN else 0 )


# Expand multiple choice responses into binary variables
for col in ["information_sources", "investment_instrument", "investment_reasons", "investment_barriers", "investment_inspiration", "investment_emotions"]:
    df = splitMultipleChoice(col, df)

# Rename all newly created dummy variables for clarity
df.rename(columns=
    {
        "Informace si nevyhledávám" : "info_source_none",
        "Od finančního poradce" : "info_source_consulting",
        "Od rodiny nebo přátel" : "info_source_family",
        "Z internetu (blogy, diskusní fóra, zpravodajství)" : "info_source_internet",
        "Z knih a odborných publikací" : "info_source_books",
        "Akcie" : "instrument_stock",
        "Dluhopisy" : "instrument_bonds",
        "Jiná aktiva" : "instrument_other",
        "Komodity" : "instrument_commodities",
        "Kryptoměny" : "instrument_crypto",
        "Nemovitosti" : "instrument_reality",
        "Podílové fondy" : "instrument_funds",
        "Spořící produkty (spořící účet, termínované vklady)" : "instrument_savings_account",
        "Dlouhodobé zhodnocování majetku" : "i_reasons_long_term_appr",
        "Doporučení od rodiny nebo přátel" : "i_reasons_recommend",
        "Investování mě zajímá" : "i_reasons_hobby",
        "Jiné_x" : "i_reasons_other",
        "Možnost získat vyšší výnosy než ze spoření" : "i_reasons_better_than_savings",
        "Ochrana před inflací" : "i_reasons_inflation_protection",
        "Rychlé zbohatnutí" : "i_reasons_get_rich_fast",
        "Zajištění do budoucnosti" : "i_reasons_future_precaution",
        "Jiné_y" : "i_barriers_other",
        "Nedostatek kapitálu k investování" : "i_barriers_capital",
        "Nedostatek znalostí o investování" : "i_barriers_knowledge",
        "Nedostatek času na sledování investic" : "i_barriers_time",
        "Nízká důvěra ve finanční trhy" : "i_barriers_trust",
        "Obecný nezájem o finance" : "i_barriers_not_caring",
        "Pocit, že je investování příliš složité" : "i_barriers_difficulty",
        "Strach ze ztráty peněz" : "i_barriers_fear_of_losing_money",
        "Žiju v přítomnosti a peníze si chci užít teď" : "i_barriers_enjoy_present",
        "Ano, mezi přáteli nebo kolegy" : "inspiration_friends",
        "Ano, sleduji inspirativní osobnosti" : "inspiration_celebrities",
        "Ano, v rodině" : "inspiration_family",
        "Ne, v mém okolí nikdo neinvestuje ani neplánuje" : "inspiration_none",
        "Důvěra a klid" : "emotions_calm",
        "Lhostejnost" : "emotions_dont_care",
        "Nadšení a zájem" : "emotions_excitement",
        "Skepticismus vůči finančním trhům" : "emotions_scepticism",
        "Strach a nejistota" : "emotions_fear"
     },
    inplace = True)

# Drop original text columns and intermediate _split columns
df = df.drop(columns = ["information_sources",
                        "investment_instrument",
                        "investment_reasons",
                        "investment_barriers",
                        "investment_inspiration",
                        "investment_emotions",
                        "information_sources_split",
                        "investment_instrument_split",
                        "investment_reasons_split",
                        "investment_barriers_split",
                        "investment_inspiration_split",
                        "investment_emotions_split",
                        "open_commentary"
                        ])

# Save cleaned data to new CSV, saved to the same directory as source file
output_path = os.path.join(os.path.dirname(file_path), "out.csv")
df.to_csv(output_path, index=False)
print(f"Data saved to {output_path}")
exit()