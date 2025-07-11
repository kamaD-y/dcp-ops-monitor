import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { DcpOpsMonitorStack } from '../../lib/dcp-ops-monitor-stack';

test('Snapshot test for DcpOpsStatusNotificationStack', () => {
  const app = new cdk.App();
  // WHEN
  const stack = new DcpOpsMonitorStack(app, 'DcpOpsMonitorStack', {
    env: {
      account: process.env.CDK_DEFAULT_ACCOUNT,
      region: process.env.CDK_DEFAULT_REGION,
    },
    logLevel: 'INFO',
    startUrl: 'https://example.com/login',
    userAgent:
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    lineMessageApiUrl: 'https://api.line.me/v2/bot/message/broadcast',
    lineMessageApiToken: 'testLineToken',
    loginParameterName: '/dcp-ops-monitor/dummy-login-parameters',
  });
  // THEN
  expect(Template.fromStack(stack)).toMatchSnapshot();
});
