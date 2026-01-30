# BigQuery Homelessness Data Exploration – Part 2

## Project Context
Part 2 builds on the cleaned and prepared homelessness table created in Part 1.
The goal of this analysis is to answer policy- and program-focused questions
using SQL queries executed in BigQuery.

---

## Question 1: Unaccompanied Homeless Youth (2018)

**Question:**  
Which three Continuum of Care (CoC) areas had the highest number of unaccompanied
homeless youth under age 18 in 2018?

**Approach:**  
- Filtered the dataset to include only records from 2018  
- Grouped results by Continuum of Care name  
- Summed the number of unaccompanied homeless youth under 18  
- Sorted results in descending order and selected the top three  

**Answer:**  
1. San Jose/Santa Clara City & County CoC — 506  
2. Oregon Balance of State CoC — 243  
3. Las Vegas/Clark County CoC — 214  

**SQL used:** see `part2.sql`

---

## Question 2: Unsheltered Homeless Trend in Delaware

**Question:**  
Has the number of unsheltered homeless individuals in Delaware increased over the
past seven years?

**Answer:**  
Yes. While there was a decrease between 2012 and 2013, the total number of
unsheltered homeless individuals increased steadily from 2014 through 2018,
rising from 37 to 93. This indicates an overall upward trend.

**SQL used:** see `part2.sql`

---

## Question 3: Safe Haven Sheltered Homeless (2018)

**Question 3a:**  
In 2018, how many different locations had at least one person sheltered in a Safe
Haven program?

**Answer:**  
In 2018, 90 different Continuum of Care locations reported at least one individual
sheltered in a Safe Haven program.

**Question 3b:**  
What were the top three locations by number of individuals sheltered in Safe
Haven programs in 2018?

**Answer:**  
- Philadelphia CoC — 235  
- Reno, Sparks/Washoe County CoC — 185  
- Indianapolis CoC — 68  

**SQL used:** see `part2.sql`

---

## Question 4: Top States by Overall Homeless Population (2018)

**Question:**  
What were the top seven states by overall homeless population in 2018?

**Answer:**  
- California (CA) — 129,972  
- New York (NY) — 91,897  
- Florida (FL) — 31,030  
- Texas (TX) — 25,310  
- Washington (WA) — 22,304  
- Massachusetts (MA) — 20,068  
- Oregon (OR) — 14,476  

**SQL used:** see `part2.sql`

---

## Question 5: Population vs. Homelessness Comparison

**Question:**  
Do the top states for total population align with the top states for overall
homelessness?

**Answer:**  
No. While California and New York rank highly in both population and homelessness,
states such as Washington, Massachusetts, and Oregon rank significantly higher in
homelessness than they do in total population.

**Overrepresented states for homelessness:**  
- Washington (WA)  
- Massachusetts (MA)  
- Oregon (OR)

---

## Question 6: Effective Shelter Provision (2018)

**Question:**  
Which locations had more than 1,000 overall homeless individuals but fewer than
100 unsheltered individuals in 2018?

**Answer:**  
Multiple locations met this criteria, indicating comparatively strong shelter
provision.

From this group, the locations where unsheltered individuals accounted for less
than 2% of the overall homeless population were:

- Springfield/Hampden County CoC (~1.31%)  
- Nassau, Suffolk Counties CoC (~1.34%)  

**SQL used:** see `part2.sql`

---

## Key Skills Demonstrated
- Writing complex SQL queries
- Aggregation and filtering
- Trend analysis over time
- Translating policy questions into analytical logic
