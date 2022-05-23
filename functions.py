import numpy as np


def run_DCF_valuation(self, eps: float, three_year_eps_growth: float, decay_rate: float, pe_ratios_outcomes: list = None,
                      historic_pe_ratios: list = None, time_horizon: int = 10) -> list:
    """
    Runs a discounted cash flow analysis using earnings per share, resulting in a low, middle, and high share prices
    :param eps: current earning per share
    :param three_year_eps_growth: an estimate YoY% EPS growth rate for the next three years
    :param pe_ratios_outcomes: a list of three terminal pe ratios [low, middle, high]
    :param historic_pe_ratios: (optional) a list of historic pe ratios, if provided, outcome pe ratios will be
    estimated using the range of historic values.
    :param time_horizon: default is 10. The time horizon to conduct the DCF for.
    :param decay_rate: after the first three years, this becomes the second derivative of EPS YoY growth.
    :return: a list with [low, middle, high] value estimates for each
    """
    discount_rate = self.discount_rate

    if not historic_pe_ratios:
        pe_scenarios = pe_ratios_outcomes.sort()
    else:
        pes = np.array(historic_pe_ratios)
        mean_pe = np.mean(pes)
        std_pe = np.std(pes)
        pe_scenarios = [mean_pe - std_pe, mean_pe, mean_pe + std_pe]

    # Calculate intrinsic value for each scenario
    values = []  # Stores the value for each scenario

    for i, scene in enumerate(pe_scenarios):
        future_flow = []  # Stores the estimate future cash flows for each scenario
        future_pv = []  # Stores estimate PV values for each scenario

        term_pe = pe_scenarios[i]

        for j, t in enumerate(range(0, time_horizon)):
            if j <= 3:
                rate = three_year_eps_growth
            else:
                rate = rate - (rate * decay_rate)

            if j == 0:
                future_val = eps * (1 + (rate / 100))

            else:
                future_val = future_flow[j - 1] * (1 + (rate / 100))

            future_flow.append(future_val)

            exp = -t - 1
            pv = future_val * ((1 + discount_rate) ** exp)
            future_pv.append(pv)

        terminal_value = future_flow[-1] * term_pe
        term_pv = terminal_value * ((1 + discount_rate) ** exp)
        future_pv.append(term_pv)

        values.append(sum(future_pv))

    return values
