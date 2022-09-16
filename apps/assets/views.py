from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Account, StockSheld
import pandas as pd

# Create your views here.


class AssetAPI(APIView):
    def get(self, request, id):
        """
        투자화면

        Args:
            id : 계좌_id
        Returns:
            result: {"account_name":str, "stock_firm_name":str, "account_number":int, "total_asset":int}
        """
        try:
            # 계좌 테이블에서 데이터 취득
            account = Account.objects.get(id=id)
            total_asset = 0
            # 보유 종목 테이블에서 데이터 취득
            stocksheld_list = StockSheld.objects.filter(account_id=id)
            # 보유 종목이 있는 경우 각 종목의 평가금액을 구한 뒤 합산
            ss_df = pd.DataFrame(stocksheld_list.values())
            ss_df["asset"] = ss_df["current_price"] * ss_df["amount"]
            total_asset = ss_df["asset"].sum()
            result = {
                "account_name": account.account_name,
                "stock_firm_name": account.stock_firm_id.stock_firm_name,
                "account_number": account.account_number,
                "total_asset": total_asset,
            }
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"messgae": "서버에 에러가 발생하였습니다."})


class AssetDetailAPI(APIView):
    def get(self, request, id):
        """
        투자상세 화면
            계좌명
            증권사
            계좌번호
            계좌 총 자산
            투자 원금
            총 수익금 (총 자산 - 투자 원금)
            수익률 (총 수익금 / 투자 원금 * 100)

        Args:
            id : 계좌_id
        Returns:
            result: {"account_name":str, "stock_firm_name":str, "account_number":int, "total_market_value":int, "investment_principal":int, "total_profit" : int, "profit_rate" : float}
        """
        try:
            # 계좌 테이블에서 데이터 취득
            account = Account.objects.get(id=id)
            total_asset = 0
            total_profit = 0
            profit_rate = 0
            investment_principal = account.investment_principal
            # 보유 종목 테이블에서 데이터 취득
            stocksheld_list = StockSheld.objects.filter(account_id=id)
            # 각 종목의 평가금액을 구한 뒤 합산
            ss_df = pd.DataFrame(stocksheld_list.values())
            ss_df["asset"] = ss_df["current_price"] * ss_df["amount"]
            total_asset = ss_df["asset"].sum()
            total_profit = investment_principal - total_asset
            profit_rate = round(total_profit / investment_principal * 100, 2)
            result = {
                "account_name": account.account_name,
                "stock_firm_name": account.stock_firm_id.stock_firm_name,
                "account_number": account.account_number,
                "total_asset": total_asset,
                "investment_principal": investment_principal,
                "total_profit": total_profit,
                "profit_rate": profit_rate,
            }
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"messgae": "서버에 에러가 발생하였습니다."})


class AssetStockAPI(APIView):
    def get(self, request, id):
        """
        투자상세화면

        Args:
            id : 계좌_id
        Returns:
            result: {"sotcksheld_list_dict:{"asset_group_name":[{"stock_name" : str, "isin":str, market_value:int}]}"}
        """
        try:
            # 보유 종목 테이블에서 데이터 취득
            stocksheld_list = StockSheld.objects.filter(account_id=id)
            # 자산그룹에 따라 분류한 list의 dict
            stocksheld_list_dict = {}
            # 취득한 보유 종목 만큼 loop
            for stocksheld in stocksheld_list:
                stock = stocksheld.stock_id
                stocksheld_dict = {}
                # 자산그룹명 취득
                assetgroup_name = stock.asset_group_id.asset_group_name
                stocksheld_dict["stock_name"] = stock.stock_name
                stocksheld_dict["isin"] = stock.isin
                stocksheld_dict["market_value"] = (
                    stocksheld.current_price * stocksheld.amount
                )
                # stocksheld_list_dict의 key에 해당 자산그룹이 있으면 list에 추가
                if assetgroup_name in stocksheld_list_dict.keys():
                    stocksheld_list_dict[assetgroup_name].append(stocksheld_dict)
                # stocksheld_list_dict의 key에 해당 자산그룹이 없으면 해당 자산그룹을 key로 하는 list 추가
                else:
                    stocksheld_list_dict[assetgroup_name] = [stocksheld_dict]
            result = {"sotcksheld_list_dict": stocksheld_list_dict}
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"messgae": "서버에 에러가 발생하였습니다."})
