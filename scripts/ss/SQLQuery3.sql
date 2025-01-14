SELECT TOP (100) [DbAddr]
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
	  ,CONCAT([Year], '-', [Month], '-', [Day]) AS [spill_days]
  FROM [dbo].[AnaloguesAggregatedDailyView]
  WHERE [DBAddr] = '11943'
  AND [Year] = '2024'
  AND [95percentile] > 95