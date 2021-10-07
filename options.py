"""
This file contains functions from the opstrat python package avaiable through pipi
Code below is inspired from the original

Some descriptions are taken from Investopedia.

teaching_with_code(;)

USAGE:
-----

"""
from typing import List
import numpy as np
import logging as log
from dataclasses import asdict, dataclass

# set log level
# TODO: add option to externally set this
log.basicConfig(level=log.INFO)

##########################################
#     constants have their own types     #
##########################################
class OP_TYPE:
    """
    Option types can be a call or put

    Call:
    ----
    Call options are financial contracts that give the option
    buyer the right, but not the obligation, to buy a stock,
    bond, commodity, or other asset or instrument at a specified
    price within a specific time period. The stock, bond, or
    commodity is called the underlying asset. A call buyer profits
    when the underlying asset increases in price.

    Put:
    ----
    A put option is a contract giving the owner the right,
    but not the obligation, to sell–or sell short–a specified
    amount of an underlying security at a pre-determined price
    within a specified time frame.
    """

    CALL = "Call"
    PUT = "Put"

    # TODO: there should be a more pythonic way to do this
    def check_type(txt: str):
        return txt in (OP_TYPE.CALL, OP_TYPE.PUT)


class TR_TYPE:
    """
    The transaction types are Buy or Sell

    Buy/Long:
    --------
    The term long has nothing to do with the measurement of time.
    Instead, it speaks to the owning of an underlying asset. The
    long position holder is one who currently holds the underlying
    asset in their portfolio.
    When a trader buys or holds a call options contract from an options
    writer, they are long, due to the power they hold in being able to buy
    the asset. An investor who is long a call option is one who buys
    a call with the expectation that the underlying security will
    increase in value (bull-ish). The long position call holder believes
    the asset's value is rising and may decide to exercise their option to
    buy it by the expiration date.

    Sell/Short:
    ----------
    A short call is a strategy involving a call option, which obligates
    the call seller to sell a security to the call buyer at the strike
    price if the call is exercised.
    A short call is under the expectency of asset value to go down
    (bearish trading strategy), reflecting a bet that the security underlying
    the option will fall in price.
    A short call involves more risk but requires less upfront money
    than a long put, another bearish trading strategy.
    """

    BUY = "Buy"  # also called Long
    SELL = "Sell"  # also called Short

    def check_type(txt: str):
        return txt in (TR_TYPE.BUY, TR_TYPE.SELL)

@dataclass
class OptionsContract:
    """
    A NamedTuple describing the attributes of a contract.
    A list of options contracts is intended to be passed to a
    multi-leg payoff calculator
    The class NamedTuples has a function `_asdict()`
    that provides dict with named types.
    Having such a class enforces conformity.

    args:
    -------
    op_type: OP_TYPE
        option type can be 'Call' or 'Put'

    spot: int
        spot price (current price) of the stock

    spot_range: int or float
        the range around which spot price is evaluated

    strike: int or float
        the strike price of this option contract
        based on where the spot price is the strike price can be
        - in the money => strike < spot
        - out of the money => strike > spot
        - at the money => strike == spot

    tr_type: TR_TYPE
        Buy or Sell (Long or Short) transaction type

    op_pr: int or float,
        option price, can be found in the option chain

    """

    op_type: OP_TYPE
    strike: int or float
    tr_type: TR_TYPE
    op_pr: int or float
    spot: int = None
    spot_range: int or float = None
    num_contracts: int = 1

    # TODO: values should be called something else
    # what are the attributes of a contract called
    @property
    def values(self):
        """
        A wrapper over the _asdict() function
        return the value of each attribute as a dict
        """
        # drop values that are not defined
        this = asdict(self).copy()
        for k in asdict(self).keys():
            if this[k] is None:
                del this[k]

        return this


##########################################


def compute_payoff(
    op_type: OP_TYPE,
    strike: int or float,
    tr_type: TR_TYPE,
    op_pr: int or float,
    spot: int,
    spot_range: int or float,
    num_contracts: int = 1,
) -> np.array:
    """
    Compute the pay-offs for a single options contract
    NOTE: Do not use kwargs to force API user into thinking about each arg

    args:
    -------
    op_type: OP_TYPE
        option type can be 'Call' or 'Put'

    strike: int or float
        the strike price of this option contract
        based on where the spot price is the strike price can be
        - in the money => strike < spot
        - out of the money => strike > spot
        - at the money => strike == spot

    tr_type: TR_TYPE
        Buy or Sell (Long or Short) transaction type

    op_pr: int or float,
        option price, can be found in the option chain

    spot: int
        spot price (current price) of the stock

    spot_range: int or float
        the range around which spot price is evaluated

    num_contracts: int, default = 1
        number of contracts

    returns
    -------
    A 1D numpy array

    """

    # check the type of constants passed
    if not OP_TYPE.check_type(op_type):
        log.warning(f"Invalid op_type '{op_type}'  passed. see doc")
        return None
    if not TR_TYPE.check_type(tr_type):
        log.warning(f"Invalid op_type '{tr_type}' passed. see doc")
        return None

    # build price range around the spot price
    # pay off will be computed around this price range
    # use a step size of 0.01 - describes a range factor
    # TODO: this should be a that can be changed constant
    # Intermitted Volitility (IV) should be a good indicator of this?
    x = spot * np.arange(100 - spot_range, 101 + spot_range, 0.01) / 100

    # an array that will store
    pay_off = np.zeros_like(x)

    # Assume that this is BUY scenario
    # if this is a call
    # You are saying that you will buy a x100 at the strike price
    # NOTE: keeping condition outside loop reduces the number of times it is computed
    if op_type == OP_TYPE.CALL:
        for i in range(len(x)):
            pay_off[i] = max(x[i] - strike - op_pr, -op_pr)
    # You will sell a x100 at strike price
    elif op_type == OP_TYPE.PUT:
        for i in range(len(x)):
            pay_off[i] = max(strike - x[i] - op_pr, -op_pr)

    # If if this a Sell scenario,
    # simply invert the payoffs
    if tr_type == TR_TYPE.SELL:
        pay_off = -1 * pay_off

    # get the pay off back
    # number of contracts multiplier
    # Each contract generally has 100 stocks
    return pay_off * num_contracts


# TODO:
def compute_payoff_multileg(
    spot: int, spot_range: int or float, op_legs: List[OptionsContract]
) -> np.array:
    raise NotImplementedError


# TODO:
def black_scholes(
    t: int = 40,
    r: float = 4.00,  # TODO: change to [0, 1]
    v: float = 32.00, # TODO: change to [0, 1]
    K: int or float = 60,
    St: int or float = 62,
    op_type: OP_TYPE = OP_TYPE.CALL,
) -> dict:
    """
    Parameters:
    t : Time to expiration in days
    r : Risk free rate in percentage
    v : Volatility in percentage
    K : Excercise Price
    St: Current Stock Price
    type: Type of option 'c' for call 'p' for put
    default: 'c'
    """
    raise NotImplementedError


if __name__ == "__main__":

    print("Running pay off test")

    op_leg = OptionsContract(
        op_type=OP_TYPE.CALL,
        # spot=100,
        # spot_range=10,
        strike=102,
        tr_type=TR_TYPE.BUY,
        op_pr=2,
        num_contracts=1,
    )

    
    # pass the leg as kwargs
    returns = compute_payoff(**op_leg.values, spot=100, spot_range=10)
    print(returns)
