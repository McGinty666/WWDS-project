-- query1
SELECT  
    [Hour],
    [DbAddr],
    [count],
    ROUND([mean_EValue], 2) AS [meanEValue],
    [stddev_EValue],
    --[min_EValue],
    --[max_EValue],
    --[5percentile],
    --[50percentile],
    --[95percentile],
    --[CountofOutOfDate],
    --[CountofOutOfRange],
    --[CountofSuspect],
    --[SourceSystem],
    [Year],
    [Month],
    [Day]
FROM 
    [dbo].[AnaloguesAggregatedHourlyView]
WHERE 
    [SourceSystem] = 'Waste'
    AND [DbAddr] = '{DBAddr_AAHV}'
    AND [Year] = 2024
    AND [Month] = 01
    AND [Day] BETWEEN 22 AND 25
ORDER BY 
    [Year], [Month], [Day], [Hour];

-- query2
SELECT 
    [ReadingDate],
    [Easting],
    [Northing],
    [Intensity],
    [Intensity(mm/hr)],
    [Depth],
    [Depth(mm)],
    [IssuedDate],
    [Year],
    [Month],
    [Day]
FROM 
    [WDC].[NimrodReadings]
WHERE 
    [Easting] = {easting}
    AND [Northing] = {northing}
    AND [ReadingDate] BETWEEN '{start_date}' AND '{end_date}'
ORDER BY 
    [ReadingDate];

--query3
SELECT
	[DbAddr]
      ,[count]
      ,[mean_EValue]
      ,[stddev_EValue]
      ,[min_EValue]
      ,[max_EValue]
      ,[5percentile]
      ,[50percentile]
      ,[95percentile]
      ,[98percentile]
      ,[Variance]
      ,[CountofOutOfDate]
      ,[CountofOutOfRange]
      ,[CountofSuspect]
      ,[SourceSystem]
      ,[Year]
      ,[Month]
      ,[Day]
  FROM [dbo].[AnaloguesAggregatedDailyView]
  WHERE CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE) BETWEEN {start_date} AND {end_date}
  AND [DbAddr] = {DBAddr_AADV}
  ORDER BY CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE)

--query4
SELECT 
      ,[TimeGMT]
      ,[date]
      ,[SourceSystemId]
      ,[DbAddr]
      ,[DbName]
      ,[EValue]
     --,[OutOfDate]
     --,[OutOfRange]
     -- ,[Suspect]
     --,[Flag4]
     -- ,[Flag5]
     -- ,[Flag6]
     -- ,[Flag7]
     -- ,[Flag8]
     --,[Flag9]
     -- ,[Flag10]
     -- ,[Flag11]
     -- ,[Flag12]
     --,[Flag13]
     -- ,[Flag14]
     -- ,[Flag15]
     --,[DbSource]
     -- ,[AlarmStatus]
     --,[AlarmLevel]
     -- ,[AreaNumber]
     -- ,[ElementDependantValue]
     -- ,[AlarmCategory]
     -- ,[Id]
     -- ,[EPOCH]
     -- ,[SourceSystem]
      ,[Year]
      ,[Month]
      ,[Day]
  FROM [dbo].[AnaloguesView]
  WHERE CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE) BETWEEN {start_date} AND {end_date}
  AND [DbAddr] = {DBAddr_AADV}
  ORDER BY CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE)





