# -*- coding: utf-8 -*-


# BankCSVtoQif - Smart conversion of csv files from a bank to qif
# Copyright (C) 2015-2016  Nikolai Nowaczyk
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from datetime import datetime
import re

from bankcsvtoqif.banks import BankAccountConfig
from bankcsvtoqif.transaction import TransactionType


class Orico(BankAccountConfig):
    """ Orient Corporation (Orico) """

    transaction_type = TransactionType.CREDIT_CARD
    amount_sanitization_regex = re.compile(r"^\\")

    def __init__(self):
        BankAccountConfig.__init__(self)

        self.delimiter = ','
        self.quotechar = '"'
        self.dropped_lines = 10
        self.default_source_account = 'Assets:Current Assets:Checking Account'
        self.default_target_account = 'Imbalance-JPY'
        self.encoding = 'shift-jis'

    def get_date(self, line, all_lines):
        date = line[0]
        if not date:
            date = all_lines[2][1]
        return datetime.strptime(date, "%Y年%m月%d日")

    def get_description(self, line, all_lines):
        return "{}（{}）".format(line[1], line[3])

    def get_amount(self, amount):
        amount = self.amount_sanitization_regex.sub("", amount)
        amount = amount.replace(",", "")
        return int(amount)

    def find_amount(self, line):
        indexes = [8, 11]
        for index in indexes:
            try:
                return self.get_amount(line[index])
            except ValueError:
                pass
        raise ValueError(
            "Could not find a cash amount in any of these cells: {}".format(
                ", ".join(str(index) for index in indexes)
            )
        )

    def get_debit(self, line, all_lines):
        amount = self.find_amount(line)
        return -min(amount, 0)

    def get_credit(self, line, all_lines):
        amount = self.find_amount(line)
        return max(amount, 0)
