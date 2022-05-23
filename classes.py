from functions import *


class Position:
    """
    A class that contains, and tracks changes to, a given stock position.
    The following user facing class functions are defined:
    - Position.add_base_position(shares: float or int, average_price: float or int): initiates an a stock position
    - Position.make_a_buy(shares: float or int, average_price: float or int) adds a buy to the current position
    - Position.run_dcf_valuation(eps: float, three_year_eps_growth: float, pe_ratios_outcomes: list = None,
                          historic_pe_ratios: list = None): runs a DCF valuation and updates self.valuations
    """

    def __init__(self, ticker: str = None, current_price: float = None):
        if not ticker:
            self.ticker = None
            print('WARNING: Empty position class initiated, please provide a ticker in the')
        else:
            # store ticker name
            self.ticker = str(ticker).capitalize()

            # store number of shares and purchases
            self.shares = 0
            self.invested = 0

            self.purchases = []  # a list of purchase amounts in shares (int or float)
            self.purchase_prices = []  # a list of the same length as self.purchase that stores the price at each buy
            self.average_price = None

            # store price data
            if not current_price:
                self.current_price = current_price
                self.equity = self.current_price * self.shares
                self.profit_loss = self.invested - self.equity
            else:
                self.equity = None
                self.profit_loss = None

            # store attributes for DCF
            self.discount_rate = 0.125  # default discount rate
            self.valuations = None  # when calculated this stores [low, middle, high]
            self.decay_rate = 0.05

    # #### KEY USER METHODS #####
    # define a function to initiate a positions with a starting share balance
    def add_base_position(self, shares: float or int, average_price: float or int):
        if shares == 0:
            self.shares = shares
            self.invested = shares * average_price
            self.purchases = [shares]
            self.purchase_prices = [average_price]
            self._update_average_price()

            if isinstance(self.current_price, float):
                self._update_equity()

        else:
            return print('ERROR: You are trying to initialize a position in {} that already exists!')

    # define a function to make buy trades
    def make_a_buy(self, shares, average_price):
        self.shares += shares
        self.invested += (shares * average_price)
        self.purchases.append(shares)
        self.purchase_prices.append(average_price)
        self._update_average_price()

        if isinstance(self.current_price, float):
            self._update_equity()

    # main internal DCF function, how the DCF results are used/interpreted is controlled by the portfolio object
    def run_dcf_valuation(self, eps: float, three_year_eps_growth: float, pe_ratios_outcomes: list = None,
                          historic_pe_ratios: list = None):
        if not historic_pe_ratios:
            self.valuations = run_DCF_valuation(eps, three_year_eps_growth, self.decay_rate,
                                                pe_ratios_outcomes=pe_ratios_outcomes)
        else:
            self.valuations = run_DCF_valuation(eps, three_year_eps_growth, self.decay_rate,
                                                historic_pe_ratios=historic_pe_ratios)

        return self.valuations

    # #### INTERNAL METHODS - using individually may cause issues #####
    def _update_decay_rate(self, new_decay_rate):
        self.decay_rate = new_decay_rate

    def _update_discount_rate(self, updated_discount_rate: float):
        self.discount_rate = updated_discount_rate

    def _update_current_price(self, new_price):
        self.current_price = new_price

        # if we own shares, update our equity and profit attributes
        if self.shares > 0:
            self._update_equity()

    def _update_average_price(self):
        self.average_price = self.invested / self.shares

    def _update_equity(self):
        self.equity = self.current_price * self.shares
        self.profit_loss = self.invested - self.equity


