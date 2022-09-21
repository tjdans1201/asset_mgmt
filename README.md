# asset_mgmt

## 프로젝트 설명
- 투자 조회와 투자금 입금 신청 및 검증 서비스

- pandas를 사용하여 계좌 총 자산, 총 수익금, 수익률과 같은 항목을 계산

## 사용된 기술
 - **Back-End** : Python, Django, Django REST framework
 - **Database** : sqlite3
 - **Library** : Pandas

## ERD

<img width="196" alt="erd" src="https://user-images.githubusercontent.com/57758265/191485315-6d48dd4e-491b-4389-9400-f52424f7310d.png">

<img width="196" alt="erd" src="https://user-images.githubusercontent.com/57758265/191485592-872254fe-6e76-4c36-8f03-4db6317ad5f5.png">

asset_group, stock, stock_firm 테이블은 기본적으로 마스터 데이터가 존재한다고 가정

## Batch
데이터 셋은 apps/data에 csv로 파일로 제공된다고 가정하고 개발
pandas로 csv를 읽어서 각 테이블에 데이터를 추가하거나 수정
- account_asset_info_set.csv
- account_basic_info_set.csv
- asset_group_info_set.csv
매일 오전 10시 경 batch가 실행된다고 가정
- 10시 정각 : asset_group_info_set.csv의 데이터 중 stock table에 없는 종목은 추가
- 10시 10초 : account_basic_info_set.csv를 읽고 각 계좌의 투자원금을 업데이트
- 10시 20초 : account_asset_info_set.csv를 읽고 계좌 별 보유종목의 현재가와 보유수량을 업데이트

### 종목

## API

### 투자 화면

요청 받은 계좌를 조회하고 보유 종목 테이블에서 해당 계좌의 보유 종목 데이터를 취득한 후 각 종목의 현재 가치와 보유량을 통해 계좌 총 자산을 구한 뒤 리턴한다.

method : get

/api/assets/<int:id>

Response_body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 계좌명 | account_name | str |  |
| 증권사 | stockfirm_name | int |  |
| 계좌번호 | account_number | int |  |
| 계좌 총 자산 | total_market_value | int |  |

HTTP status code

| HTTP status | AppErrors | 메시지 | 설명 |
| --- | --- | --- | --- |
| 200 | - | - | 정상종료 |
| 500 | Internal Server Error | 서버 에러가 발생하였습니다. | API 내부 에러 발생 |

Response Example

1) 200

```json
{
    "account_name": "계좌1",
    "stock_firm_name": "디셈버증권",
    "account_number": 5736692368320,
    "total_asset": 1929245
}
```

2) 500

```json
{
    "Message": 서버 에러가 발생하였습니다.
}
```

### 투자 상세 화면

요청 받은 계좌를 조회하고 보유 종목 테이블에서 해당 계좌의 보유 종목 데이터를 취득한 후 각 종목의 현재 가치와 보유량을 통해 계좌 총 자산, 총 수익금, 수익률을 계산하여 리턴한다.

method : get

/api/assets/<int:id>/detail

Response_body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 계좌명 | account_name | str |  |
| 증권사 | stockfirm_name | str |  |
| 계좌번호 | account_number | int |  |
| 계좌 총 자산 | total_market_value | int |  |
| 투자 원금 | investment_principal | int |  |
| 총 수익금 | total_profit | int |  |
| 수익률 | profit_rate | int |  |

HTTP status code

| HTTP status | AppErrors | 메시지 | 설명 |
| --- | --- | --- | --- |
| 200 | - | - | 정상종료 |
| 500 | Internal Server Error | 서버 에러가 발생하였습니다. | API 내부 에러 발생 |

Response Example

1) 200

```json
{
    "account_name": "계좌1",
    "stock_firm_name": "디셈버증권",
    "account_number": 5736692368320,
    "total_asset": 1929245,
    "investment_principal": 1911386,
    "total_profit": -17859,
    "profit_rate": -0.93
}
```

2) 500

```json
{
    "Message": 서버 에러가 발생하였습니다.
}
```

### 보유종목 화면 API

요청 받은 계좌의 보유 종목을 조회하여 각 종목을 자산군으로 분류하여 요구하는 항목을 리턴한다.

method : get

/api/assets/<int:id>/detail/stock

Response_body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 보유종목 | stocksheld_list_dict | dict{} |  |
| 자산군 |  | dict_list{[]} |  |
| 보유종목명 | stock_name | str |  |
| 보유 종목의 평가 금액 | market_value | int |  |
| 보유 종목의 ISIN | isin | str |  |

HTTP status code

| HTTP status | AppErrors | 메시지 | 설명 |
| --- | --- | --- | --- |
| 200 | - | - | 정상종료 |
| 500 | Internal Server Error | 서버 에러가 발생하였습니다. | API 내부 에러 발생 |

Response Example

