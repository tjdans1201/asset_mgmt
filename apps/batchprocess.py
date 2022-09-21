import sys
import os

sys.dont_write_bytecode = True
import sqlite3
import pandas as pd

curDir = os.path.dirname(os.path.normpath(__file__))


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


sqliteConnection = sqlite3.connect("db.sqlite3")
sqliteConnection.row_factory = dict_factory
cursor = sqliteConnection.cursor()


def insert_stock():
    """
    csv로부터 종목 정보를 취득하여 새로운 종목일 경우 데이터베이스에 추가
    """
    try:
        print("start ")
        # asset_group_info_set.csv 파일을 dataframe화
        asset_group_info_df = pd.read_csv(curDir + "/data/asset_group_info_set.csv")
        # db와 일치하도록 컬럼명 변경
        asset_group_info_df.rename(
            columns={"종목명": "stock_name", "ISIN": "isin", "자산그룹": "asset_group_name"},
            inplace=True,
        )
        sqlite_select_Query = "select * from assets_assetgroup;"
        cursor.execute(sqlite_select_Query)
        record = cursor.fetchall()
        # 자산군 id를 부여하기 위하여 자산군 테이블로부터 데이터 취득
        asset_group_df = pd.DataFrame(record)
        # 각 자산군 이름에 맞게 merge
        merge_df = asset_group_df.merge(
            asset_group_info_df, on="asset_group_name", how="left"
        )
        merge_df.rename(columns={"id": "asset_group_id_id"}, inplace=True)
        # 필요한 칼럼만 남김
        merge_df = merge_df.drop(["asset_group_name"], axis=1)
        # 종목 테이블에서 데이터 취득
        SQL = "select stock_name, isin, asset_group_id_id from assets_stock"
        table_df = pd.read_sql(SQL, sqliteConnection)
        # 종목 테이블에 존재하지 않는 종목만 테이블에 추가
        insert_df = (
            pd.merge(table_df, merge_df, how="outer", indicator=True)
            .query('_merge == "right_only"')
            .drop(columns=["_merge"])
        )
        insert_df.to_sql(
            "assets_stock", sqliteConnection, if_exists="append", index=False
        )
        print("finish insert_stock")
    except Exception as e:
        print(e)
        pass


def update_account_asset_info():
    """
    csv로부터 보유종목과 현재시세를 취득하여 데이터베이스 업데이트
    """
    try:
        print("start update_account_asset_info")
        # csv로부터 data취득후 데이터프레임으로 변환
        account_asset_info_df = pd.read_csv(curDir + "/data/account_asset_info_set.csv")
        # 필요한 컬럼만 남기고 db 컬럼명에 맞게 변경
        account_asset_info_df.rename(
            columns={
                "계좌번호": "account_number",
                "ISIN": "isin",
                "현재가": "current_price",
                "보유수량": "amount",
            },
            inplace=True,
        )
        account_asset_info_df = account_asset_info_df[
            ["account_number", "isin", "current_price", "amount"]
        ]
        # 계좌 테이블과 종목 테이블에서 id값 취득하고 데이터프레임화
        account_query = "select id, account_number from assets_account"
        cursor.execute(account_query)
        account_rocords = cursor.fetchall()
        account_df = pd.DataFrame(account_rocords)
        account_df.rename(columns={"id": "account_id_id"}, inplace=True)
        stock_query = "select id, isin from assets_stock"
        cursor.execute(stock_query)
        stock_rocords = cursor.fetchall()
        stock_df = pd.DataFrame(stock_rocords)
        stock_df.rename(columns={"id": "stock_id_id"}, inplace=True)
        # csv데이터의 계좌번호를 기준으로 id값 merge
        account_asset_info_df = stock_df.merge(
            account_asset_info_df, on="isin", how="left"
        )
        # csv데이터의 isin을 기준으로 id값 merge
        account_asset_info_df = account_df.merge(
            account_asset_info_df, on="account_number", how="left"
        )
        # 보유종목 테이블에 존재하는 컬럼만 남김
        account_asset_info_df = account_asset_info_df.drop(
            ["account_number", "isin"], axis=1
        )
        # 가공한 dataframe을 dict_list로 변환
        account_asset_info_dict_list = account_asset_info_df.to_dict("records")
        # db 업데이트
        for i in account_asset_info_dict_list:
            query = (
                "update assets_stocksheld set current_price = %s, amount = %s where account_id_id = %s and stock_id_id = %s"
                % (
                    i["current_price"],
                    i["amount"],
                    i["account_id_id"],
                    i["stock_id_id"],
                )
            )
            cursor.execute(query)
        sqliteConnection.commit()
        account_asset_info_df.to_sql(
            "assets_stocksheld", sqliteConnection, if_exists="append"
        )
        print("finish update_account_asset_info")
    except Exception as e:
        print(e)
        pass


def update_investment_principle():
    """
    csv로부터 계좌 별 투자원금 데이터를 취득하여 데이터베이스 업데이트
    """
    try:
        print("start update_investment_principle")
        # csv를 dataframe화
        account_basic_info_df = pd.read_csv(curDir + "/data/account_basic_info_set.csv")
        # table에 맞게 컬럼명 변경
        account_basic_info_df.rename(
            columns={"계좌번호": "account_number", "투자원금": "investment_principal"},
            inplace=True,
        )
        account_basic_info_dict = account_basic_info_df.to_dict("records")
        # 데이터베이스 업데이트
        for i in account_basic_info_dict:
            query = (
                "update assets_account set investment_principal = %s where account_number = %s"
                % (i["investment_principal"], i["account_number"])
            )
            cursor.execute(query)
        sqliteConnection.commit()
        print("finish update_investment_principle")
    except Exception as e:
        print(e)
        pass
