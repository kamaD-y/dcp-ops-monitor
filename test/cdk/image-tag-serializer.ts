module.exports = {
  test: (val: unknown) => typeof val === 'string',
  serialize: (val: unknown) => {
    if (typeof val !== 'string') {
      return;
    }
    const regex1 =
      /(\${AWS::AccountId}\.dkr\.ecr\.\${AWS::Region}\.\${AWS::URLSuffix}\/cdk-hnb659fds-container-assets-\${AWS::AccountId}-\${AWS::Region}:)(\w+)/;
    const regex2 = /([A-Fa-f0-9]{64}.zip)/;
    return `"${val.replace(regex1, '$1[Image Tag]').replace(regex2, '[Hash Id].zip')}"`;
  },
};
