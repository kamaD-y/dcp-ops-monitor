#!/bin/bash

# 起動時にバケットを作成する
awslocal s3 mb s3://${ERROR_BUCKET_NAME}

# 起動時にParameterStoreにパラメータを登録する
awslocal ssm put-parameter --name ${SCRAPING_PARAMETER_NAME} --value ${SCRAPING_PARAMETER_VALUE} --type SecureString --overwrite
awslocal ssm put-parameter --name ${LINE_MESSAGE_PARAMETER_NAME} --value ${LINE_MESSAGE_PARAMETER_VALUE} --type SecureString --overwrite