class Portfolio:

    def __init__(self, positions_dict: dict = None):
        """
        An instance of this Portfolio class is largely to store active positions, and update them all simultaneously.
        :param positions_dict: a dictionary with ticker names as keys storing [# of shares, average price]
        """
        self.positions = {}
        self.tickers = []
        self.conservativeness = 0.5  # default is 0.5, but can range from 0 (no conservativeness) to 1 (max)
        self.greed = 0.5  # default is 0.5, but can range from 0 to 1. A higher value more strongly weights stock returns.
        self.gamma = 0.2

        if isinstance(positions_dict, dict):
            for tick in list(positions_dict.keys()):
                shares, price = positions_dict[tick]
                self.positions[tick] = Position(ticker=tick)
                self.positions[tick].add_base_position(shares, price)
                self.tickers.append(tick)
                print(f'Initialized a position in ticker {tick}, with {shares} shares at an average price of {price}')

        # initialize dictionary to hold portfolio balance values
        self.raw_valuations = {}  # stores raw DCF expected return values for each position
        self.expected_returns = {}  # stores the expected return if the price returns to intrinsic value
        self.greedy_returns = {}
        self.balance_scores = {}
        self.overbalance_scores = {}  # will be zero unless a balance eq is used

    # #### METHODS TO GET INFORMATION FROM THE PORTOFLIO #####
    def get_tickers(self):
        return list(self.positions.keys())

    def get_current_equity(self):
        balance = 0
        tickers = self.get_tickers()
        sub_tickers = []
        for tick in tickers:
            position = self.positions[tick]
            if isinstance(position.equity, float or int):
                balance += position.equity
            else:
                print(f'No current price provided for ticker {tick}, please call '
                      f'Portfolio.update_current_prices({tick}: [# of shares, average price]) to provide values')
        return balance

    def get_position_sizes(self):
        tickers = self.get_tickers()
        positions_info_dict = {}
        for tick in tickers:
            positions_info_dict[tick] = {}

    def verify_valuations(self) -> dict:
        """
        Used to check which positions in the portfolio have had completed DCF valuations
        :return:
        """
        valuations_dict = {}
        for tick in self.get_tickers():
            position = self.positions[tick]
            if not position.valuations:
                valuations_dict[tick] = 'No DCF valuation completed'
            else:
                low, mid, high = position.valuations
                valuations_dict[tick] = f'DCF completed: low={low}, middle={mid}, high={high}'
        return valuations_dict

    def calculate_current_allocations(self) -> dict:
        """
        Uses current prices to calculate what % of the portfolio value is associated with each position
        :return: a dictionary with tickers and their relative proportion
        """
        return

    def get_optimal_allocations(self, current_prices_dict: dict = None, gamma: float = 0.05, greed: float = None,
                                conservativeness: float = None):
        """

        :param current_prices_dict:
        :param gamma: controls the weighting of the rebalanced coefficient in optimization
        :param greed: (optional) allows a greed value (float 0 - 1) that differs from the Portfolios setting to be used
        :return:
        """
        # if current_prices_dict is provided, update prices
        tickers = self.get_tickers()
        if isinstance(current_prices_dict, dict):
            self.update_current_prices(current_prices_dict)

        # use custom parameters is input
        if not gamma:
            gamma = self.gamma
        if not greed:
            greed = self.greed

        if not conservativeness:
            conservativeness = self.conservativeness

        # update expected returns
        self.calculate_expected_roic(new_conservativeness=conservativeness)

        # add greed re-weighting
        greed_exponent = get_greed_exponent(greed)
        self.add_greed_weights(greed_exponent)

        # create portfolio_balancer weights
        self.add_portolio_balancer(gamma)

        # calculate optimal allocation
        balanced_values = []
        for tick in tickers:
            balanced_values.append(self.greedy_returns[tick] * (1 + self.balance_scores[tick]))

        balance_sum = sum(balanced_values)

        optimal_allocations = {}
        for i, tick in enumerate(tickers):
            optimal_allocations[tick] = balanced_values[i] / balance_sum

        return optimal_allocations

    # #### METHODS TO UPDATE PORTFOLIO VALUES OR POSITIONS #####
    def update_conservativeness(self, new_conservativeness: float):
        warning = False
        if isinstance(new_conservativeness, float):
            if 0 < new_conservativeness < 1:
                old_conservativeness = float(self.conservativeness)
                self.conservativeness = new_conservativeness
                return print(
                    f'SUCCESS: conservativeness updated from {old_conservativeness} to {self.conservativeness}')
            else:
                warning = True
        else:
            warning = True

        if warning:
            return print('WARNING: new_conservativeness parameter must be a floating point number between 0 - 1. '
                         'Could not update value')

    def update_greed(self, new_greed: float):
        warning = False
        if isinstance(new_greed, float):
            if 0 < new_greed < 1:
                old_conservativeness = float(self.conservativeness)
                self.conservativeness = new_greed
                return print(
                    f'SUCCESS: conservativeness updated from {old_conservativeness} to {self.conservativeness}')
            else:
                warning = True
        else:
            warning = True

        if warning:
            return print('WARNING: new_greed parameter must be a floating point number between 0 - 1. '
                         'Could not update value')

    def open_new_positions(self, new_positions_dict: dict):
        """
        Allows new positions to be initiated with a dictionary
        :param new_positions_dict: a dictionary where {'TICKER': [# of shares, average price]} OR a Positions class
        """
        if isinstance(new_positions_dict, dict):
            for tick in list(new_positions_dict.keys()):
                if tick not in self.tickers:
                    shares, price = new_positions_dict[tick]
                    self.positions[tick] = Position(ticker=tick)
                    self.positions[tick].add_base_position(shares, price)
                    self.tickers.append(tick)
                    print(
                        f'Initialized a position in ticker {tick}, with {shares} shares at an average price of {price}')
                else:
                    print(f'Cant make new position in {tick} because on already exists '
                          f'with {self.positions[tick].shares} shares')

    def add_position_class_instance(self, new_position):
        if isinstance(new_position, Position):
            tick = new_position.ticker
            self.positions[tick] = new_position
            self.tickers.append(tick)
        else:
            return print('WARNING: Must provide initated Position object. To add positions with a dictionary use the '
                         'Portfolio.open_new_positions(new_position_dicts)')

    def update_current_prices(self, current_prices_dict: dict = None):
        """
        Allows each positions current price to be updated
        :param current_prices_dict: a dictionary with ticker strings as keys, and new
        :return:
        """
        tickers = self.get_tickers()
        if isinstance(current_prices_dict, dict):
            for tick in tickers:
                position = self.positions[tick]

                if tick in list(current_prices_dict.keys()):
                    current_price = current_prices_dict[tick]
                    position._update_current_price(current_price)
                else:
                    print(f'Could not update current price for stock {tick}')

    def run_batch_dcf(self, dcf_dict, historic_data: bool = False):
        """
        Allows a DCF analyses to be ran for multiple positions by referencing their tickers
        :param dcf_dict: a dictionary where {'TICK': current EPS, three year EPS growth rate: float, pe_ratios: list]
        :param historic_data: default is false, if true or is >3 pe ratios are provided, the pe ratios are viewed as
        historic and low,mid,high scenarios are defined via standard deviations instead of explictly.
        :return: updates each positions valuation attributes
        """
        for dcf_tick in list(dcf_dict.keys()):
            if dcf_tick in self.get_tickers():
                eps, eps_growth, pe_ratios = dcf_dict[dcf_tick]
                position = self.positions[dcf_tick]

                if isinstance(pe_ratios, list):
                    if not historic_data and len(pe_ratios) == 3:
                        position.run_dcf_valuation(eps, eps_growth, pe_ratios)
                    elif not historic_data and len(pe_ratios) != 3:
                        print('Please provide exactly three pe ratios if historic_data=False: [low, middle, high] \n'
                              'Intepreting as historic'
                              )

        return

    def change_decay_rates(self, new_rate, sub_tickers: list = None):
        """
        Changes position object decay rates
        :param new_rate: the new EPS growth decay rate to switch too
        :param sub_tickers: if none (default) the new decay rate is applied to all positions. Other wise a subset of tickers
        can be specified via a list of strings.
        :return:
        """
        if not sub_tickers:
            tickers = list(self.positions.keys())
        else:
            tickers = sub_tickers

        # update rates for tickers
        for tick in tickers:
            position = self.positions[tick]
            position._update_decay_rate(new_rate)

    # #### METHODS TO RETURN STATE BASED (i.e., current price based) values #####
    def calculate_expected_roic(self, current_prices_dict: dict = None, new_conservativeness: float = None):
        """

        :param current_prices_dict:
        :param new_conservativeness:
        :return:
        """
        tickers = self.get_tickers()

        # update conservativeness if input (optional)
        if isinstance(new_conservativeness, float):
            self.update_conservativeness(new_conservativeness)

        # update current prices if necessary
        if isinstance(current_prices_dict, dict):
            self.update_current_prices(current_prices_dict)

        # get scenario weighting based on conservativeness
        scenario_weights = self._get_scenario_weightings()

        # calculate expected returns
        valuations = {}
        relative_values = {}
        for tick in tickers:
            position = self.positions[tick]
            if isinstance(position.current_price, float):
                valuations = position.valuations
                if not valuations:
                    print(f'WARNING: No DCF valuation completed for ticker {tick}, run a DCF for the position within '
                          f'the portfolio (ex: Portfolio[TICKER].run_dcf_valuation() or for the whole portfolio'
                          f'(ex: Portfolio.run_batch_dcf_valuations()')
                else:
                    # get valuations and weight based off conservativeness
                    final_value = sum([value * weight for value, weight in zip(valuations, scenario_weights)])
                    relative_value = (final_value - position.current_price) / position.current_price

                    # add to dictionaries to store for each ticker
                    valuations[tick] = final_value
                    relative_values[tick] = relative_value

            elif not position:
                print(f'No current price data for ticker {tick}')
        self.raw_valuations = valuations
        self.expected_returns = relative_values

    def add_greed_weights(self, greed_exponent: float):
        """
        Raises expected returns by an exponent ranging 1 to 3 (corresponding to greed 0 - 1, 0.5 -> 2 is default)
        :param greed_exponent: the greed exponent fom get_greed_exponent(self.greed)
        :return:
        """
        expected_returns = self.expected_returns
        for tick in expected_returns.keys():
            greed_return = (float(expected_returns[tick]) ** greed_exponent)
            self.greedy_returns[tick] = greed_return
        return self.greedy_returns

    def add_portolio_balancer(self, gamma: float = None, eta: float = 0.95):
        if not gamma:
            gamma = self.gamma

        self.balance_scores = {}
        allocations = self.calculate_current_allocations()
        allocations_array = np.array(list(allocations.values()))
        allocations_mean = np.mean(allocations_array)
        allocations_std = np.std(allocations_array)

        for tick in allocations.keys():
            allocation = allocations[tick]
            z_score = (allocation - allocations_mean) / allocations_std
            balance_score = -z_score*gamma
            if abs(balance_score) > eta:
                if balance_score < 0:
                    balance_score = -eta
                else:
                    balance_score = eta
            self.balance_scores[tick] = balance_score
        return self.balance_scores

    # #### INTERNAL METHODS - using may cause issues#####
    def _get_scenario_weightings(self):
        low = 0
        mid = 0
        high = 0
        return [low, mid, high]

    def _positions_info_printer(self, positions_info_dict: dict):
        for key in positions_info_dict.keys():
            position_dict = positions_info_dict[key]
            shares = position_dict['Shares']
            equity = position_dict['Equity']
            profit_loss = position_dict['Return_in_dollars']

            print(f'------ TICKER: {key} ------\n'
                  f'# of shares: {shares} \n'
                  f'Current equity value: {equity}\n:'
                  f'Total retrun in $: {profit_loss}\n')


