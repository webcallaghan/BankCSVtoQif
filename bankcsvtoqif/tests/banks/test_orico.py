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

from bankcsvtoqif.banks.orico import Orico
from bankcsvtoqif.tests.banks import TestBankAccountConfig
from bankcsvtoqif.transaction import Transaction


class TestOrico(TestBankAccountConfig):
    def testParse(self):
        account_config = Orico()
        self.assert_csv_parsed_as(
            "orico.csv",
            account_config,
            [
                Transaction(
                    date=datetime(2021, 3, 1),
                    description="This is a debit テスト（家族）",
                    debit=4000,
                    credit=0,
                    source_account=account_config.default_source_account,
                    target_account=account_config.default_target_account,
                ),
                Transaction(
                    date=datetime(2021, 3, 10),
                    description="This is a credit テスト（本人）",
                    debit=0,
                    credit=5000,
                    source_account=account_config.default_source_account,
                    target_account=account_config.default_target_account,
                ),
                Transaction(
                    date=datetime(2021, 3, 29),
                    description="ご利用代金明細書発行手数料（本人）",
                    debit=0,
                    credit=110,
                    source_account=account_config.default_source_account,
                    target_account=account_config.default_target_account,
                ),
            ]
        )
