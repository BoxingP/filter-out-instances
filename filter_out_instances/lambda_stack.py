from aws_cdk import (
    aws_iam as iam,
    aws_lambda as _lambda,
    core as cdk
)


class LambdaStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        publish_logs_to_cloudwatch = iam.ManagedPolicy(self, 'PublishLogsPolicy',
                                                       managed_policy_name='-'.join(
                                                           [construct_id, 'publish logs policy'.replace(' ', '-')]
                                                       ),
                                                       description='Policy to operate EC2 instances',
                                                       statements=[
                                                           iam.PolicyStatement(
                                                               sid='AllowPublishLogsToCloudwatch',
                                                               actions=[
                                                                   'logs:CreateLogGroup',
                                                                   'logs:CreateLogStream',
                                                                   'logs:PutLogEvents'
                                                               ],
                                                               resources=['arn:aws-cn:logs:*:*:*']
                                                           )
                                                       ]
                                                       )
        operating_ec2_policy = iam.ManagedPolicy(self, 'OperatingEC2Policy',
                                                 managed_policy_name='-'.join(
                                                     [construct_id, 'operating ec2 policy'.replace(' ', '-')]
                                                 ),
                                                 description='Policy to operate EC2 instances',
                                                 statements=[
                                                     iam.PolicyStatement(
                                                         sid='AllowDescribeEC2Instances',
                                                         actions=['ec2:DescribeInstances'],
                                                         resources=['*']
                                                     )
                                                 ]
                                                 )
        operating_rds_policy = iam.ManagedPolicy(self, 'OperatingRDSPolicy',
                                                 managed_policy_name='-'.join(
                                                     [construct_id, 'operating rds policy'.replace(' ', '-')]
                                                 ),
                                                 description='Policy to operate RDS instances',
                                                 statements=[
                                                     iam.PolicyStatement(
                                                         sid='AllowDescribeRDSInstances',
                                                         actions=['rds:DescribeDBInstances'],
                                                         resources=['arn:aws-cn:rds:*:*:db:*']
                                                     )
                                                 ]
                                                 )

        lambda_role = iam.Role(self, 'LambdaRole',
                               assumed_by=iam.ServicePrincipal('lambda.amazonaws.com.cn'),
                               description="IAM role for Lambda function",
                               managed_policies=[
                                   publish_logs_to_cloudwatch,
                                   operating_ec2_policy,
                                   operating_rds_policy
                               ],
                               role_name='-'.join([construct_id, 'role'.replace(' ', '-')]),
                               )
        lambda_function = _lambda.Function(self, 'LambdaFunction',
                                           code=_lambda.Code.from_asset(path="./filter_out_instances/lambda"),
                                           handler="filter_out_instances.lambda_handler",
                                           runtime=_lambda.Runtime.PYTHON_3_8,
                                           memory_size=128,
                                           role=lambda_role,
                                           timeout=cdk.Duration.seconds(900)
                                           )
        lambda_function.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        cdk.CfnOutput(self, 'OutputLambdaName',
                      export_name='-'.join([construct_id, 'lambda name'.replace(' ', '-')]),
                      value=lambda_function.function_name)
        cdk.CfnOutput(self, 'OutputLambdaARN',
                      export_name='-'.join([construct_id, 'lambda arn'.replace(' ', '-')]),
                      value=lambda_function.function_arn)
