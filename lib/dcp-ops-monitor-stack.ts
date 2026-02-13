import * as path from 'node:path';
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
import * as ssm from 'aws-cdk-lib/aws-ssm';
import type { Construct } from 'constructs';

export interface DcpOpsMonitorStackProps extends cdk.StackProps {
  logLevel: string;
  userAgent: string;
  scrapingParameterName: string;
  spreadsheetParameterName: string;
  lineMessageParameterName: string;
}

export class DcpOpsMonitorStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: DcpOpsMonitorStackProps) {
    super(scope, id, props);

    // Parameter Store
    const scrapingParameter = ssm.StringParameter.fromSecureStringParameterAttributes(this, 'ScrapingParameter', {
      parameterName: props.scrapingParameterName,
    });
    const spreadsheetParameter = ssm.StringParameter.fromSecureStringParameterAttributes(this, 'SpreadsheetParameter', {
      parameterName: props.spreadsheetParameterName,
    });
    const lineMessageParameter = ssm.StringParameter.fromSecureStringParameterAttributes(this, 'LineMessageParameter', {
      parameterName: props.lineMessageParameterName,
    });

    // S3 Bucket
    const dataBucket = new s3.Bucket(this, 'DataBucket', {
      versioned: false,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Lambda Function用の LogGroup
    const logGroup = new logs.LogGroup(this, 'LogGroup', {
      retention: logs.RetentionDays.ONE_WEEK,
    });

    // Lambda Function
    const webScrapingFunction = new lambda.DockerImageFunction(this, 'webScrapingFunction', {
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../lambda'), {
        file: 'web-scraping/Dockerfile',
        extraHash: props.env?.region,
      }),
      memorySize: 1024,
      timeout: cdk.Duration.seconds(60),
      loggingFormat: lambda.LoggingFormat.JSON,
      logGroup: logGroup,
      applicationLogLevel: props.logLevel,
      environment: {
        POWERTOOLS_SERVICE_NAME: 'web-scraping',
        POWERTOOLS_LOG_LEVEL: props.logLevel,
        USER_AGENT: props.userAgent,
        SCRAPING_PARAMETER_NAME: scrapingParameter.parameterName,
        SPREADSHEET_PARAMETER_NAME: spreadsheetParameter.parameterName,
        DATA_BUCKET_NAME: dataBucket.bucketName,
      },
    });
    webScrapingFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['ssm:GetParameter'],
        resources: [scrapingParameter.parameterArn, spreadsheetParameter.parameterArn],
      }),
    );
    webScrapingFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['s3:PutObject'],
        resources: [`${dataBucket.bucketArn}/*`],
      }),
    );

    // 平日（月〜金）09:00 JST に実行する Rule を作成
    new events.Rule(this, 'EventRule', {
      schedule: events.Schedule.cron({
        minute: '0',
        hour: '0',
        weekDay: 'MON-FRI',
      }),
      targets: [new targets.LambdaFunction(webScrapingFunction)],
    });

    // サマリ通知用Lambda Function
    const summaryNotificationFunction = new lambda.Function(this, 'SummaryNotificationFunction', {
      runtime: lambda.Runtime.PYTHON_3_13,
      handler: 'src.handler.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../lambda'), {
        bundling: {
          image: cdk.DockerImage.fromRegistry('ghcr.io/astral-sh/uv:python3.13-bookworm-slim'),
          command: [
            'bash',
            '-c',
            [
              'export UV_CACHE_DIR=/tmp/uv-cache',
              'cd summary-notification',
              'uv export --no-hashes --no-dev --no-emit-workspace -o /tmp/requirements.txt',
              'pip install -r /tmp/requirements.txt -t /asset-output/',
              'cp -r src/ /asset-output/src/',
              'cp -r ../shared/src/shared /asset-output/shared/',
            ].join(' && '),
          ],
        },
      }),
      memorySize: 128,
      timeout: cdk.Duration.seconds(30),
      loggingFormat: lambda.LoggingFormat.JSON,
      logGroup: logGroup,
      applicationLogLevel: props.logLevel,
      environment: {
        POWERTOOLS_SERVICE_NAME: 'summary-notification',
        POWERTOOLS_LOG_LEVEL: props.logLevel,
        LINE_MESSAGE_PARAMETER_NAME: lineMessageParameter.parameterName,
        DATA_BUCKET_NAME: dataBucket.bucketName,
      },
    });
    summaryNotificationFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['s3:GetObject', 's3:ListBucket'],
        resources: [dataBucket.bucketArn, `${dataBucket.bucketArn}/*`],
      }),
    );
    summaryNotificationFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['ssm:GetParameter'],
        resources: [lineMessageParameter.parameterArn],
      }),
    );

    // 毎週日曜 09:00 JST に実行する Rule を作成
    new events.Rule(this, 'SummaryNotificationEventRule', {
      schedule: events.Schedule.cron({
        minute: '0',
        hour: '0',
        weekDay: 'SUN',
      }),
      targets: [new targets.LambdaFunction(summaryNotificationFunction)],
    });

    // エラー通知用 SNS Topic
    const errorAlarmTopic = new sns.Topic(this, 'ErrorAlarmTopic', {
      displayName: 'DCP Ops Monitor Error Alarm',
    });

    // Lambda エラーメトリクス Alarm
    const webScrapingErrorAlarm = new cloudwatch.Alarm(this, 'WebScrapingErrorAlarm', {
      metric: webScrapingFunction.metricErrors({
        period: cdk.Duration.minutes(5),
      }),
      threshold: 1,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
      alarmDescription: 'web-scraping Lambda でエラーが発生しました',
    });
    webScrapingErrorAlarm.addAlarmAction(new cw_actions.SnsAction(errorAlarmTopic));

    const summaryNotificationErrorAlarm = new cloudwatch.Alarm(this, 'SummaryNotificationErrorAlarm', {
      metric: summaryNotificationFunction.metricErrors({
        period: cdk.Duration.minutes(5),
      }),
      threshold: 1,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
      alarmDescription: 'summary-notification Lambda でエラーが発生しました',
    });
    summaryNotificationErrorAlarm.addAlarmAction(new cw_actions.SnsAction(errorAlarmTopic));
  }
}
