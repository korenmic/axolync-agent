import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import { createRequire } from 'node:module';
import path from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';

function readArg(name, fallback = null) {
  const prefix = `--${name}=`;
  const found = process.argv.find((arg) => arg.startsWith(prefix));
  if (found) return found.slice(prefix.length);
  const index = process.argv.indexOf(`--${name}`);
  if (index >= 0 && index + 1 < process.argv.length) return process.argv[index + 1];
  return fallback;
}

function hasFlag(name) {
  return process.argv.includes(`--${name}`);
}

const browserRoot = path.resolve(readArg('browser-root', process.cwd()));
const browserRequire = createRequire(path.join(browserRoot, 'package.json'));
const { chromium } = browserRequire('playwright');
const port = Number.parseInt(readArg('port', '5288'), 10);
const query = readArg('query', '');
const activeSongSearchAddon = readArg('active-songsearch-addon', null);
const activeSongSearchAdapter = readArg('active-songsearch-adapter', null);
const expectPanel = hasFlag('expect-panel');
const clickFirst = hasFlag('click-first');
const screenshotPath = readArg('screenshot', null);
const url = `http://127.0.0.1:${Number.isFinite(port) ? port : 5288}/`;

const viteCliPath = path.resolve(browserRoot, 'node_modules', 'vite', 'bin', 'vite.js');
const child = spawn(process.execPath, [
  viteCliPath,
  '--host',
  '127.0.0.1',
  '--port',
  String(Number.isFinite(port) ? port : 5288),
  '--strictPort',
], {
  cwd: browserRoot,
  env: {
    ...process.env,
    VITE_AXOLYNC_BUILD_FLAVOR: process.env.VITE_AXOLYNC_BUILD_FLAVOR ?? 'debug',
    VITE_AXOLYNC_DEVELOPER_MODE_EXPOSED: process.env.VITE_AXOLYNC_DEVELOPER_MODE_EXPOSED ?? 'true',
  },
  stdio: ['ignore', 'pipe', 'pipe'],
});

let serverOutput = '';
child.stdout.on('data', (chunk) => { serverOutput += chunk.toString(); });
child.stderr.on('data', (chunk) => { serverOutput += chunk.toString(); });

async function waitForServer() {
  const deadlineMs = Date.now() + 30_000;
  while (Date.now() < deadlineMs) {
    if (child.exitCode !== null) {
      throw new Error(`Vite dev server exited early with code ${child.exitCode}.\n${serverOutput}`);
    }
    try {
      const response = await fetch(url, { cache: 'no-store' });
      if (response.ok) return;
    } catch {
      // Retry until Vite binds the temporary smoke port.
    }
    await delay(250);
  }
  throw new Error(`Timed out waiting for Vite dev server on ${url}.\n${serverOutput}`);
}

async function stopServer() {
  if (child.exitCode !== null) return;
  child.kill('SIGTERM');
  const deadlineMs = Date.now() + 5_000;
  while (child.exitCode === null && Date.now() < deadlineMs) {
    await delay(100);
  }
  if (child.exitCode === null) child.kill('SIGKILL');
}

function activeSongSearchSelection() {
  if (!activeSongSearchAddon && !activeSongSearchAdapter) return null;
  return {
    addonId: activeSongSearchAddon ?? 'axolync-manual-addon',
    adapterId: activeSongSearchAdapter ?? 'ManualSongSearchAdapter',
  };
}

async function snapshot(page) {
  return page.evaluate(() => {
    const panels = Array.from(document.querySelectorAll('[data-songsearch-results-panel="true"]'));
    const candidates = Array.from(document.querySelectorAll('button[data-songsearch-candidate-key]'));
    const input = document.querySelector('input[data-core-songsearch-input="true"]');
    return {
      status: document.querySelector('#status-bar .status-pill')?.textContent?.trim() ?? '',
      coreFormCount: document.querySelectorAll('form[data-core-songsearch-form="true"]').length,
      coreInputPlaceholder: input?.getAttribute('placeholder') ?? null,
      coreInputValue: input?.value ?? null,
      panelCount: panels.length,
      panelRoles: panels.map((panel) => panel.getAttribute('role')),
      panelLabels: panels.map((panel) => panel.getAttribute('aria-label')),
      panelMessages: panels.flatMap((panel) => Array.from(panel.querySelectorAll('.status-songsearch-results-message')).map((message) => message.textContent?.trim() ?? '')),
      candidateCount: candidates.length,
      candidateTexts: candidates.map((candidate) => candidate.textContent?.trim() ?? ''),
      candidateKeys: candidates.map((candidate) => candidate.getAttribute('data-songsearch-candidate-key')),
      activeElementTag: document.activeElement?.tagName ?? null,
    };
  });
}

