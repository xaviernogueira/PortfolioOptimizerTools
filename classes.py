from functions import *

class position:

    def __init__(self, ticker: str = None, current_price: float = None):
        if not ticker:
            self.ticker = None
            return
        else:
            # store ticker name
            self.ticker = str(ticker).capitalize()

            # store number of shares and purchases
            self.shares = 0
            self.invested = 0

            self.purchases = []  # a list of purchase amoutns in shares (int or float)
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

    # make class methods to redefine values from outside the class
    @classmethod
    def _update_decay_rate(self, new_decay_rate):
        self.decay_rate = new_decay_rate

    @classmethod
    def _update_discount_rate(self, updated_discount_rate: float):
        self.discount_rate = updated_discount_rate

    @classmethod
    def _update_current_price(self, new_price):
        self.current_price = new_price

    # define functions to internally update the state of the position class
    def update_average_price(self):
        self.average_price = self.invested / self.shares

    def update_equity(self):
        self.equity = self.current_price * self.shares
        self.profit_loss = self.invested - self.equity

    # define a function to initiate a positions with a starting share balance
    def add_base_position(self, shares, average_price):
        if shares == 0:
            self.shares = shares
            self.invested = shares * average_price
            self.purchases = [shares]
            self.purchase_prices = [average_price]
            self.update_average_price()

            if isinstance(self.current_price, float):
                self.update_equity()

        else:
            return print('ERROR: You are trying to initialize a position in {} that already exists!')

    # define a function to make buy trades
    def make_a_buy(self, shares, average_price):
        self.shares += shares
        self.invested += (shares * average_price)
        self.purchases.append(shares)
        self.purchase_prices.append(average_price)
        self.update_average_price()

        if isinstance(self.current_price, float):
            self.update_equity()

    # main internal DCF function, how the DCF results are used/interpreted is controlled by the portfolio object
    def update_valuation(self, eps: float, three_year_eps_growth: float, pe_ratios_outcomes: list = None,
                      historic_pe_ratios: list = None, time_horizon: int = 10,
                      decay_rate: float = 0.05):




class Portfolio:

    def __init__(self, positions_dict: dict = None):
        """

        :param positions_dict: a dictionary with ticker names as keys storing [# of shares, average price]
        """
        """:param conservativeness: default is 0.5, but can range from 0 (no conservativeness) to 1 (max). A higher value 
        places more probabilistic weight on lower terminal pe outcomes, and increase growth decay rates. """
        self.positions = {}

        if isinstance(positions_dict, dict):
            for tick in list(positions_dict.keys()):
                shares, price = positions_dict[tick]
                self.positions[tick] = position(ticker=tick)
                self.positions[tick].add_base_position(shares, price)
                print(f'Initialized a position in ticker {tick}, with {shares} shares at an average price of {price}')

    def calculate_expected_oppurtunity



