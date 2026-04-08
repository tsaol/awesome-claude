---
name: aws-diagram
description: >
  Generate AWS architecture diagrams and system topology diagrams using the Python Diagrams library.
  Use this skill when the user asks to:
  - Create an AWS architecture diagram
  - Generate a system topology diagram
  - Visualize cloud infrastructure
  - Draw network diagrams with AWS services
  - Create deployment architecture visuals
  The LLM generates Python code using the Diagrams library, then executes it to render PNG images.
license: MIT
---

# AWS Architecture Diagram Generator

Generate professional AWS architecture and system topology diagrams from natural language descriptions. Uses the Python [Diagrams](https://diagrams.mingrammer.com/) library to produce clean, consistent PNG images.

## Usage

```
/aws-diagram <architecture description>
/aws-diagram A three-tier web app with ALB, ECS Fargate, and Aurora PostgreSQL
/aws-diagram VPC with public/private subnets, NAT gateway, and S3 endpoint
```

## Execution Flow

### Step 1: Understand the Architecture

Parse the user's description and identify:
- **AWS Services** involved (EC2, S3, RDS, Lambda, etc.)
- **Relationships** between services (data flow, network connections)
- **Groupings** (VPCs, subnets, availability zones, regions)
- **Direction** of data flow (left-to-right, top-to-bottom)

### Step 2: Generate Python Code

Write Python code using the `diagrams` library. Follow these rules:

**Import Convention:**
```python
from diagrams import Diagram, Cluster, Edge
# Import specific AWS service nodes
from diagrams.aws.compute import EC2, ECS, Lambda, Fargate
from diagrams.aws.database import RDS, Aurora, DynamoDB, ElastiCache
from diagrams.aws.network import ELB, ALB, NLB, CloudFront, Route53, VPC, PrivateSubnet, PublicSubnet, NATGateway, InternetGateway
from diagrams.aws.storage import S3
from diagrams.aws.integration import SQS, SNS, Eventbridge
from diagrams.aws.analytics import Kinesis, Glue, Athena
from diagrams.aws.security import IAM, WAF, KMS, CertificateManager
from diagrams.aws.management import Cloudwatch, SystemsManager
from diagrams.aws.ml import Sagemaker, Bedrock
# ... import as needed
```

**Code Structure:**
```python
from diagrams import Diagram, Cluster, Edge

# Output to skill directory
output_path = "/home/ubuntu/codes/awesome-claude/skills/aws-diagram/<filename>"

with Diagram("<Title>", filename=output_path, show=False, direction="TB"):
    # Use Cluster for groupings (VPC, subnet, AZ, etc.)
    with Cluster("VPC"):
        with Cluster("Public Subnet"):
            # service nodes
            pass
        with Cluster("Private Subnet"):
            # service nodes
            pass

    # Define connections
    # service_a >> service_b          (simple connection)
    # service_a >> Edge(label="HTTPS") >> service_b  (labeled connection)
    # service_a << service_b          (reverse direction)
```

**Diagram Parameters:**
- `show=False` — always set, don't open image viewer
- `direction` — "TB" (top-bottom, default), "LR" (left-right), "BT", "RL"
- `filename` — always use absolute path under output directory
- `outformat` — default "png", can use "jpg", "svg", "pdf"

**Best Practices:**
- Use `Cluster` for logical groupings (VPC, Subnet, AZ, Region, Service Group)
- Use `Edge(label="...")` to annotate data flows
- Use `Edge(color="...")` to distinguish different flow types (red for errors, blue for data, green for success)
- Keep diagrams readable — max 15-20 nodes per diagram
- For complex architectures, split into multiple diagrams
- Use meaningful variable names that match the service purpose

### Step 3: Execute and Render

```bash
# Run the generated Python script
python3 /home/ubuntu/codes/awesome-claude/skills/aws-diagram/<filename>.py
```

### Step 4: Return Result

After rendering, report:
- The output PNG file path
- A brief description of what the diagram shows
- Read the generated image to verify it rendered correctly

## Output Directory

All generated diagrams (`.py` source + `.png` output) are saved to:
```
/home/ubuntu/codes/awesome-claude/skills/aws-diagram/
```

File naming convention: `<descriptive-name>.png`
Examples: `three-tier-web-app.png`, `data-pipeline.png`, `vpc-network.png`

## Available Node Types

### Compute
`EC2, ECS, Fargate, Lambda, Batch, ElasticBeanstalk, Lightsail, AppRunner`

### Database
`RDS, Aurora, DynamoDB, ElastiCache, Neptune, Redshift, DocumentDB, MemoryDB, Timestream`

### Network
`VPC, ALB, NLB, ELB, CloudFront, Route53, APIGateway, PrivateSubnet, PublicSubnet, NATGateway, InternetGateway, DirectConnect, TransitGateway, VPCPeering, Endpoint`

### Storage
`S3, EFS, FSx, EBS, Backup`

### Integration
`SQS, SNS, Eventbridge, StepFunctions, MQ, AppSync`

### Analytics
`Kinesis, Glue, Athena, EMR, Opensearch, QuickSight, LakeFormation, MSK`

### Security
`IAM, WAF, Shield, KMS, SecretsManager, CertificateManager, Cognito, GuardDuty, Inspector, SecurityHub`

### Management
`Cloudwatch, CloudTrail, SystemsManager, Config, Organizations, CloudFormation`

### ML
`Sagemaker, Bedrock, Comprehend, Rekognition, Textract, Translate, Polly, Transcribe, Lex`

### Others
`diagrams.aws.cost.CostExplorer`
`diagrams.aws.devtools.CodeBuild, CodePipeline, CodeDeploy, CodeCommit`
`diagrams.aws.mobile.Amplify`
`diagrams.aws.general.User, Users, Client`

For the full list, see: https://diagrams.mingrammer.com/docs/nodes/aws

## Non-AWS Providers

The Diagrams library also supports other providers for hybrid/multi-cloud diagrams:

- `diagrams.onprem` — On-premise (Docker, Kubernetes, Nginx, etc.)
- `diagrams.gcp` — Google Cloud Platform
- `diagrams.azure` — Microsoft Azure
- `diagrams.k8s` — Kubernetes resources
- `diagrams.generic` — Generic nodes (database, compute, etc.)

## Examples

### Three-Tier Web App

```
/aws-diagram A three-tier web application: Route53 DNS pointing to CloudFront CDN, 
then ALB distributing to ECS Fargate containers in two AZs, 
backed by Aurora PostgreSQL with a read replica
```

### Serverless Data Pipeline

```
/aws-diagram A serverless data pipeline: S3 triggers Lambda for processing, 
results go to DynamoDB, with SQS for dead letter queue and 
CloudWatch for monitoring
```

### VPC Network Layout

```
/aws-diagram VPC with two AZs, each with public and private subnets. 
Public subnets have NAT gateways and ALB. Private subnets have 
ECS tasks and RDS. S3 VPC endpoint for storage access.
```

## Troubleshooting

### Import Errors

If a specific node class doesn't exist, check the diagrams library version:
```bash
python3 -c "import diagrams; print(diagrams.__version__)"
```

Some newer AWS services may not have dedicated node classes. Use `diagrams.aws.general.General` with a custom label as fallback.

### Graphviz Errors

The `diagrams` library requires `graphviz` system package:
```bash
# Should already be installed
which dot
# If not:
sudo apt-get install -y graphviz
```

### Large Diagrams

For complex architectures with 20+ nodes, consider:
1. Splitting into multiple diagrams (network view, data flow view, security view)
2. Using `direction="LR"` for wide architectures
3. Grouping related services in Clusters to reduce visual noise