async function waitForRequestedSongSearchBootstrap(consoleMessages) {
  if (!activeSongSearchAddon) {
    return { requested: false, observed: true };
  }
  const installMarker = `Preinstalled addon install completed (${activeSongSearchAddon})`;
  const deadlineMs = Date.now() + 20_000;
  while (Date.now() < deadlineMs) {
    if (consoleMessages.some((line) => line.includes(installMarker))) {
      await delay(500);
      return { requested: true, observed: true, marker: installMarker };
    }
    await delay(100);
  }
  return { requested: true, observed: false, marker: installMarker };
}

try {
  await waitForServer();
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });
    const failures = [];
    const consoleMessages = [];
    page.on('pageerror', (error) => failures.push(`pageerror: ${error.message}`));
    page.on('console', (message) => {
      const line = `${message.type()}: ${message.text()}`;
      consoleMessages.push(line);
      if (message.type() === 'error') failures.push(`console error: ${message.text()}`);
    });

    await page.addInitScript((selection) => {
      localStorage.setItem('axolync_uiPreferences', JSON.stringify({
        addonManagerTabStyle: 'hamburger',
        playbarButtonStyle: 'v2',
        theme: 'aurora-stage',
        songSearchFeelLucky: false,
        songSearchManualFallbackOnNoResults: true,
        songSearchAllowSessionStartWhilePaused: true,
      }));
      if (selection) {
        localStorage.setItem('axolync_activeControllerLaneAdapters', JSON.stringify({
          songsearch: selection,
        }));
      }
    }, activeSongSearchSelection());

    await page.goto(url, { waitUntil: 'domcontentloaded' });
    await page.waitForSelector('form[data-core-songsearch-form="true"] input[data-core-songsearch-input="true"]', { timeout: 15_000 });
    const bootstrapWait = await waitForRequestedSongSearchBootstrap(consoleMessages);
    if (!bootstrapWait.observed) {
      failures.push(`requested SongSearch addon did not finish bootstrap before query: ${JSON.stringify(bootstrapWait)}`);
    }
    const before = await snapshot(page);
    if (before.coreFormCount !== 1 || before.coreInputPlaceholder !== 'Search song') {
      failures.push(`core SongSearch form did not render as expected: ${JSON.stringify(before)}`);
    }

    let afterSubmit = before;
    let afterClick = null;
    if (query.trim()) {
      await page.fill('input[data-core-songsearch-input="true"]', query);
      await page.press('input[data-core-songsearch-input="true"]', 'Enter');
      if (expectPanel) {
        await page.waitForSelector('[data-songsearch-results-panel="true"]', { timeout: 20_000 });
      } else {
        await page.waitForFunction(() => {
          const status = document.querySelector('#status-bar .status-pill')?.textContent?.trim() ?? '';
          const panel = document.querySelector('[data-songsearch-results-panel="true"]');
          return /detected|song/i.test(status) || Boolean(panel);
        }, { timeout: 20_000 });
      }
      await delay(300);
      afterSubmit = await snapshot(page);
      if (expectPanel && afterSubmit.candidateCount < 1) {
        failures.push(`expected SongSearch result candidates, got ${JSON.stringify(afterSubmit)}`);
      }
      if (clickFirst) {
        const firstCandidate = page.locator('button[data-songsearch-candidate-key]').first();
        await firstCandidate.click({ timeout: 10_000 });
        await page.waitForFunction(() => {
          const status = document.querySelector('#status-bar .status-pill')?.textContent?.trim() ?? '';
          return /detected/i.test(status);
        }, { timeout: 20_000 });
        await delay(300);
        afterClick = await snapshot(page);
      }
    }

    if (screenshotPath) {
      await fs.mkdir(path.dirname(path.resolve(screenshotPath)), { recursive: true });
      await page.screenshot({ path: path.resolve(screenshotPath), fullPage: true });
    }

    if (failures.length > 0) {
      throw new Error(failures.join('\n'));
    }

    console.log(JSON.stringify({
      ok: true,
      url,
      query,
      activeSongSearchSelection: activeSongSearchSelection(),
      bootstrapWait,
      before,
      afterSubmit,
      afterClick,
      screenshotPath: screenshotPath ? path.resolve(screenshotPath) : null,
      relevantConsoleMessages: consoleMessages.filter((line) => /SongSearch|songsearch|manual|lrclib/i.test(line)).slice(-20),
    }, null, 2));
  } finally {
    await browser.close();
  }
} finally {
  await stopServer();
}
