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
  userAgent:
    process.env.USER_AGENT ||
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
  /* NOTE: CDK で暗号化文字列を使用したパラメータを作成できない為、以下3つのパラメータを手動で事前に作成します。
    $ aws ssm put-parameter \
       --name "/dcp-ops-monitor/scraping-parameters" \
       --value '{"start_url": "https://xxx", "login_user_id":"xxxx","login_password":"xxxx","login_birthdate":"19701201"}' \
       --type "SecureString"

    $ aws ssm put-parameter \
       --name "/dcp-ops-monitor/spreadsheet-parameters" \
       --value '{"spreadsheet_id": "xxx", "sheet_name": "xxx", "credentials": {"type": "service_account", ...}}' \
       --type "SecureString"

    $ aws ssm put-parameter \
       --name "/dcp-ops-monitor/line-message-parameters" \
       --value '{"url": "https://xxx", "token": "xxx"}' \
       --type "SecureString"
   */
  scrapingParameterName: '/dcp-ops-monitor/scraping-parameters',
  spreadsheetParameterName: '/dcp-ops-monitor/spreadsheet-parameters',
  lineMessageParameterName: '/dcp-ops-monitor/line-message-parameters',
});
