#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import * as dotenv from 'dotenv';
import { DcpOpsMonitorStack } from '../lib/dcp-ops-monitor-stack';

dotenv.config({ path: '.env' });

const app = new cdk.App();
new DcpOpsMonitorStack(app, 'DcpOpsMonitorStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'ap-northeast-1',
  },
  logLevel: process.env.LOG_LEVEL || 'INFO',
  loginUrl: process.env.LOGIN_URL || 'https://www.nrkn.co.jp/rk/login.html',
  loginUserId: process.env.LOGIN_USER_ID || 'dummy-user-id',
  loginPassword: process.env.LOGIN_PASSWORD || 'dummy-password',
  loginBirthdate: process.env.LOGIN_BIRTHDATE || '19700101',
  userAgent:
    process.env.USER_AGENT ||
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
  line_message_api_url: process.env.LINE_MESSAGE_API_URL || 'https://api.line.me/v2/bot/message/broadcast',
  line_message_api_token: process.env.LINE_MESSAGE_API_TOKEN || 'dummy-line-token',
});
