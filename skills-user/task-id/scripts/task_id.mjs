import { deflateRawSync, inflateRawSync } from 'node:zlib';
import { dirname, join, relative, resolve } from 'node:path';
import { existsSync, readFileSync } from 'node:fs';

function fail(message) {
  console.error(message);
  process.exit(1);
}

function normalizePath(input) {
  if (!input) return '';
  let value = String(input).trim();
  if (value.startsWith('/')) {
    value = value.slice(1);
  }
  value = value.replace(/\//g, '\\');
  return resolve(value);
}

function toPosixPath(input) {
  return String(input || '').replace(/\\/g, '/');
}

function encodeHumanReadable(humanReadable) {
  const compressed = deflateRawSync(Buffer.from(String(humanReadable), 'utf8'));
  return `atid1:${compressed.toString('base64url')}`;
}

function decodePacked(value) {
  const text = String(value || '').trim();
  if (!text.startsWith('atid1:')) {
    return text;
  }
  const payload = text.slice('atid1:'.length);
  return inflateRawSync(Buffer.from(payload, 'base64url')).toString('utf8');
}

function findGitRoot(filePath) {
  let current = resolve(filePath);
  if (!existsSync(current)) {
    fail(`Path does not exist: ${filePath}`);
  }
  current = dirname(current);
  while (true) {
    if (existsSync(join(current, '.git'))) {
      return current;
    }
    const parent = dirname(current);
    if (parent === current) {
      fail(`Could not find repo root for: ${filePath}`);
    }
    current = parent;
  }
}

function readMarkdownTasks(sourcePath) {
  const text = readFileSync(sourcePath, 'utf8');
  const lines = text.split(/\r?\n/);
  const tasks = [];
  for (const line of lines) {
    const match = line.match(/^\s*-\s\[(?: |x|X)\]\s+(.*)$/);
    if (!match) continue;
    const taskText = String(match[1] || '').trim();
    const explicit = taskText.match(/^(\d+)\.\s+/);
    tasks.push({
      countedIndex: tasks.length + 1,
      taskIndex: explicit ? Number(explicit[1]) : tasks.length + 1,
      text: taskText,
    });
  }
  return tasks;
}

function normalizeTaskText(text) {
  return String(text || '').replace(/\s+/g, ' ').trim();
}

function buildHumanReadable({ sourcePath, workspaceRoot, taskIndex }) {
  const repoRoot = findGitRoot(sourcePath);
  const repo = toPosixPath(relative(resolve(workspaceRoot), repoRoot)) || repoRoot.split(/[/\\]/).pop();
  const relSource = toPosixPath(relative(repoRoot, sourcePath));
  return `htid1:${repo}::${relSource}::${taskIndex}`;
}

function parseHumanReadable(humanReadable) {
  const value = String(humanReadable).startsWith('htid1:')
    ? String(humanReadable).slice('htid1:'.length)
    : String(humanReadable);
  const parts = value.split('::');
  if (parts.length !== 3) {
    fail(`Invalid human-readable task id: ${humanReadable}`);
  }
  return {
    repo: parts[0],
    relSource: parts[1],
    taskIndex: Number(parts[2]),
  };
}

function resolveFromSource(sourcePath, taskIndex, workspaceRoot) {
  const absoluteSource = normalizePath(sourcePath);
  const tasks = readMarkdownTasks(absoluteSource);
  const match = tasks.find((task) => Number(task.taskIndex) === Number(taskIndex));
  if (!match) {
    fail(`Task index ${taskIndex} was not found in ${absoluteSource}`);
  }
  const humanReadable = buildHumanReadable({
    sourcePath: absoluteSource,
    workspaceRoot,
    taskIndex: match.taskIndex,
  });
  return {
    humanReadable,
    packed: encodeHumanReadable(humanReadable),
    source: absoluteSource,
    taskIndex: match.taskIndex,
    taskText: match.text,
  };
}

function parseQueue(queuePath) {
  const lines = readFileSync(queuePath, 'utf8').split(/\r?\n/);
  const items = [];
  for (let i = 0; i < lines.length; i += 1) {
    const header = lines[i].match(/^###\s+(Q-\d+)/);
    if (!header) continue;
    const block = [];
    let j = i + 1;
    while (j < lines.length && !/^###\s+Q-\d+/.test(lines[j])) {
      block.push(lines[j]);
      j += 1;
    }
    const statusLine = block.find((line) => line.includes('- Status:'));
    const sourceLine = block.find((line) => line.includes('- Source:'));
    const taskLine = block.find((line) => line.includes('- Task:'));
    items.push({
      qid: header[1],
      status: statusLine || '',
      sourceLine: sourceLine || '',
      taskLine: taskLine || '',
    });
    i = j - 1;
  }
  return items;
}

function extractMarkdownLinkTarget(line) {
  const match = String(line || '').match(/\]\(([^)]+)\)/);
  if (!match) fail(`Could not parse source link from line: ${line}`);
  return match[1];
}

