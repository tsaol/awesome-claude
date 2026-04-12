---
name: aws-diagram
description: "Generate AWS architecture diagrams in draw.io format following the awslabs official style. Supports PNG/SVG export via draw.io CLI and automated 6-point quality validation. Use when the user asks to create, update, or export an AWS architecture diagram."
license: Apache-2.0
---

# AWS Architecture Diagram Generator

Generate professional AWS architecture diagrams in draw.io XML format, following the [awslabs/agent-plugins](https://github.com/awslabs/agent-plugins) official style specification.

## Capabilities

- Generate `.drawio` files with proper AWS service icons (`mxgraph.aws4.*`)
- Export to PNG/SVG/PDF via draw.io CLI
- Run automated 6-point quality validation
- Support light/dark mode adaptive colors

## Usage

```
/aws-diagram <description of the architecture>
```

Examples:
```
/aws-diagram A serverless API with Lambda, API Gateway, DynamoDB, and S3
/aws-diagram Three-tier web app with ALB, ECS Fargate, Aurora, and ElastiCache
/aws-diagram ML pipeline with SageMaker Training, Model Registry, and S3
```

## Output

The skill produces:
1. `architecture.drawio` - Editable draw.io XML file
2. `architecture.png` - Exported PNG image (if draw.io CLI is installed)
3. Quality check report (6/6 must pass)

## Workflow

### Step 1: Gather Requirements

Ask the user (or infer from context):
- Which AWS services are involved?
- What is the data flow between them?
- Are there external actors (users, on-premises, third-party)?
- Any specific grouping (VPC, subnets, regions)?

### Step 2: Generate draw.io XML

Write the `.drawio` file following the format specification below.

### Step 3: Validate

Run the quality check script:
```bash
python3 skills/aws-diagram/scripts/validate_drawio.py <file.drawio>
```

All 6 checks must pass before delivery.

### Step 4: Export PNG

```bash
# Install draw.io CLI (one-time)
wget https://github.com/jgraph/drawio-desktop/releases/download/v26.2.2/drawio-amd64-26.2.2.deb -O /tmp/drawio.deb
sudo dpkg -i /tmp/drawio.deb && sudo apt-get install -f -y

# Export
xvfb-run drawio --export --format png --border 10 --output output.png input.drawio
```

---

## Quality Check Rules (6 Points)

Every generated diagram MUST pass all 6 checks:

| # | Rule | What to Check |
|---|------|---------------|
| 1 | **AWS Cloud boundary** | `mxgraph.aws4.group_aws_cloud` group present; external actors (Users) positioned outside; all AWS services positioned inside |
| 2 | **No crossing lines** | All edges use `orthogonalEdgeStyle`; query edges and registration edges exit at different Y positions; registration edges route around services via explicit waypoints (>= 3 waypoints) |
| 3 | **Clear hierarchy** | Elements follow left-to-right (or top-to-bottom) flow with increasing x (or y) coordinates |
| 4 | **Color-coded edges** | Different edge types use distinct visual styles: solid for synchronous, dashed for async/optional, open-arrow for data flow |
| 5 | **All API calls labeled** | Every edge representing an API call has a label with the method name |
| 6 | **No emojis** | No emoji characters in any diagram element values |

---

## Draw.io XML Format Specification

### XML Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile>
  <diagram name="Architecture" id="arch">
    <mxGraphModel dx="2200" dy="900" grid="0" guides="1" tooltips="1"
      connect="1" arrows="1" fold="1" page="0" pageScale="1"
      pageWidth="2100" pageHeight="900">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- All content here -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

Page sizing:
- Small (3-5 services): `pageWidth="800" pageHeight="600"`
- Medium (6-12 services): `pageWidth="1169" pageHeight="827"`
- Large (13+): `pageWidth="1600" pageHeight="1200"`
- Add ~600px width for legend panel

### Title Block

```xml
<mxCell id="title-group" connectable="0" style="group;fontFamily=Helvetica;" value="" vertex="1" parent="1">
  <mxGeometry x="50" y="30" width="1200" height="83" as="geometry" />
</mxCell>
<mxCell id="title-text" style="text;html=1;resizable=1;points=[];autosize=1;align=left;verticalAlign=top;spacingTop=-4;fontSize=30;fontStyle=1;fontFamily=Helvetica;" value="Architecture Title" vertex="1" parent="title-group">
  <mxGeometry width="800" height="42" as="geometry" />
</mxCell>
<mxCell id="subtitle-text" style="text;html=1;resizable=0;points=[];autosize=1;align=left;verticalAlign=top;spacingTop=-4;fontSize=16;fontFamily=Helvetica;" value="One-line description" vertex="1" parent="title-group">
  <mxGeometry x="5" y="40" width="800" height="25" as="geometry" />
</mxCell>
<mxCell id="title-sep" style="line;strokeWidth=2;html=1;strokeColor=#FF9900;fontFamily=Helvetica;" value="" vertex="1" parent="title-group">
  <mxGeometry x="5" y="70" width="1190" height="10" as="geometry" />
</mxCell>
```

### AWS Cloud Group

Use `container=0` so services stay at `parent="1"` with absolute coordinates:

```xml
<mxCell id="aws-cloud" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud;strokeColor=#232F3E;fillColor=light-dark(#232F3E0D,#232F3E0D);fillStyle=auto;verticalAlign=top;align=left;spacingLeft=30;fontColor=#232F3E;dashed=0;container=0;pointerEvents=0;collapsible=0;recursiveResize=0" value="AWS Cloud" vertex="1" parent="1">
  <mxGeometry x="260" y="150" width="1060" height="660" as="geometry" />
</mxCell>
```

### Users Container (Outside AWS Cloud)

```xml
<mxCell id="users-container" style="fillColor=#f5f5f5;strokeColor=light-dark(#666666,#D4D4D4);rounded=1;whiteSpace=wrap;html=1;verticalAlign=top;fontStyle=1;fontSize=12;fontColor=#333333;fontFamily=Helvetica;container=1;collapsible=0;shadow=1;strokeWidth=1;" value="Users" vertex="1" parent="1">
  <mxGeometry x="50" y="300" width="130" height="170" as="geometry" />
</mxCell>
<mxCell id="users-icon" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;fillColor=#232F3D;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.users;fontFamily=Helvetica;" value="" vertex="1" parent="users-container">
  <mxGeometry x="41" y="30" width="48" height="48" as="geometry" />
</mxCell>
```

### Service Container (120x120 with 48x48 Icon)

Container `value` = category label (NOT service name). Icon `value` = service name.

```xml
<mxCell id="lambda-ctr" style="fillColor={TINT};strokeColor={STROKE};rounded=1;whiteSpace=wrap;html=1;verticalAlign=top;fontStyle=1;fontSize=12;fontColor={STROKE};fontFamily=Helvetica;container=1;collapsible=0;shadow=1;strokeWidth=1.5;" value="{CATEGORY}" vertex="1" parent="1">
  <mxGeometry x="500" y="300" width="120" height="120" as="geometry" />
</mxCell>
<mxCell id="lambda-icon" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;fillColor={ICON_FILL};strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=10;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.{SHAPE};fontFamily=Helvetica;shadow=1;" value="Service Name&lt;div&gt;&lt;i&gt;detail&lt;/i&gt;&lt;/div&gt;" vertex="1" parent="lambda-ctr">
  <mxGeometry x="36" y="30" width="48" height="48" as="geometry" />
</mxCell>
```

### Service Category Colors

| Category | fillColor (tint) | strokeColor | Icon fillColor |
|----------|------------------|-------------|----------------|
| Compute | `#FFF2E8` | `#ED7100` | `#ED7100` |
| Database | `#F5E6F7` | `#C925D1` | `#C925D1` |
| Analytics / Networking | `#EDE7F6` | `#8C4FFF` | `#8C4FFF` |
| Storage | `#E8F5E9` | `#3F8624` | `#3F8624` |
| App Integration | `#FCE4EC` | `#E7157B` | `#E7157B` |
| AI / ML | `#E0F2F1` | `#01A88D` | `#01A88D` |
| Security | `#FFEBEE` | `#DD344C` | `#DD344C` |
| General / Auxiliary | `#F5F5F5` | `#666666` | `#666666` |

### AWS Service Icon Names (mxgraph.aws4.*)

**Compute:** `lambda`, `ec2`, `fargate`, `elastic_beanstalk`, `app_runner`, `batch`
**Database:** `dynamodb`, `rds`, `aurora`, `elasticache`, `neptune`
**Storage:** `s3`, `glacier`, `elastic_file_system`, `elastic_block_store`
**Analytics:** `kinesis`, `athena`, `glue`, `emr`, `redshift`, `quicksight`
**App Integration:** `sqs`, `sns`, `eventbridge`, `step_functions`, `apigateway`, `appsync`
**Security:** `cognito`, `identity_and_access_management`, `secrets_manager`, `waf`
**Networking:** `route_53`, `cloudfront`, `vpc`, `transit_gateway`
**Containers:** `ecs`, `eks`, `ecr`
**AI/ML:** `sagemaker`, `bedrock`, `rekognition_2`, `comprehend`, `textract`
**Management:** `cloudwatch_2`, `cloudtrail`, `systems_manager`, `cloudformation`

### Group Shapes

| Group | grIcon | strokeColor |
|-------|--------|-------------|
| AWS Cloud | `mxgraph.aws4.group_aws_cloud` | `#232F3E` |
| Region | `mxgraph.aws4.group_region` | `#00A4A6` |
| VPC | `mxgraph.aws4.group_vpc2` | `#8C4FFF` |
| Public Subnet | `mxgraph.aws4.group_public_subnet` | `#248814` |
| Private Subnet | `mxgraph.aws4.group_private_subnet` | `#147EBA` |
| Security Group | `mxgraph.aws4.group_security_group` | `#DD344C` |

**CRITICAL:** Regions MUST use `container=0`. Services placed at `parent="1"` with absolute coordinates.

### Edge Styles

**Standard (synchronous):**
```xml
<mxCell id="edge-1" style="edgeStyle=orthogonalEdgeStyle;html=1;endArrow=block;elbow=vertical;startArrow=none;endFill=1;strokeColor=#545B64;rounded=0;" edge="1" parent="1" source="icon-a" target="icon-b">
```

**Dashed (async / optional):**
```xml
<mxCell id="edge-2" style="edgeStyle=orthogonalEdgeStyle;html=1;endArrow=block;elbow=vertical;startArrow=none;endFill=1;strokeColor=#545B64;rounded=0;dashed=1;" edge="1" ...>
```

**Open arrow (data flow):**
```xml
<mxCell id="edge-3" style="edgeStyle=orthogonalEdgeStyle;html=1;endArrow=open;elbow=vertical;startArrow=none;endFill=0;strokeColor=#545B64;rounded=0;" edge="1" ...>
```

**Edge label (separate child cell):**
```xml
<mxCell id="edge-1-label" value="API call" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=11;fontFamily=Helvetica;labelBackgroundColor=none;" connectable="0" vertex="1" parent="edge-1">
  <mxGeometry relative="1" x="-0.3" y="0" as="geometry"><mxPoint as="offset" /></mxGeometry>
</mxCell>
```

### Avoiding Crossing Lines

When multiple edges leave the same source:

1. **Use different exit points:** Assign distinct `exitX`/`exitY` values as XML attributes on each edge
2. **Route around services:** For edges that need to pass other services, use explicit waypoints:
   ```xml
   <mxGeometry relative="1" as="geometry">
     <Array as="points">
       <mxPoint x="620" y="184" />
       <mxPoint x="840" y="184" />
     </Array>
   </mxGeometry>
   ```
3. **Separate lanes:** Query edges (solid) and registration/async edges (dashed) should exit at different Y positions and use separate horizontal/vertical lanes
4. **Edges on opposite sides:** If possible, route output edges from the left side (`exitX=0`) and data edges from the right side (`exitX=1`)

### Step Badges (28x28)

```xml
<mxCell id="step-N" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#007CBD;strokeColor=default;fontColor=#FFFFFF;fontStyle=1;fontSize=16;fontFamily=Helvetica;shadow=1;glass=0;strokeWidth=2;align=center;verticalAlign=middle;labelBackgroundColor=none;" value="N" vertex="1" parent="1">
  <mxGeometry x="X" y="Y" width="28" height="28" as="geometry" />
</mxCell>
```

Place near arrow source end, offset 20px, minimum 10px clearance from icons.

### Legend Panel

Position at `x = diagram_right_edge + 40`. Include:
- Step descriptions (badge 40x38 + text block)
- Connection types section (solid, dashed, open-arrow with labels)
- Background: `fillColor=light-dark(#EDF3FF,#305363);strokeColor=#6c8ebf`

### Font Standards

| Element | Size | Style |
|---------|------|-------|
| Title | 30px | bold |
| Subtitle | 16px | regular |
| Group labels | 12px | regular |
| Container labels | 12px | bold |
| Service labels | 10px | regular |
| Edge labels | 11px | regular |
| Step badges | 16px (diagram) / 22px (legend) | bold |
| Legend title | 16px | bold |
| Legend text | 14px | regular |

**All fonts:** `fontFamily=Helvetica`

---

## Critical Rules

1. **Service icons connect to edges, NOT containers** - always use the icon ID as edge source/target
2. **Container value = category** (e.g., "Compute"), **Icon value = service name** (e.g., "AWS Lambda")
3. **No emojis** in any element values
4. All positions aligned to grid multiples of 10
5. Edge labels always have `connectable="0"` and `labelBackgroundColor=none`
6. Use `light-dark()` for adaptive colors; add `fillStyle=auto`
7. Run `validate_drawio.py` before delivery - all 6 checks must pass
