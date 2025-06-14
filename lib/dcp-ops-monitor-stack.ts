import * as path from 'node:path';
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import * as cdk from 'aws-cdk-lib';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as cw_actions from 'aws-cdk-lib/aws-cloudwatch-actions';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as sns_subs from 'aws-cdk-lib/aws-sns-subscriptions';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import type { Construct } from 'constructs';

export interface DcpOpsMonitorStackProps extends cdk.StackProps {
  logLevel: string;
  loginUrl: string;
  userAgent: string;
  lineMessageApiUrl: string;
  lineMessageApiToken: string;
}

export class DcpOpsMonitorStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: DcpOpsMonitorStackProps) {
    super(scope, id, props);

    // Parameter Store
    const loginParametersForScraping = ssm.StringParameter.fromSecureStringParameterAttributes(
      this,
      'LoginParametersForScraping',
      {
        parameterName: '/dcp-ops-monitor/login-parameters-for-scraping',
      },
    );

    // SNS Topic
    const successTopic = new sns.Topic(this, 'SuccessTopic', {});
    const failureTopic = new sns.Topic(this, 'FailureTopic', {});

    // S3 Bucket
    const errorBucket = new s3.Bucket(this, 'ErrorBucket', {
      versioned: false,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Lambda Function用の LogGroup
    const logGroup = new logs.LogGroup(this, 'LogGroup', {
      retention: logs.RetentionDays.ONE_WEEK,
    });

    // Lambda Function
    const etlFunction = new lambda.DockerImageFunction(this, 'ETLFunction', {
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../lambda/dcp_etl'), {
        file: 'Dockerfile',
        extraHash: props.env?.region,
      }),
      memorySize: 1024,
      timeout: cdk.Duration.seconds(60),
      loggingFormat: lambda.LoggingFormat.JSON,
      logGroup: logGroup,
      applicationLogLevel: props.logLevel,
      environment: {
        POWERTOOLS_LOG_LEVEL: props.logLevel,
        LOGIN_URL: props.loginUrl,
        USER_AGENT: props.userAgent,
        LOGIN_PARAMETER_ARN: loginParametersForScraping.parameterArn,
        SNS_TOPIC_ARN: successTopic.topicArn,
        ERROR_BUCKET_NAME: errorBucket.bucketName,
      },
    });
    etlFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['ssm:GetParameter'],
        resources: [loginParametersForScraping.parameterArn],
      }),
    );
    etlFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['sns:Publish'],
        resources: [successTopic.topicArn],
      }),
    );
    etlFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['s3:PutObject'],
        resources: [`${errorBucket.bucketArn}/*`],
      }),
    );

    // LINE通知用Lambda Function
    const notificationFunction = new PythonFunction(this, 'NotificationFunction', {
      runtime: lambda.Runtime.PYTHON_3_13,
      entry: path.join(__dirname, '../lambda/dcp_notification'),
      index: 'src/handler.py',
      handler: 'handler',
      bundling: {
        assetExcludes: ['.venv'],
      },
      environment: {
        POWERTOOLS_LOG_LEVEL: props.logLevel,
        LINE_MESSAGE_API_URL: props.lineMessageApiUrl,
        LINE_MESSAGE_API_TOKEN: props.lineMessageApiToken,
      },
    });

    notificationFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['logs:DescribeMetricFilters'],
        resources: ['*'],
      }),
    );

    notificationFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['logs:FilterLogEvents'],
        resources: [logGroup.logGroupArn],
      }),
    );

    // SNS Topic に LINE通知用Lambda Function をサブスクライブ
    successTopic.addSubscription(new sns_subs.LambdaSubscription(notificationFunction));
    failureTopic.addSubscription(new sns_subs.LambdaSubscription(notificationFunction));

    // 毎週月曜日 09:00 に実行する Rule を作成
    new events.Rule(this, 'EventRule', {
      schedule: events.Schedule.cron({
        minute: '0',
        hour: '0',
        weekDay: 'MON',
      }),
      targets: [new targets.LambdaFunction(etlFunction)],
    });

    // Lambda Functionエラーログ検知用の MetricFilter を作成
    const etlFunctionMetricFilter = etlFunction.logGroup.addMetricFilter('ETLFunctionErrorLogFilter', {
      filterPattern: logs.FilterPattern.all(logs.FilterPattern.stringValue('$.level', '=', 'ERROR')),
      metricNamespace: 'Custom/DcpOpsMonitor',
      metricName: 'ETLFunctionErrorLog',
      metricValue: '1',
    });

    // MetricFilter に対する CloudWatchAlarm を作成
    etlFunctionMetricFilter
      .metric({
        statistic: cloudwatch.Stats.SUM,
      })
      .createAlarm(this, 'ETLFunctionErrorLogAlarm', {
        threshold: 1,
        evaluationPeriods: 1,
        alarmName: 'ETLFunctionErrorLogAlarm',
        comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      })
      .addAlarmAction(new cw_actions.SnsAction(failureTopic));
  }
}
