-- query1
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
    [Intensity(mm/hr)],
    [Depth(mm)],
    [Year],
    [Month],
    [Day]
FROM 
    [WDC].[NimrodReadings]
WHERE 
    [Easting] = {easting}
    AND [Northing] = {northing}
    AND CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE) BETWEEN '{start_date}' AND '{end_date}'
ORDER BY 
    CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE);

-- query3
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
    AND [DbAddr] = {DBAddr_AADV}
ORDER BY 
    CAST(CONCAT([Year], '-', [Month], '-', [Day]) AS DATE);

-- query4
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