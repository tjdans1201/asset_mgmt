from django.test import TestCase
from rest_framework.test import APIClient
import os
import pandas as pd
from ..assets.models import AssetGroup, StockFirm, Stock, StockSheld, Account
from ..transactions.models import Transaction
import hashlib

curDir = os.path.dirname(os.path.normpath(__file__))

# 더미데이터 생성
def set_dummy(table_list):
    for i in table_list:
        df = pd.read_csv(curDir + "/dummy/" + i + ".csv")
        i_dict_list = df.to_dict("records")
        if i == "assets_assetgroup":
            assets_assetgroups = [
                AssetGroup(id=x["id"], asset_group_name=x["asset_group_name"])
                for x in i_dict_list
            ]
            AssetGroup.objects.bulk_create(assets_assetgroups)
        elif i == "assets_stockfirm":
            assets_stockfirms = [
                StockFirm(id=x["id"], stock_firm_name=x["stock_firm_name"])
                for x in i_dict_list
            ]
            StockFirm.objects.bulk_create(assets_stockfirms)
        elif i == "assets_stock":
            assets_stocks = [
                Stock(
                    id=x["id"],
                    stock_name=x["stock_name"],
                    isin=x["isin"],
                    asset_group_id_id=x["asset_group_id_id"],
                )
                for x in i_dict_list
            ]
            Stock.objects.bulk_create(assets_stocks)
        elif i == "assets_account":
            assets_accounts = [
                Account(
                    id=x["id"],
                    account_holder=x["account_holder"],
                    stock_firm_id_id=x["stock_firm_id_id"],
                    account_number=x["account_number"],
                    account_name=x["account_name"],
                    investment_principal=x["investment_principal"],
                )
                for x in i_dict_list
            ]
            Account.objects.bulk_create(assets_accounts)
        elif i == "assets_stocksheld":
            assets_stockshelds = [
                StockSheld(
                    id=x["id"],
                    account_id_id=x["account_id_id"],
                    stock_id_id=x["stock_id_id"],
                    current_price=x["current_price"],
                    amount=x["amount"],
                )
                for x in i_dict_list
            ]
            StockSheld.objects.bulk_create(assets_stockshelds)
        print("finish insert table " + i)


class TestViews(TestCase):
    @classmethod
    def setUp(cls):
        table_list = [
            "assets_assetgroup",
            "assets_stockfirm",
            "assets_stock",
            "assets_account",
            "assets_stocksheld",
        ]
        set_dummy(table_list)

    def test_get_assets(self):
        # 투자화면 조회 테스트
        client = APIClient()
        result = client.get("/api/assets/1")
        exp = {
            "account_name": "계좌1",
            "stock_firm_name": "디셈버증권",
            "account_number": "5736692368320",
            "total_asset": 1989245,
        }
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, exp)

    def test_get_assets_detail(self):
        # 투자상세 조회 테스트

        client = APIClient()
        result = client.get("/api/assets/1/detail")
        exp = {
            "account_name": "계좌1",
            "stock_firm_name": "디셈버증권",
            "account_number": "5736692368320",
            "total_asset": 1989245,
            "investment_principal": 1971386,
            "total_profit": -17859,
            "profit_rate": -0.91,
        }
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, exp)

    def test_get_assets_stock(self):
        # 보유종목 조회 테스트

        client = APIClient()
        result = client.get("/api/assets/1/detail/stock")
        exp = {
            "sotcksheld_list_dict": {
                "미국 주식": [
                    {
                        "stock_name": "미국S&P500",
                        "isin": "KR7360750004",
                        "market_value": 180285,
                    },
                    {
                        "stock_name": "미국나스닥100",
                        "isin": "KR7133690008",
                        "market_value": 187967,
                    },
                ],
                "미국섹터 주식": [
                    {
                        "stock_name": "미국나스닥바이오",
                        "isin": "KR7203780002",
                        "market_value": 152484,
                    },
                    {
                        "stock_name": "미국S&P IT(합성)",
                        "isin": "KR7200020006",
                        "market_value": 57560,
                    },
                ],
                "선진국 주식": [
                    {
                        "stock_name": "선진국MSCI World",
                        "isin": "KR7251350005",
                        "market_value": 99470,
                    },
                    {
                        "stock_name": "일본니케이225",
                        "isin": "KR7241180009",
                        "market_value": 283184,
                    },
                ],
                "신흥국 주식": [
                    {
                        "stock_name": "베트남VN30",
                        "isin": "KR7245710009",
                        "market_value": 161712,
                    },
                    {
                        "stock_name": "신흥국MSCI",
                        "isin": "KR7195980008",
                        "market_value": 212595,
                    },
                ],
                "전세계 주식": [
                    {
                        "stock_name": "전세계MSCI",
                        "isin": "KR7195980002",
                        "market_value": 6130,
                    }
                ],
                "부동산 / 원자재": [
                    {
                        "stock_name": "WTI원유선물",
                        "isin": "KR7261220008",
                        "market_value": 282618,
                    },
                    {
                        "stock_name": "S&P글로벌인프라",
                        "isin": "KR7130680002",
                        "market_value": 103152,
                    },
                ],
                "채권 / 현금": [
                    {
                        "stock_name": "단기채권",
                        "isin": "KR7153130000",
                        "market_value": 151182,
                    },
                    {
                        "stock_name": "미국장기우량회사채",
                        "isin": "KR7332620004",
                        "market_value": 26637,
                    },
                    {"stock_name": "현금", "isin": "CASH", "market_value": 84269},
                ],
            }
        }
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, exp)

    def test_transaction(self):
        # 투자금 입금
        client = APIClient()
        result = client.post(
            "/api/transactions",
            {
                "account_number": "5736692368320",
                "user_name": "류영길",
                "transfer_amount": 10000,
            },
            format="json",
        )
        self.assertTrue("transfer_identifier" in result.data.keys())
        transaction = Transaction.objects.all().values()[0]
        transfer_identifier = result.data["transfer_identifier"]
        self.assertEqual(
            result.data["transfer_identifier"], transaction["transfer_identifier"]
        )
        self.assertEqual(transaction["is_finish"], False)
        transaction_hash = hashlib.sha512("5736692368320류영길10000".encode())
        transaction_hash = transaction_hash.hexdigest()
        before_current_price = StockSheld.objects.get(
            stock_id_id=14, account_id_id=1
        ).current_price
        before_account_investment_principal = Account.objects.get(
            id=1
        ).investment_principal

        # 투자금 입금 인증 실패
        result = client.put(
            "/api/transactions",
            {
                "signature": transaction_hash,
                "transfer_identifier": 12344,
            },
            format="json",
        )
        self.assertEqual(result.data, {"message": "인증에 실패했습니다."})

        # 투자금 입금 인증 성공
        result = client.put(
            "/api/transactions",
            {
                "signature": transaction_hash,
                "transfer_identifier": transfer_identifier,
            },
            format="json",
        )
        print(result.data)
        self.assertEqual(result.data["status"], True)
        transaction = Transaction.objects.all().values()[0]
        self.assertEqual(transaction["is_finish"], True)
        after_current_price = StockSheld.objects.get(
            stock_id_id=14, account_id_id=1
        ).current_price
        after_account_investment_principal = Account.objects.get(
            id=1
        ).investment_principal
        self.assertEqual(after_current_price - before_current_price, 10000)
        self.assertEqual(
            after_account_investment_principal - before_account_investment_principal,
            10000,
        )
