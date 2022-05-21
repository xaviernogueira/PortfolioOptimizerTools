def run_DCF_valuation(self, eps: float, three_year_eps_growth: float, pe_ratios_outcomes: list = None,
                      historic_pe_ratios: list = None, time_horizon: int = 10,
                      decay_rate: float = 0.05) -> list:
    """

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

    return