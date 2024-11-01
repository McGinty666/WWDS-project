-- query0
SELECT [Source],
      [DB Addr],
      [DB Name],
       [Value Text],
	   [OS Name]
  FROM [DALReport].[TelexWasteAnalogues]
  WHERE [DB Name] LIKE '%{site_id}%'
UNION ALL
SELECT [Source],
      [DB Addr],
      [DB Name],
	  [Value Text],
	  [OS Name]
  FROM [DALReport].[TelexWaste2Analogues]
  WHERE [DB Name] LIKE '%{site_id}%'

-- query1
SELECT 
    [ReadingDate],
    [Easting],
    [Northing],
    [Intensity(mm/hr)],
    [Depth(mm)],
    [Year],
    [Month],
    [Day]
FROM 
    [WDC].[NimrodReadings]
WHERE 
    [Easting] BETWEEN '{min_easting}' AND '{max_easting}' - 1
    AND [Northing] BETWEEN '{min_northing}' AND '{max_northing}' - 1
    AND CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE) BETWEEN '{start_date}' AND '{end_date}'
ORDER BY 
    CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE);

-- query2
SELECT 
    [TimeGMT],
    [date],
    [SourceSystemId],
    [DbAddr],
    [DbName],
    [EValue],
    [Year],
    [Month],
    [Day]
FROM 
    [dbo].[AnaloguesView]
WHERE 
    CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE) BETWEEN '{start_date}' AND '{end_date}'
    AND [DbAddr] = {DBAddr_sump}
    AND [Sourcesystem] = '{SourceSystem_sump}'
ORDER BY 
    [TimeGMT]

-- query3
SELECT  
    [Hour],
    [DbAddr],
    [count],
    ROUND([mean_EValue], 2) AS [meanEValue],
    [stddev_EValue],
    [Year],
    [Month],
    [Day]
FROM 
    [dbo].[AnaloguesAggregatedHourlyView]
WHERE 
    [SourceSystem] = '{sourcesystem_flow_meter}'
    AND [DbAddr] = '{DBAddr_flow_meter}'
    AND CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE) BETWEEN '{start_date}' AND '{end_date}'
ORDER BY 
    [Year], [Month], [Day], [Hour];

-- query4
SELECT
    [DbAddr],
    [mean_EValue],
    [min_EValue],
    [max_EValue],
    [98percentile],
    [Variance],
    [SourceSystem],
    [Year],
    [Month],
    [Day]
FROM 
    [dbo].[AnaloguesAggregatedDailyView]
WHERE 
    CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE) BETWEEN '{start_date}' AND '{end_date}'
    AND [DbAddr] = {DBAddr_sump}
    AND [Sourcesystem] = '{SourceSystem_sump}'
ORDER BY 
    CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE);

-- query5
SELECT 
    [TimeGMT],
    [date],
    [SourceSystemId],
    [DbAddr],
    [DbName],
    [EValue],
    [Year],
    [Month],
    [Day]
FROM 
    [dbo].[AnaloguesView]
WHERE 
    CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE) BETWEEN '{start_date}' AND '{end_date}'
    AND [DbAddr] = {DBAddr_flow_meter}
    AND [Sourcesystem] = '{sourcesystem_flow_meter}'
ORDER BY 
    [TimeGMT]

-- query6
SELECT
    [DbAddr],
    [mean_EValue],
    [min_EValue],
    [max_EValue],
    [98percentile],
    [Variance],
    [SourceSystem],
    [Year],
    [Month],
    [Day]
FROM 
    [dbo].[AnaloguesAggregatedDailyView]
WHERE 
    CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE) BETWEEN '{start_date_screen}' AND '{end_date_screen}'
    AND [DbAddr] = {DBAddr_sump}
    AND [Sourcesystem] = '{SourceSystem_sump}'
	AND [98percentile] > '{spill_level}'
	AND [5percentile] < '{on_level}'
ORDER BY 
    CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE);

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