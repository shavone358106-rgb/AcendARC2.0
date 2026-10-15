#!/usr/bin/env node
/**
 * Stop Hook - Check for console.log in modified JS/TS files after each response
 *
 * Ported from everything-claude-code hooks.json inline Stop hook.
 */

const fs = require('fs');
const { execSync } = require('child_process');

try {
  execSync('git rev-parse --git-dir', { stdio: 'pipe' });
  const files = execSync('git diff --name-only HEAD', { encoding: 'utf8', stdio: 'pipe' })
    .split('\n')
    .filter(f => /\.(ts|tsx|js|jsx)$/.test(f) && fs.existsSync(f));
  let found = false;
  for (const f of files) {
    if (fs.readFileSync(f, 'utf8').includes('console.log')) {
      console.error(`[Hook] WARNING: console.log found in ${f}`);
      found = true;
    }
  }
  if (found) console.error('[Hook] Remove console.log statements before committing');
} catch {}
process.exit(0);
