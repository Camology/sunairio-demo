import pandas as pd

# Read the data in
df = pd.read_csv('load_sims_full_stack_202412.csv', index_col=0)
df.index = pd.to_datetime(df.index.values, utc=True)
#timezone info was causing grief for D3
df = df.tz_localize(None)

#print all designated percentiles, can add more and update the other script as needed
percentiles = [0.25, 0.50, 0.75, 0.99]

index_header = 'datetime'
value_header = ['value']

for percentile in percentiles:
    hourly_df = df.quantile(percentile, axis=1)
    hourly_df.to_csv('hourly_data_%sP.csv' % percentile, header=value_header, index=True, index_label=index_header)

    daily_min_df = df.resample('D').min().quantile(percentile, axis=1)
    daily_min_df.to_csv('daily_min_%s.csv' % percentile, header=value_header, index=True, index_label=index_header)

    monthly_min_df = df.resample('D').min().quantile(percentile, axis=1)
    monthly_min_df.to_csv('monthly_min_%s.csv' % percentile, header=value_header, index=True, index_label=index_header)

    daily_max_df = df.resample('D').max().quantile(percentile, axis=1)
    daily_max_df.to_csv('daily_max_%s.csv' % percentile, header=value_header, index=True, index_label=index_header)

    monthly_max_df = df.resample('D').max().quantile(percentile, axis=1)
    monthly_max_df.to_csv('monthly_max_%s.csv' % percentile, header=value_header, index=True, index_label=index_header)

    daily_mean_df = df.resample('D').mean().quantile(percentile, axis=1)
    daily_mean_df.to_csv('daily_mean_%s.csv' % percentile, header=value_header, index=True, index_label=index_header)

    monthly_mean_df = df.resample('D').mean().quantile(percentile, axis=1)
    monthly_mean_df.to_csv('monthly_mean_%s.csv' % percentile, header=value_header, index=True, index_label=index_header)