1) 200

```json
{
    "stocksheld_list_dict": {
        "미국 주식": [
            {
                "stock_name": "미국S&P500",
                "isin": "KR7360750004",
                "market_value": 180285
            },
            {
                "stock_name": "미국나스닥100",
                "isin": "KR7133690008",
                "market_value": 187967
            }
        ],
        "미국섹터 주식": [
            {
                "stock_name": "미국나스닥바이오",
                "isin": "KR7203780002",
                "market_value": 152484
            },
            {
                "stock_name": "미국S&P IT(합성)",
                "isin": "KR7200020006",
                "market_value": 57560
            }
        ],
        "선진국 주식": [
            {
                "stock_name": "선진국MSCI World",
                "isin": "KR7251350005",
                "market_value": 99470
            },
            {
                "stock_name": "일본니케이225",
                "isin": "KR7241180009",
                "market_value": 283184
            }
        ],
        "신흥국 주식": [
            {
                "stock_name": "베트남VN30",
                "isin": "KR7245710009",
                "market_value": 161712
            },
            {
                "stock_name": "신흥국MSCI",
                "isin": "KR7195980008",
                "market_value": 212595
            }
        ],
        "전세계 주식": [
            {
                "stock_name": "전세계MSCI",
                "isin": "KR7195980002",
                "market_value": 6130
            }
        ],
        "부동산 / 원자재": [
            {
                "stock_name": "WTI원유선물",
                "isin": "KR7261220008",
                "market_value": 282618
            },
            {
                "stock_name": "S&P글로벌인프라",
                "isin": "KR7130680002",
                "market_value": 103152
            }
        ],
        "채권 / 현금": [
            {
                "stock_name": "단기채권",
                "isin": "KR7153130000",
                "market_value": 151182
            },
            {
                "stock_name": "미국장기우량회사채",
                "isin": "KR7332620004",
                "market_value": 26637
            },
            {
                "stock_name": "현금",
                "isin": "CASH",
                "market_value": 24269
            }
        ]
    }
}
```

2) 500

```json
{
    "Message": 서버 에러가 발생하였습니다.
}
```

### 입금 phase1 API

요청 받은 투자금 입금 데이터를 sha512 방식으로 해시하여 랜덤으로 생성한 거래정보 식별자와 함께 db에 저장하고 거래정보 식별자를 리턴한다.

method : post

/api/transactions

Request Body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 계좌번호 | account_number | str |  |
| 고객명 | user_name | str |  |
| 거래 금액 | transfer_amount | int |  |

Request Example

```json
{
"account_number": "123123",
"user_name": "아이작",
"transfer_amount": 1000
}
```

Response_body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 거래 정보 식별자 | transfer_identifier | int |  |

HTTP status code

| HTTP status | AppErrors | 메시지 | 설명 |
| --- | --- | --- | --- |
| 201 | - |  | 정상종료 |
| 400 | Request Error | "리퀘스트 에러가 발생했습니다.” | Request Body 문제 |
| 500 | Internal Server Error | "서버 에러가 발생하였습니다.” | API 내부 에러 발생 |

Response Example

1) 200

```json
{
"transfer_identifier": 111
}
```

2) 400

```json
{
    "message": "리퀘스트 에러가 발생했습니다."
}
```

3) 500

```json
{
    "message": "서버 에러가 발생하였습니다."
}
```

### 입금 phase2 API

파라미터의 해싱된 거래 데이터와 거래정보 식별자를 가지고 있는 데이터가 db에 있는 경우 요청한 금액을 계좌의 투자원금과 현금자산에 반영하고 db의 거래 결과 테이블을 완료 상태로 변경한다.

method : put

/api/transactions

Request Body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 해싱된 거래 데이터 | signature | str |  |
| 거래정보 식별자 | transfer_identifier | int |  |

Request Example

```json
{
"signature": "82b64b05dfe897e1c2bce88a62467c084d79365af1", // "123123아이작1000" 을 sha512 hash 한 값.
"transfer_identifier": 111
}
```

Response_body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 거래 결과 | status | boolean |  |

HTTP status code

| HTTP status | AppErrors | 메시지 | 설명 |
| --- | --- | --- | --- |
| 200 | - |  | 정상종료 |
| 400 | Request Error | "인증에 실패했습니다.” | Request Body 문제 |
| 500 | Internal Server Error | "서버 에러가 발생하였습니다.” | API 내부 에러 발생 |

Response Example

1) 200

```json
{
"status": true
}
```

2) 400

```json
{
    "message": "인증에 실패했습니다."
}
```

3) 500

```json
{
    "message": "서버 에러가 발생하였습니다."
}
```

## unittest
<img width="452" alt="화면 캡처 2022-09-21 200021" src="https://user-images.githubusercontent.com/57758265/191487832-d4119419-fca8-4cdc-881c-ce606b280a66.png">

