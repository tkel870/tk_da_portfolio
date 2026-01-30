CREATE TABLE Exploration_Project.homelessness AS
SELECT 
  CoC_Number, 
  LEFT(CoC_Number, 2) AS State, 
  CoC_Name, 
  Overall_Homeless, 
  Sheltered_ES_Homeless, 
  Sheltered_TH_Homeless, 
  Sheltered_SH_Homeless, 
  Sheltered_Total_Homeless, 
  Unsheltered_Homeless, 
  Homeless_Individuals, 
  Homeless_People_in_Families, 
  Chronically_Homeless, 
  Homeless_Veterans, 
  Homeless_Unaccompanied_Youth_Under_18, 
  Count_Year
FROM `bigquery-public-data.sdoh_hud_pit_homelessness.hud_pit_by_coc`;
