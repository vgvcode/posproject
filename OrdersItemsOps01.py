from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
import sys

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

if len(sys.argv) != 2:
    print("Usage: python3 {} local|remote".format(sys.argv[0]))
    sys.exit(1)

if sys.argv[1] == "remote":
    endpoint = "https://dynamodb.us-east-1.amazonaws.com"
else:
    endpoint = "http://localhost:8000"

#endpoint = "https://dynamodb.us-east-1.amazonaws.com"
#endpoint = "http://localhost:8000"

tableName = "orders"

dynamodb = boto3.resource('dynamodb',endpoint_url=endpoint)

table = dynamodb.Table(tableName)

posID = 'posMountRoadOfficeFirstFloorChennai'
orderID = '12345' 

response = table.put_item(
   Item={
        'PosID': posID,
        'OrderID': orderID,
        'Info': {
            'CreatedTime': '05Oct2016',
            'UpdatedTime': '06Oct2016',
            'ListOfItems': [
                            {'id': 21, 'name': 'IDLI', 'price': 25, 'quantity': 3, 'amount': 75},
                            {'id': 21, 'name': 'DOSAI`', 'price': decimal.Decimal(40.50), 'quantity': 1, 'amount': decimal.Decimal(40.50)}
                           ],
            'Gross': decimal.Decimal(1500),
            'Tax': decimal.Decimal(150),
            'Net': decimal.Decimal(1650)
        }
    }
)

print("PutItem succeeded:")
print(json.dumps(response, indent=4, cls=DecimalEncoder))