function extractTaskLineText(line) {
  const match = String(line || '').match(/- Task:\s+`(.+)`/);
  if (match) return match[1];
  return String(line || '').replace(/^- Task:\s+/, '').trim();
}

function resolveFromQueue(qid, workspaceRoot, queueFile) {
  const absoluteQueue = normalizePath(queueFile);
  const items = parseQueue(absoluteQueue);
  const item = items.find((entry) => entry.qid === qid);
  if (!item) fail(`Queue item not found: ${qid}`);
  const sourcePath = normalizePath(extractMarkdownLinkTarget(item.sourceLine));
  const queuedTaskText = normalizeTaskText(extractTaskLineText(item.taskLine));
  const tasks = readMarkdownTasks(sourcePath);
  const match = tasks.find((task) => normalizeTaskText(task.text) === queuedTaskText);
  if (!match) {
    fail(`Could not match queued task text back to source file: ${qid}`);
  }
  const humanReadable = buildHumanReadable({
    sourcePath,
    workspaceRoot,
    taskIndex: match.taskIndex,
  });
  return {
    humanReadable,
    packed: encodeHumanReadable(humanReadable),
    source: sourcePath,
    taskIndex: match.taskIndex,
    taskText: match.text,
    qid,
  };
}

function resolveAny(idValue, workspaceRoot) {
  const humanReadable = decodePacked(idValue);
  const parsed = parseHumanReadable(humanReadable);
  const source = resolve(workspaceRoot, parsed.repo, parsed.relSource);
  return resolveFromSource(source, parsed.taskIndex, workspaceRoot);
}

function formatBlob(result) {
  return [
    `TASK-ID-HTID1: ${result.humanReadable}`,
    `TASK-ID-ATID1: ${result.packed}`,
    `SOURCE: ${toPosixPath(result.source)}`,
    `TEXT: ${result.taskText}`,
  ].join('\n');
}

function printResult(result, format) {
  if (format === 'json') {
    console.log(JSON.stringify(result, null, 2));
    return;
  }
  if (format === 'canonical') {
    console.log(result.humanReadable);
    return;
  }
  console.log(formatBlob(result));
}

function parseArgs(argv) {
  const [, , command, ...rest] = argv;
  const positional = [];
  const named = new Map();
  for (let i = 0; i < rest.length; i += 1) {
    const token = rest[i];
    if (token.startsWith('--')) {
      named.set(token.slice(2), rest[i + 1]);
      i += 1;
      continue;
    }
    positional.push(token);
  }
  return { command, positional, named };
}

const { command, positional, named } = parseArgs(process.argv);
const workspaceRoot = normalizePath(named.get('workspace-root') || process.cwd());
const format = String(named.get('format') || 'blob');

if (command === 'from-queue') {
  const qid = positional[0];
  if (!qid) fail('Usage: from-queue <Q-ID> [--workspace-root <path>] [--queue-file <path>] [--format blob|json|canonical]');
  const queueFile = named.get('queue-file') || join(workspaceRoot, '.codex', 'local-task-queue.md');
  printResult(resolveFromQueue(qid, workspaceRoot, queueFile), format);
  process.exit(0);
}

if (command === 'from-source') {
  const sourcePath = positional[0];
  const taskIndex = positional[1];
  if (!sourcePath || !taskIndex) fail('Usage: from-source <source-file> <task-index> [--workspace-root <path>] [--format blob|json|canonical]');
  printResult(resolveFromSource(sourcePath, Number(taskIndex), workspaceRoot), format);
  process.exit(0);
}

if (command === 'decode') {
  const packed = positional[0];
  if (!packed) fail('Usage: decode <atid1:...> [--format canonical|json]');
  const humanReadable = decodePacked(packed);
  if (format === 'json') {
    console.log(JSON.stringify({ packed, humanReadable }, null, 2));
  } else {
    console.log(humanReadable);
  }
  process.exit(0);
}

if (command === 'resolve') {
  const value = positional[0];
  if (!value) fail('Usage: resolve <htid1-or-atid1> [--workspace-root <path>] [--format blob|json|canonical]');
  printResult(resolveAny(value, workspaceRoot), format);
  process.exit(0);
}

fail('Supported commands: from-queue, from-source, decode, resolve');
