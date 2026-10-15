#!/usr/bin/env node
/**
 * PostToolUse Hook (Edit/Write) - JS/TS quality checks
 *
 * Ported from everything-claude-code hooks.json inline hooks:
 * - Auto-format JS/TS files with Prettier (only if prettier is installed locally)
 * - TypeScript check after editing .ts/.tsx files (only if a tsconfig.json exists)
 * - Warn about console.log statements
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

let data = '';
process.stdin.on('data', c => (data += c));
process.stdin.on('end', () => {
  let input = {};
  try {
    input = JSON.parse(data);
  } catch {
    process.exit(0);
  }
  const p = input.tool_input && input.tool_input.file_path;
  if (!p || !/\.(ts|tsx|js|jsx)$/.test(p) || !fs.existsSync(p)) process.exit(0);

  // Find nearest project root (package.json / tsconfig.json)
  const findUp = name => {
    let dir = path.dirname(p);
    while (dir !== path.dirname(dir)) {
      if (fs.existsSync(path.join(dir, name))) return dir;
      dir = path.dirname(dir);
    }
    return null;
  };

  // Prettier: only when installed in the project, to avoid network downloads
  const pkgRoot = findUp('package.json');
  if (pkgRoot && fs.existsSync(path.join(pkgRoot, 'node_modules', '.bin', 'prettier'))) {
    try {
      execSync(`npx --no-install prettier --write "${p}"`, { cwd: pkgRoot, stdio: 'pipe' });
    } catch {}
  }

  // TypeScript check
  if (/\.(ts|tsx)$/.test(p)) {
    const tsRoot = findUp('tsconfig.json');
    if (tsRoot && fs.existsSync(path.join(tsRoot, 'node_modules', '.bin', 'tsc'))) {
      let out = '';
      try {
        out = execSync('npx --no-install tsc --noEmit --pretty false 2>&1', { cwd: tsRoot, encoding: 'utf8', stdio: 'pipe' });
      } catch (e) {
        out = e.stdout || '';
      }
      const lines = out.split('\n').filter(l => l.includes(path.relative(tsRoot, p))).slice(0, 10);
      if (lines.length) console.error(lines.join('\n'));
    }
  }

  // console.log warning
  const matches = [];
  fs.readFileSync(p, 'utf8').split('\n').forEach((l, i) => {
    if (/console\.log/.test(l)) matches.push(`${i + 1}: ${l.trim()}`);
  });
  if (matches.length) {
    console.error(`[Hook] WARNING: console.log found in ${p}`);
    matches.slice(0, 5).forEach(m => console.error(m));
    console.error('[Hook] Remove console.log before committing');
  }
  process.exit(0);
});
