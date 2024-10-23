-- query7
WITH SpillDays AS (
    SELECT DISTINCT 
        CONCAT([Year], '-', [Month], '-', [Day]) AS [spill_days]
    FROM [dbo].[AnaloguesAggregatedDailyView]
    WHERE [DBAddr] = '{DBAddr_sump}'
      AND [98percentile] > '{spill_level}'
	  AND CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE) BETWEEN '{start_date_spill_query}' AND '{end_date_spill_query}'
)
SELECT 
      [Hour],
      [DbAddr],
      [count],
      [mean_EValue],
      [stddev_EValue],
      [min_EValue],
      [max_EValue],
      [5percentile],
      [50percentile],
      [95percentile],
      [CountofOutOfDate],
      [CountofOutOfRange],
      [CountofSuspect],
      [SourceSystem],
      [Year],
      [Month],
      [Day],
      CONCAT([Year], '-', [Month], '-', [Day], '-', [Hour]) AS [spill_hours] 
  FROM [dbo].[AnaloguesAggregatedHourlyView]
  WHERE [DBAddr] = '{DBAddr_sump}'
    AND [50percentile] > {spill_level}
    AND CONCAT([Year], '-', [Month], '-', [Day]) IN (SELECT [spill_days] FROM SpillDays)	
ORDER BY CONCAT([Year], '-', [Month], '-', [Day], '-', [Hour])