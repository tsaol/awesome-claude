from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.storage import S3
from diagrams.aws.network import ALB
from diagrams.aws.ml import Bedrock
from diagrams.aws.analytics import Quicksight
from diagrams.aws.management import SystemsManager
from diagrams.aws.general import User

output_path = "/home/ubuntu/codes/awesome-claude/skills/aws-diagram/aws-infrastructure"

with Diagram("AWS Infrastructure", filename=output_path, show=False, direction="TB", outformat="png"):

    user = User("Developer")
    ssm = SystemsManager("SSM")

    with Cluster("us-west-2 (Oregon)"):
        s3_cls = S3("cls-laptop\n(S3)")
        bedrock = Bedrock("Bedrock\n(Claude/Nova)")

        with Cluster("OpenClaw"):
            openclaw_oregon = EC2("OpenClaw\ni-08b22ac")

        with Cluster("LiteLLM Proxy"):
            litellm = EC2("LiteLLM\ni-0bba132\nlitellm.xcaoliu.com")

    with Cluster("ap-northeast-1 (Tokyo)"):
        s3_lang = S3("cls-languages\n(S3)")

        with Cluster("EngLearn"):
            englearn = EC2("EngLearn\ni-0f86894")
            englearn_db = RDS("SQLite DB")

        with Cluster("OpenClaw Mac"):
            openclaw_mac = EC2("Mac mini\ni-0f7aa36\nmac1.metal")

        with Cluster("Spot GPU (Ollama)"):
            alb = ALB("Private ALB\n:11434")
            spot_gpu = EC2("g6e.xlarge Spot\nL40S 48GB\nQwen 35B")

    with Cluster("us-east-1 (Virginia)"):
        quicksight = Quicksight("QuickSight\nEnterprise")

    # Connections
    user >> ssm >> [openclaw_oregon, englearn, openclaw_mac, litellm]

    openclaw_oregon >> Edge(label="API") >> litellm
    openclaw_mac >> Edge(label="API") >> litellm
    litellm >> Edge(label="Converse API") >> bedrock

    englearn >> Edge(label="inference") >> alb >> spot_gpu
    englearn >> Edge(label="backup") >> s3_lang
    englearn >> englearn_db

    openclaw_oregon >> Edge(label="store") >> s3_cls
