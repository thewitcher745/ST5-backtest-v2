from typing import Union, Literal

import numpy as np
import pandas as pd

import algo_code.position_prices_setup as setup
import utils.constants as constants


class Position:
    def __init__(self, parent_ob):
        self.parent_ob = parent_ob
        self.entry_price = parent_ob.top if parent_ob.type == "long" else parent_ob.bottom

        self.type = parent_ob.type

        self.status: str = "ACTIVE"
        self.entry_pdi = None
        self.qty: float = 0
        self.highest_target: int = 0
        self.target_hit_pdis: list[int] = []
        self.exit_pdi = None
        self.portioned_qty = []
        self.net_profit = None

        self.target_list = []
        self.stoploss = None

        # Set up the target list nd stoploss using a function which operates on the "self" object and directly manipulates the instance.
        setup.default_1234(self)

    def enter(self, entry_pdi: int):
        """
        Method to enter the position. This method sets the current position status to "ENTERED", and registers the entry PDI, entry price, and
        quantity of the entry. Raises an IndexError if the entry isn't within the active indices of its parent OrderBlock.

        Args:
            entry_pdi (int): The PDI at which the entry is made
        """

        if entry_pdi > self.parent_ob.end_pdi or entry_pdi < self.parent_ob.formation_pdi:
            raise IndexError(f"Entry PDI {entry_pdi} is out of bounds for Order Block {self.parent_ob.id}")

        self.entry_pdi = entry_pdi
        self.qty = constants.used_capital / self.entry_price
        self.status = "ENTERED"

    def exit(self,
             symbol: str,
             pair_df_times: np.ndarray,
             exit_status: str,
             exit_pdi: int,
             target_hit_pdis: list[int],
             exit_price: float) -> dict:
        """
        Calculate the exit parameters when triggered, and return a dict item containing the exit parameters.
        Args:
            symbol (str): The name of the pair currently being backtested
            pair_df_times (np.ndarray): A numpy ndarray containing time data from pair_df
            exit_status (str): The exit status, can be 'STOPLOSS', 'TRAILING', 'FULL_TARGET_*' or 'TARGET_*'
            exit_pdi (int): The PDI of the exiting candle
            target_hit_pdis (list[int]): The PDI's of the targets hit
            exit_price (float): The exiting price

        Returns:
            dict: A dict containing the exit parameters of the position, to be added to its parent OB's exit_positions list.
        """
        exit_parameters = {
            'Pair name': symbol,
            'Position ID': self.parent_ob.id,
            'Status': exit_status,
            'Net profit': 0,
            'Quantity': self.qty,
            'Entry time': pair_df_times[self.entry_pdi],
            'Exit time': pair_df_times[exit_pdi],
            'Target hit times': [pair_df_times[pdi] for pdi in target_hit_pdis],
            'Type': self.type,
            'Entry price': self.entry_price,
            'Exit price': exit_price,
            'Stoploss': self.stoploss,
            'Target list': [float(target) for target in self.target_list]
        }

        self.parent_ob.exit_positions.append(exit_parameters)

        return exit_parameters
