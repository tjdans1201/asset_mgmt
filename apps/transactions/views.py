from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Transaction
from apps.assets.models import Account, StockSheld
from .serializers import TransactionSerializer
import random
import hashlib


def validate_post(request_body):
    """
    파라미터 타입 체크
    """
    flg = False
    if all(
        i in request_body for i in ("account_number", "user_name", "transfer_amount")
    ):
        if (
            type(request_body["account_number"]) is str
            and type(request_body["user_name"]) is str
            and type(request_body["transfer_amount"]) is int
        ):
            flg = True
    return flg


def validate_put(request_body):
    """
    파라미터 타입 체크
    """
    flg = False
    if all(i in request_body for i in ("signature", "transfer_identifier")):
        if (
            type(request_body["signature"]) is str
            and type(request_body["transfer_identifier"]) is int
        ):
            flg = True
    return flg


# Create your views here.
class TransactionsAPI(APIView):
    def post(self, request):
        """
        입금 거래 정보들을 서버에 등록
        요청 데이터 계좌번호, 고객명, 거래 금액 순서로 연결한 string 을 hash해서 db에 등록
        랜덤으로 4자리의 거래정보 식별자를 생성하여 db에 등록
        args:
            request.data : {
                            "account_number": "str",
                            "user_name": "str",
                            "transfer_amount": int
                            }

        Returns: {"transfer_identifier": int}
        """
        try:
            request_body = request.data
            # 파라미터 체크
            if validate_post(request_body) == False:
                return Response(
                    {"message": "리퀘스트 에러가 발생했습니다."}, status=status.HTTP_400_BAD_REQUEST
                )
            # 요청한 거래정보 hash
            request_body["transaction_signature"] = hashlib.sha512(
                (
                    request_body["account_number"]
                    + request_body["user_name"]
                    + str(request_body["transfer_amount"])
                ).encode("utf-8")
            ).hexdigest()
            # 랜덤으로 4자리의 거래정보 식별자를 생성
            request_body["transfer_identifier"] = random.randint(1000, 9999)
            serializer = TransactionSerializer(data=request_body)
            # 거래정보를 등록
            if serializer.is_valid():
                serializer.save()
                result = {"transfer_identifier": request_body["transfer_identifier"]}
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"message": "리퀘스트 에러가 발생했습니다."}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print(e)
            return Response(
                {"message": "서버 에러가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):
        """
        등록된 거래정보를 검증하고 실제 고객의 자산을 업데이트
        등록한 거래정보를 해싱한 값과 db에 등록된 값과 거래정보 식별자가 같으면 검증 성공
        검증에 성공하면 투자원금과 현금자산을 업데이트하고 해당 거래정보도 업데이트
        args:
            request.data : {
                            "signature": str, // 거래 데이터를 sha512 hash 한 값.
                            "transfer_identifier": int
                            }
        Returns: {"status": True}

        """
        try:
            request_body = request.data
            if validate_put(request_body) == False:
                return Response(
                    {"message": "리퀘스트 에러가 발생했습니다."}, status=status.HTTP_400_BAD_REQUEST
                )
            # 입력받은 정보로 등록된 거래정보를 취득
            transaction = Transaction.objects.filter(
                transaction_signature=request_body["signature"].lower(),
                transfer_identifier=request_body["transfer_identifier"],
                is_finish=False,
            )
            if transaction:
                # 해당 거래정보가 있으면 해당 계좌정보를 취득
                account = Account.objects.filter(
                    account_holder=transaction[0].user_name,
                    account_number=str(transaction[0].account_number),
                )
                if account:
                    # 계좌가 있는 경우 투자원금과 현금자산을 업데이트
                    stocksheld = StockSheld.objects.get(
                        account_id=account[0].id, stock_id=14
                    )
                    stocksheld.current_price += transaction[0].transfer_amount
                    stocksheld.save()
                    account[0].investment_principal += transaction[0].transfer_amount
                    account[0].save()
                    transaction[0].is_finish = True
                    transaction[0].save()
                    result = {"status": True}
                    return Response(result, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"message": "존재하지 않는 계좌입니다."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {"message": "인증에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print(e)
            return Response(
                {"message": "서버 에러가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
