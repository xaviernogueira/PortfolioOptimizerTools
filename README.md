# PortfolioOptimizerTools
This repository aims to provide open-source access to a small suite of investment porfolio inflow optimization. The classes and functions are defined as such to be able to handle time series inputs, and therefore allocate capital real-time, however here we demo using historic data.

## Portfolio managment approach
The original idea for this repository was to automate logic that I have pfeviously applied manually to manage my own finances.

## Method overview
The tool calculates a discounted cash flow valuation using user-provided growth assumptions, terminal multiple scenarios, and risk-based discount ratwe (default is 12.5%). With valuations stored for the portfolio, the current prices at a given time step are compared with both the valuation to estimate Y year ROIC, as well as the porfolios current position basin values to estimate the most effective allocation of new capital.

 To avoid only investing in one thing, we build in the option to use two main types of portfolio balance equations:
 * Correlation minimizer - uses historic price data to calculate the correlation between each stock, and can push the optimizer to avoid an overly correlated portfolio.
 * Position-evener - uses the standard deviation of the top N largest positions to avoid growing one position too large.

## DCF Inputs
For all companies in the porfolio, the following must be provided.
* Current share price
* Current Earnings Per Share (EPS)
* Estimated next-3-year average YoY earnings growth
* PE data: either a list with an estimate low, medium, and high PE OR a list of any length with historic PE values (used to estimate typical values)
* Optional: Discount rate - default is 12%. One may raise the rate for additional risk concerns (i.e., low moat, regulatory ris, etc.).
* `conservativeness` = (0 - 1, default is 0.5), this is a parameter used that weights terminal PE range probabilities and also governs the earnings growth decay rate.

## Optimization parameters
At each time step where a porfolio contribution is provided, a custom optimizer equation finds the ideal allocation %s based on both maximizing DCF estimated long term returns, but also acheiving porfolio balance (and avoiding over-correlation is historic price time series data is provided).

There are two parameters used to govern the weight placed on the balancer equations.
* **balance_eq** = `1 / (np.std(np.array(sort(position_sizes)[-3:]))**2)`
    * The weight placed on the balance coef in the optimizer is `gamma` and ranges between (0 and 1). At 1, avoiding position oversizing is treated as equally desirable as optimizing returns.
* **correlation_eq** = Method TBD

## See our optimizer demo in the `optimizer_demo.ipynb` Jupyter notebook. 
All data from the demo was either manually transcribed or downloaded from Yahoo Finances "Historical Data" tab for the trailing 5-year time period. 