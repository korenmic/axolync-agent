import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const roots = ['skills-user', 'skills-workspace'];

function readFrontmatterField(text, field) {
  const match = text.match(new RegExp(`^${field}:\\s*["']?(.+?)["']?\\s*$`, 'm'));
  return match?.[1] ?? '';
}

for (const root of roots) {
  const dir = resolve(process.cwd(), root);
  if (!existsSync(dir)) {
    console.log(JSON.stringify({ root, missing: true }));
    continue;
  }

  const rows = [];
  for (const folder of readdirSync(dir).filter((name) => name !== '__pycache__').sort()) {
    const skillPath = resolve(dir, folder, 'SKILL.md');
    if (!existsSync(skillPath)) {
      rows.push({ folder, missingSkill: true });
      continue;
    }

    try {
      const text = readFileSync(skillPath, 'utf8');
      rows.push({
        folder,
        name: readFrontmatterField(text, 'name'),
        description: readFrontmatterField(text, 'description'),
        path: skillPath,
      });
    } catch (error) {
      rows.push({ folder, invalid: true, error: String(error?.message ?? error) });
    }
  }

  console.log(JSON.stringify({ root, rows }));
}
