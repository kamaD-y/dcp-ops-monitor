#!/bin/bash

# 起動時にバケットを作成する
awslocal s3 mb s3://${ERROR_BUCKET_NAME}

# 起動時にParameterStoreにパラメータを登録する
awslocal ssm put-parameter --name ${LOGIN_PARAMETER_NAME} --value ${LOGIN_PARAMETER_VALUE} --type SecureString --overwrite
awslocal ssm put-parameter --name ${LINE_MESSAGE_PARAMETER_NAME} --value ${LINE_MESSAGE_VALUE} --type SecureString --overwrite

# 起動時にSNSトピックを作成する
awslocal sns create-topic --name ${SNS_TOPIC_NAME}
