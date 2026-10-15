---
name: statsmodels-ols-arima-seasonal-decompose
description: 'Practical guide for statsmodels: OLS from 2D array or filtered DataFrame, formula API for polynomial regression, ARIMA, seasonal_decompose, adfuller.'
---

# statsmodels — OLS, ARIMA, Seasonal Decompose, and ADF Test

## OLS: Building from a 2D Input

When the input is a 2D array or list, construct the DataFrame first, then slice into predictors and response:

```python
import statsmodels.api as sm
import pandas as pd

COLUMNS = ["A", "B", "C", "D", "Response"]

df = pd.DataFrame(records, columns=COLUMNS)
X = df[COLUMNS[:-1]]          # all predictor columns
y = df["Response"]
X = sm.add_constant(X)        # adds 'const'; required for intercept
model = sm.OLS(y, X)
results = model.fit()
return df, results
```

`sm.add_constant` mutates a **copy** of X; reassign to capture it. The result object has `.params`, `.rsquared`, `.pvalues`, `.fittedvalues`.

---

## OLS: Filtering from an Existing DataFrame

When predictors and response come from a pre-existing DataFrame, filter both from the same slice:

```python
filtered = df[(df[columns[1]] > height) & (df[columns[2]] < weight)]
if filtered.empty:
    return None

y = filtered[columns[0]]
X = filtered[columns[1:]]
X = sm.add_constant(X)
results = sm.OLS(y, X).fit()
return results
```

If `y` comes from the original DataFrame and `X` from a filtered slice, statsmodels raises `ValueError: The indices for endog and exog are not aligned`.

---

## OLS: Formula API (`statsmodels.formula.api`)

For polynomial regression on computed quantities, the dict key must exactly match the variable name in the formula string:

```python
from statsmodels.formula.api import ols
import numpy as np

# Histogram, then convert bin edges to centers before OLS
fig, ax = plt.subplots()
count, bins, _ = ax.hist(samples, num_bins, density=True)
ax.plot(bins, 1/(sigma * np.sqrt(2*np.pi)) * np.exp(-(bins-mu)**2/(2*sigma**2)),
        linewidth=2, color='r')

bins = (bins[:-1] + bins[1:]) / 2    # num_bins centers, not num_bins+1 edges
model = ols('count ~ bins + np.power(bins, 2)',
            data={'count': count, 'bins': bins}).fit()
ax.plot(bins,
        model.params['Intercept']
        + model.params['bins'] * bins
        + model.params['np.power(bins, 2)'] * np.power(bins, 2),
        linewidth=2, color='g')
return ax
```

---

## ARIMA Forecast

```python
from statsmodels.tsa.arima.model import ARIMA

model = ARIMA(df['closing_price'], order=(5, 1, 0))
model_fit = model.fit()
forecast = model_fit.forecast(steps=7)   # returns pandas Series
return forecast.tolist(), ax             # .tolist() when List[float] is required
```

Access the time series by its actual column name as given in the input. Do not add column-existence guards unless the task explicitly requires them — they change which exception propagates.

---

## Seasonal Decompose

### From a generated or computed series

```python
from statsmodels.tsa.seasonal import seasonal_decompose

date_range = pd.date_range(start=start_date, periods=periods, freq=freq)
data = np.random.randint(low=100, high=500, size=periods)
series = pd.Series(data, index=date_range)
try:
    decomposition = seasonal_decompose(
        series, model=model,
        period=12 if freq == 'M' else 4   # monthly→12, quarterly→4
    )
except ValueError as e:
    return {'error': str(e)}

return {
    'trend': decomposition.trend,
    'seasonal': decomposition.seasonal,
    'residual': decomposition.resid,    # attribute is .resid, not .residuals
}
```

### From a DataFrame with a date column

```python
df = df.set_index('date')
df = df.asfreq(freq, method='pad')      # pad fills gaps with last valid value
df['value'] = pd.to_numeric(df['value'], errors='coerce')
decomposition = seasonal_decompose(df['value'], model=decomp_model)
result = decomposition        # DecomposeResult object
ax = df.plot(y='value')
return result, ax
```

Omitting `period` lets statsmodels infer it from the DatetimeIndex frequency. Passing `period=freq` (a string) raises `TypeError: '<' not supported between instances of 'int' and 'str'`.

---

## Augmented Dickey-Fuller Test

```python
from statsmodels.tsa.stattools import adfuller

result = adfuller(series)
p_value = result[1]          # index 1 is the p-value
is_stationary = p_value <= 0.05
```

`adfuller` returns a tuple: `(adf_statistic, p_value, n_lags, n_obs, critical_values_dict, ...)`. A series with constant values (zero variance) can be treated as stationary without running the test.
