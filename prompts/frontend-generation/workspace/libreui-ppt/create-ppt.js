const pptxgen = require('pptxgenjs');
const html2pptx = require('/home/ubuntu/.claude/skills/pptx/scripts/html2pptx');
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const WORKSPACE = '/home/ubuntu/codes/awesome-claude/prompts/frontend-generation/workspace/libreui-ppt';

// Create gradient background PNG
async function createGradientBg(filename) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="810">
    <defs>
      <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#667eea"/>
        <stop offset="100%" style="stop-color:#764ba2"/>
      </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#g)"/>
  </svg>`;
  await sharp(Buffer.from(svg)).png().toFile(filename);
  return filename;
}

// Create frosted glass card background
async function createGlassCard(w, h, filename) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}">
    <rect width="100%" height="100%" rx="24" fill="rgba(255,255,255,0.1)" stroke="rgba(255,255,255,0.2)" stroke-width="2"/>
  </svg>`;
  await sharp(Buffer.from(svg)).png().toFile(filename);
  return filename;
}

async function createPresentation() {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.title = 'AI 驱动的智能内容安全';
  pptx.author = 'AWS AI Solutions';

  // Create gradient background
  const bgPath = path.join(WORKSPACE, 'gradient-bg.png');
  await createGradientBg(bgPath);

  // Slide 1: Cover
  const slide1 = pptx.addSlide();
  slide1.addImage({ path: bgPath, x: 0, y: 0, w: 10, h: 5.625 });
  slide1.addText('AI 驱动的智能内容安全', { x: 0.5, y: 1.8, w: 9, h: 0.8, fontSize: 44, bold: true, color: 'FFFFFF', align: 'center' });
  slide1.addText('携手共建企业级风控、营销合规与内容治理解决方案', { x: 0.5, y: 2.7, w: 9, h: 0.5, fontSize: 18, color: 'E0E7FF', align: 'center' });

  // Tags
  const tags = ['风险管控', '营销合规', '内容治理', 'AI 赋能'];
  const tagWidth = 1.4;
  const startX = (10 - tags.length * tagWidth - (tags.length - 1) * 0.2) / 2;
  tags.forEach((tag, i) => {
    slide1.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x: startX + i * (tagWidth + 0.2), y: 3.5, w: tagWidth, h: 0.4, fill: { color: '1E3A5F' }, rectRadius: 0.2 });
    slide1.addText(tag, { x: startX + i * (tagWidth + 0.2), y: 3.5, w: tagWidth, h: 0.4, fontSize: 11, color: '60A5FA', align: 'center', valign: 'middle' });
  });

  slide1.addText('AWS AI Solutions | 共创合作方案', { x: 0.5, y: 4.8, w: 9, h: 0.3, fontSize: 10, color: '94A3B8', align: 'center' });

  // Slide 2: 行业痛点
  const slide2 = pptx.addSlide();
  slide2.addImage({ path: bgPath, x: 0, y: 0, w: 10, h: 5.625 });
  slide2.addText('行业痛点与挑战', { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, bold: true, color: 'FFFFFF' });
  slide2.addText('企业在内容安全领域面临的核心问题', { x: 0.5, y: 0.95, w: 9, h: 0.3, fontSize: 12, color: 'A5B4FC' });

  const painPoints = [
    { icon: '!', title: '规模与速度', desc: '日均百万级内容审核需求，传统人工方式无法满足实时性要求' },
    { icon: '?', title: '对抗性攻击', desc: '不良行为者持续升级绕过手段：同音字、图片变体、多模态混淆' },
    { icon: '$', title: '成本与精度', desc: '大模型精度高但成本高昂，小模型快速但误判多' },
    { icon: '*', title: '多场景覆盖', desc: '风控、营销、UGC各有不同标准，缺乏统一治理框架' }
  ];

  painPoints.forEach((p, i) => {
    const x = 0.4 + (i % 2) * 4.7;
    const y = 1.5 + Math.floor(i / 2) * 1.9;
    slide2.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x, y, w: 4.5, h: 1.7, fill: { color: 'FFFFFF', transparency: 90 }, line: { color: 'FFFFFF', transparency: 80, width: 1 }, rectRadius: 0.15 });
    slide2.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: y + 0.15, w: 0.5, h: 0.5, fill: { color: 'EFF6FF' }, rectRadius: 0.1 });
    slide2.addText(p.icon, { x: x + 0.15, y: y + 0.15, w: 0.5, h: 0.5, fontSize: 18, color: '3B82F6', align: 'center', valign: 'middle' });
    slide2.addText(p.title, { x: x + 0.8, y: y + 0.2, w: 3.5, h: 0.35, fontSize: 16, bold: true, color: 'FFFFFF' });
    slide2.addText(p.desc, { x: x + 0.15, y: y + 0.75, w: 4.2, h: 0.8, fontSize: 11, color: 'CBD5E1', valign: 'top' });
  });

  slide2.addText('02 / 08', { x: 9, y: 5.2, w: 0.8, h: 0.3, fontSize: 9, color: '64748B', align: 'right' });

  // Slide 3: 解决方案
  const slide3 = pptx.addSlide();
  slide3.addImage({ path: bgPath, x: 0, y: 0, w: 10, h: 5.625 });
  slide3.addText('AWS AI 解决方案', { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, bold: true, color: 'FFFFFF' });
  slide3.addText('四大核心能力，全面覆盖内容安全场景', { x: 0.5, y: 0.95, w: 9, h: 0.3, fontSize: 12, color: 'A5B4FC' });

  const solutions = [
    { num: '01', title: '多模态检测', desc: 'ECLIP 图文一致性检测\n实时识别图文不符内容', color: '3B82F6' },
    { num: '02', title: '图谱风控', desc: 'GNN 图神经网络\n识别欺诈团伙与异常行为', color: '8B5CF6' },
    { num: '03', title: '大模型蒸馏', desc: 'BD-LLM 知识迁移\n95%成本节省保持高准确率', color: '06B6D4' },
    { num: '04', title: 'AIGC 安全', desc: 'Bedrock Guardrails\n实时过滤有害内容生成', color: '10B981' }
  ];

  solutions.forEach((s, i) => {
    const x = 0.4 + i * 2.4;
    slide3.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x, y: 1.5, w: 2.2, h: 3.5, fill: { color: 'FFFFFF', transparency: 90 }, line: { color: 'FFFFFF', transparency: 80, width: 1 }, rectRadius: 0.15 });
    slide3.addText(s.num, { x, y: 1.7, w: 2.2, h: 0.5, fontSize: 28, bold: true, color: s.color, align: 'center' });
    slide3.addText(s.title, { x, y: 2.3, w: 2.2, h: 0.4, fontSize: 16, bold: true, color: 'FFFFFF', align: 'center' });
    slide3.addText(s.desc, { x: x + 0.15, y: 2.8, w: 1.9, h: 1.8, fontSize: 11, color: 'CBD5E1', align: 'center', valign: 'top' });
  });

  slide3.addText('03 / 08', { x: 9, y: 5.2, w: 0.8, h: 0.3, fontSize: 9, color: '64748B', align: 'right' });

  // Slide 4: 技术架构
  const slide4 = pptx.addSlide();
  slide4.addImage({ path: bgPath, x: 0, y: 0, w: 10, h: 5.625 });
  slide4.addText('技术架构：四层审核体系', { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, bold: true, color: 'FFFFFF' });

  const layers = [
    { name: '应用层', desc: '商品审核 / 欺诈检测 / 广告过滤 / AIGC安全', services: 'API Gateway', color: '3B82F6' },
    { name: '模型层', desc: 'ECLIP多模态 / GNN图网络 / BD-LLM蒸馏', services: 'SageMaker + Bedrock', color: '8B5CF6' },
    { name: '数据层', desc: '多模态融合 / 图谱构建 / 向量检索', services: 'OpenSearch + Neptune', color: '06B6D4' },
    { name: '基础层', desc: '弹性计算 / 分布式存储 / 流式处理', services: 'EC2/EKS + Kinesis', color: '10B981' }
  ];

  layers.forEach((l, i) => {
    const y = 1.3 + i * 1.0;
    slide4.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x: 0.5, y, w: 9, h: 0.85, fill: { color: 'FFFFFF', transparency: 90 }, line: { color: l.color, width: 2, transparency: 0 }, rectRadius: 0.1 });
    slide4.addText((i + 1).toString(), { x: 0.7, y, w: 0.4, h: 0.85, fontSize: 20, bold: true, color: l.color, valign: 'middle' });
    slide4.addText(l.name, { x: 1.2, y: y + 0.1, w: 1.5, h: 0.35, fontSize: 14, bold: true, color: 'FFFFFF' });
    slide4.addText(l.desc, { x: 1.2, y: y + 0.45, w: 4.5, h: 0.3, fontSize: 10, color: 'CBD5E1' });
    slide4.addText(l.services, { x: 7, y, w: 2.3, h: 0.85, fontSize: 10, color: 'A5B4FC', align: 'right', valign: 'middle' });
  });

  slide4.addText('04 / 08', { x: 9, y: 5.2, w: 0.8, h: 0.3, fontSize: 9, color: '64748B', align: 'right' });

  // Slide 5: Amazon 实践成果
  const slide5 = pptx.addSlide();
  slide5.addImage({ path: bgPath, x: 0, y: 0, w: 10, h: 5.625 });
  slide5.addText('Amazon 实践成果', { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, bold: true, color: 'FFFFFF' });
  slide5.addText('经过验证的大规模内容审核能力', { x: 0.5, y: 0.95, w: 9, h: 0.3, fontSize: 12, color: 'A5B4FC' });

  const metrics = [
    { value: '99.5%', label: '审核准确率', sub: 'AI模型精度' },
    { value: '50ms', label: 'P99延迟', sub: '实时响应' },
    { value: '10亿+', label: '日均处理量', sub: '商品审核' },
    { value: '95%', label: '成本节省', sub: '模型蒸馏' }
  ];

  metrics.forEach((m, i) => {
    const x = 0.5 + i * 2.35;
    slide5.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x, y: 1.5, w: 2.15, h: 1.6, fill: { color: 'FFFFFF', transparency: 90 }, rectRadius: 0.15 });
    slide5.addText(m.value, { x, y: 1.65, w: 2.15, h: 0.7, fontSize: 32, bold: true, color: '3B82F6', align: 'center' });
    slide5.addText(m.label, { x, y: 2.35, w: 2.15, h: 0.35, fontSize: 12, bold: true, color: 'FFFFFF', align: 'center' });
    slide5.addText(m.sub, { x, y: 2.7, w: 2.15, h: 0.3, fontSize: 10, color: 'A5B4FC', align: 'center' });
  });

  // Results
  slide5.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 3.3, w: 9, h: 1.8, fill: { color: 'FFFFFF', transparency: 90 }, rectRadius: 0.15 });
  const results = [
    '违规拦截率提升 40%，误判率降低 60%',
    '人工审核量减少 80%，审核时效从小时级缩短至秒级',
    '年化避免损失超 $100M，投资回报率超 500%'
  ];
  results.forEach((r, i) => {
    slide5.addText('✓ ' + r, { x: 0.7, y: 3.5 + i * 0.5, w: 8.5, h: 0.4, fontSize: 12, color: 'E0E7FF' });
  });

  slide5.addText('05 / 08', { x: 9, y: 5.2, w: 0.8, h: 0.3, fontSize: 9, color: '64748B', align: 'right' });

  // Slide 6: 共创场景
  const slide6 = pptx.addSlide();
  slide6.addImage({ path: bgPath, x: 0, y: 0, w: 10, h: 5.625 });
  slide6.addText('共创合作场景', { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, bold: true, color: 'FFFFFF' });
  slide6.addText('针对您的业务场景，定制化解决方案', { x: 0.5, y: 0.95, w: 9, h: 0.3, fontSize: 12, color: 'A5B4FC' });

  const scenarios = [
    { title: '风控场景', items: ['交易欺诈实时识别', '刷单团伙图谱分析', '账号异常行为检测', '支付风险评估'] },
    { title: '营销场景', items: ['广告内容合规审核', '营销文案自动生成', '敏感词实时过滤', '品牌保护监控'] },
    { title: '内容治理', items: ['UGC 内容审核', '评论/评价质量把控', '版权侵权检测', '有害信息过滤'] }
  ];

  scenarios.forEach((s, i) => {
    const x = 0.5 + i * 3.1;
    slide6.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x, y: 1.4, w: 2.9, h: 3.5, fill: { color: 'FFFFFF', transparency: 90 }, rectRadius: 0.15 });
    slide6.addText(s.title, { x, y: 1.55, w: 2.9, h: 0.45, fontSize: 16, bold: true, color: 'FFFFFF', align: 'center' });
    s.items.forEach((item, j) => {
      slide6.addText('• ' + item, { x: x + 0.2, y: 2.1 + j * 0.6, w: 2.5, h: 0.5, fontSize: 11, color: 'CBD5E1' });
    });
  });

  slide6.addText('06 / 08', { x: 9, y: 5.2, w: 0.8, h: 0.3, fontSize: 9, color: '64748B', align: 'right' });

  // Slide 7: 合作模式
  const slide7 = pptx.addSlide();
  slide7.addImage({ path: bgPath, x: 0, y: 0, w: 10, h: 5.625 });
  slide7.addText('合作模式', { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, bold: true, color: 'FFFFFF' });
  slide7.addText('灵活的共创方式，满足不同阶段需求', { x: 0.5, y: 0.95, w: 9, h: 0.3, fontSize: 12, color: 'A5B4FC' });

  const modes = [
    { title: 'POC 验证', desc: '2-4周快速验证\n选定场景深度试点\n量化效果对比', color: '3B82F6' },
    { title: '联合开发', desc: '定制化模型训练\n业务规则深度融合\n持续优化迭代', color: '8B5CF6' },
    { title: '生产部署', desc: '端到端交付\n高可用架构设计\n7×24运维支持', color: '10B981' }
  ];

  modes.forEach((m, i) => {
    const x = 0.8 + i * 3.1;
    slide7.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x, y: 1.5, w: 2.7, h: 2.8, fill: { color: 'FFFFFF', transparency: 90 }, line: { color: m.color, width: 3 }, rectRadius: 0.15 });
    slide7.addText('0' + (i + 1), { x, y: 1.7, w: 2.7, h: 0.5, fontSize: 24, bold: true, color: m.color, align: 'center' });
    slide7.addText(m.title, { x, y: 2.2, w: 2.7, h: 0.4, fontSize: 16, bold: true, color: 'FFFFFF', align: 'center' });
    slide7.addText(m.desc, { x: x + 0.2, y: 2.7, w: 2.3, h: 1.4, fontSize: 11, color: 'CBD5E1', align: 'center' });
  });

  slide7.addText('07 / 08', { x: 9, y: 5.2, w: 0.8, h: 0.3, fontSize: 9, color: '64748B', align: 'right' });

  // Slide 8: 下一步
  const slide8 = pptx.addSlide();
  slide8.addImage({ path: bgPath, x: 0, y: 0, w: 10, h: 5.625 });
  slide8.addText('下一步行动', { x: 0.5, y: 1.5, w: 9, h: 0.7, fontSize: 36, bold: true, color: 'FFFFFF', align: 'center' });
  slide8.addText('让我们一起探讨您的业务场景', { x: 0.5, y: 2.2, w: 9, h: 0.4, fontSize: 16, color: 'A5B4FC', align: 'center' });

  const steps = [
    '安排技术深度交流会议',
    '确定 POC 验证场景与目标',
    '制定共创计划与时间表'
  ];

  slide8.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x: 2.5, y: 2.8, w: 5, h: 1.8, fill: { color: 'FFFFFF', transparency: 90 }, rectRadius: 0.15 });
  steps.forEach((step, i) => {
    slide8.addText((i + 1) + '. ' + step, { x: 2.8, y: 3.0 + i * 0.5, w: 4.4, h: 0.4, fontSize: 13, color: 'E0E7FF' });
  });

  slide8.addText('AWS AI Solutions Team', { x: 0.5, y: 4.9, w: 9, h: 0.3, fontSize: 11, color: '94A3B8', align: 'center' });
  slide8.addText('08 / 08', { x: 9, y: 5.2, w: 0.8, h: 0.3, fontSize: 9, color: '64748B', align: 'right' });

  // Save
  const outputPath = path.join(WORKSPACE, 'ai-content-safety-libreui.pptx');
  await pptx.writeFile({ fileName: outputPath });
  console.log('PPT created:', outputPath);
}

createPresentation().catch(console.error);
