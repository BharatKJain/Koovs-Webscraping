import pandas as pd
import json
import ast
categoryData = pd.read_csv('dataSet.csv')
dictData = {}
productDetails = {}
for category in categoryData.iloc[:, [9]].values:
    # dictData = json.loads(category[0].replace("'", '"'))
    dictData = ast.literal_eval(category[0])

    if dictData.get('Info & Care') is not None:
        productDetails['Info & Care'] = dictData.get('Info & Care')
    else:
        productDetails['Info & Care'] = "null"
    if dictData.get('Style Tips') is not None:
        productDetails['Style Tips'] = dictData.get('Style Tips')
    else:
        productDetails['Style Tips'] = "null"
    if dictData.get('Delivery & Return') is not None:
        productDetails['Delivery & Return'] = dictData.get('Delivery & Return')
    else:
        productDetails['Delivery & Return'] = "null"
    if dictData.get('Seller Details') is not None:
        productDetails['Seller Details'] = dictData.get('Seller Details')
    else:
        productDetails['Seller Details'] = "null"

    data = pd.DataFrame(productDetails, index=[0])
    data.to_csv('newDetails.csv', mode='a', header=False)
