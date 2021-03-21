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

import csv
from enum import Enum, auto


class TransactionType(Enum):
    CASH = auto()
    BANK = auto()
    CREDIT_CARD = auto()
    INVESTMENT = auto()


class Transaction(object):
    """ Represents a transaction obtained from csv-file. """

    qif_record_types = {
        TransactionType.CASH: "Cash",
        TransactionType.BANK: "Bank",
        TransactionType.CREDIT_CARD: "CCard",
        TransactionType.INVESTMENT: "Invst",
    }

    def __init__(
            self,
            date,
            description,
            debit,
            credit,
            target_account,
            source_account='Assets:Current Assets:Checking Account',
            transaction_type=TransactionType.CASH,
    ):
        self.date = date
        self.description = description
        self.debit = debit
        self.credit = credit
        self.target_account = target_account
        self.source_account = source_account
        self.transaction_type = transaction_type

    def __str__(self):
        return '<Transaction %s, %s, %s, %s, %s>'% (
            self.date,
            self.description,
            self.debit,
            self.credit,
            self.target_account
        )

    @property
    def amount(self):
        if self.is_liability():
            return self.debit - self.credit
        else:
            return self.credit - self.debit

    @property
    def qif_record_type(self):
        try:
            return self.qif_record_types[self.transaction_type]
        except KeyError:
            raise ValueError(
                "Unknown transaction type: {}".format(self.transaction_type)
            )

    def is_liability(self):
        return self.transaction_type is TransactionType.CREDIT_CARD

    def to_qif_line(self):
        return [
            '!Type:' + self.qif_record_type,
            'D' + self.date.strftime('%m/%d/%y'),
            'S' + self.target_account,
            'P' + self.description,
            '$' + '%.2f' % self.amount,
            '^'
        ]


class TransactionFactory(object):
    """ Creates Transactions from an account_config. """

    def __init__(self, account_config):
        self.account_config = account_config

    def create_from_csv_data(self, line, all_lines):
        return Transaction(
            date=self.account_config.get_date(line, all_lines),
            description=self.account_config.get_description(line, all_lines),
            debit=self.account_config.get_debit(line, all_lines),
            credit=self.account_config.get_credit(line, all_lines),
            target_account=self.account_config.get_target_account(line, all_lines),
            source_account=self.account_config.get_source_account(line, all_lines),
            transaction_type=self.account_config.get_transaction_type(line, all_lines),
        )

    def read_from_file(self, f, messenger):
        csv.register_dialect(
            'bank_csv',
            self.account_config.get_csv_dialect()
        )
        reader = csv.reader(f, 'bank_csv')
        all_lines = tuple(tuple(line) for line in reader)
        transactions = []
        for line in all_lines[self.account_config.dropped_lines:]:  # ignore first lines
            try:
                transaction = self.create_from_csv_data(line, all_lines)
                transactions.append(transaction)
                messenger.send_message('parsed: {}'.format(transaction))
            except IndexError:
                messenger.send_message('skipped: {}'.format(line))
                continue
        return transactions
