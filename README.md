[![](https://img.shields.io/badge/Python-3.8-green)](https://www.python.org/) [![](https://img.shields.io/badge/AWS-API%20Gateway-blue)](https://aws.amazon.com/api-gateway/) [![](https://img.shields.io/badge/AWS-Lambda-blue)](https://aws.amazon.com/lambda/) [![](https://img.shields.io/badge/AWS-RDS-blue)](https://aws.amazon.com/rds/)

# GoogleNewsStore

This simple Lambda function allows you to search store and retrieve Google news articles.

The aws-cli commands to set up the API Gateway and RDS setup will be added when I get some spare time. If you would like to see a live demonstration of the code, contact me on telegram at [@sreejeet](https://telegram.me/sreejeet)

This function uses a very peculiar routing based on the event resource (API Gateway resource) that was used to call this function. This routing was implemented as an experiement and does show some really good potential to reduce the overall number of functions to be deployed and redundant 3rd party modules/libraries.

## Tech stack

1. Python 3.8
2. AWS RDS (MySQL)
3. AWS Lambda
4. AWS API Gateway

## Some useful resources

1. https://docs.aws.amazon.com/lambda/latest/dg/configuration-database.html
2. https://aws.amazon.com/blogs/compute/using-amazon-rds-proxy-with-aws-lambda/
3. https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/rds-proxy.html#rds-proxy.howitworks
4. https://docs.aws.amazon.com/lambda/latest/dg/services-rds-tutorial.html
