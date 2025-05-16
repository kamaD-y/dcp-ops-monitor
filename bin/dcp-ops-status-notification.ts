#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { DcpOpsMonitorStack } from '../lib/dcp-ops-status-notification-stack';

const app = new cdk.App();
new DcpOpsMonitorStack(app, 'DcpOpsMonitorStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'ap-northeast-1',
  },
  logLevel: process.env.LOG_LEVEL || 'INFO',
  loginUrl: process.env.LOGIN_URL || 'https://www.nrkn.co.jp/rk/login.html',
  userId: process.env.USER_ID || 'dummy-user-id',
  password: process.env.PASSWORD || 'dummy-password',
  birthdate: process.env.BIRTHDATE || '19700101',
  userAgent:
    process.env.USER_AGENT ||
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
});
