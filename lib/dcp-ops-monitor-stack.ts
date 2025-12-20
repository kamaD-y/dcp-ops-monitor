import * as path from 'node:path';
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import * as cdk from 'aws-cdk-lib';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import type { Construct } from 'constructs';

export interface DcpOpsMonitorStackProps extends cdk.StackProps {
  logLevel: string;
  startUrl: string;
  userAgent: string;
  loginParameterName: string;
  lineMessageTokenParameterName: string;
}

export class DcpOpsMonitorStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: DcpOpsMonitorStackProps) {
    super(scope, id, props);

    // Parameter Store
    const loginParametersForScraping = ssm.StringParameter.fromSecureStringParameterAttributes(
      this,
      'LoginParametersForScraping',
      {
        parameterName: props.loginParameterName,
      },
    );
    const lineMessageTokenParameter = ssm.StringParameter.fromSecureStringParameterAttributes(
      this,
      'LineMessageTokenParameter',
      {
        parameterName: props.lineMessageTokenParameterName,
      },
    );

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
    const webScrapingFunction = new lambda.DockerImageFunction(this, 'webScrapingFunction', {
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../lambda/web-scraping'), {
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
        START_URL: props.startUrl,
        USER_AGENT: props.userAgent,
        LOGIN_PARAMETER_NAME: loginParametersForScraping.parameterName,
        LINE_MESSAGE_PARAMETER_NAME: lineMessageTokenParameter.parameterName,
        ERROR_BUCKET_NAME: errorBucket.bucketName,
      },
    });
    webScrapingFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['ssm:GetParameter'],
        resources: [loginParametersForScraping.parameterArn, lineMessageTokenParameter.parameterArn],
      }),
    );
    webScrapingFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['s3:PutObject'],
        resources: [`${errorBucket.bucketArn}/*`],
      }),
    );

    // LINE通知用Lambda Function
    const errorNotificationFunction = new PythonFunction(this, 'ErrorNotificationFunction', {
      runtime: lambda.Runtime.PYTHON_3_13,
      entry: path.join(__dirname, '../lambda/error-notification'),
      index: 'src/handler.py',
      handler: 'handler',
      bundling: {
        assetExcludes: ['.venv'],
      },
      environment: {
        POWERTOOLS_LOG_LEVEL: props.logLevel,
        LINE_MESSAGE_API_URL: '',
        LINE_MESSAGE_API_TOKEN: '',
      },
    });
    errorNotificationFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['s3:GetObject'],
        resources: [`${errorBucket.bucketArn}/*`],
      }),
    );
    // 毎週月曜日 09:00 に実行する Rule を作成
    new events.Rule(this, 'EventRule', {
      schedule: events.Schedule.cron({
        minute: '0',
        hour: '0',
        weekDay: 'MON',
      }),
      targets: [new targets.LambdaFunction(webScrapingFunction)],
    });
  }
}
