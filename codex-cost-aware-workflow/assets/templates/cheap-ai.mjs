#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);

function arg(name, fallback = "") {
  const i = args.indexOf(`--${name}`);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
}

function hasFlag(name) {
  return args.includes(`--${name}`);
}

function printHelp() {
  console.log(`
cheap-ai.mjs - low-cost OpenCode Go subagent for Codex

Usage:
  node tools/cheap-ai.mjs --task "Summarize this file" --files "src/a.ts,src/b.ts"
  node tools/cheap-ai.mjs --model qwen3.6-plus --task "Suggest unit tests" --files "src/auth.ts"
  node tools/cheap-ai.mjs --model minimax-m2.7 --task "Find edge cases" --files "src/parser.ts"

Options:
  --model       OpenCode Go model id. Default: qwen3.6-plus
  --task        Task for the cheap model
  --files       Comma-separated list of files to include as read-only context
  --max-chars   Max characters per file. Default: 12000
  --json        Ask for JSON output
  --help        Show help

Security:
  Requires OPENCODE_API_KEY in environment.
  Never writes files.
`);
}

if (hasFlag("help")) {
  printHelp();
  process.exit(0);
}

const apiKey = process.env.OPENCODE_API_KEY;
if (!apiKey) {
  console.error("Missing OPENCODE_API_KEY.");
  console.error('Set it in PowerShell: [Environment]::SetEnvironmentVariable("OPENCODE_API_KEY", "YOUR_KEY", "User")');
  process.exit(1);
}

const model = arg("model", "qwen3.6-plus");
const task = arg("task", "");
const filesArg = arg("files", "");
const maxChars = Number(arg("max-chars", "12000"));
const wantsJson = hasFlag("json");
const projectRoot = process.cwd();

if (!task.trim()) {
  console.error("Missing --task.");
  printHelp();
  process.exit(1);
}

function safeReadFile(filePath) {
  const rawPath = filePath.trim();
  if (!rawPath) {
    return "";
  }

  const resolved = path.resolve(projectRoot, rawPath);
  const rel = path.relative(projectRoot, resolved);

  if (rel.startsWith("..") || path.isAbsolute(rel)) {
    return `\n\n--- FILE SKIPPED: ${rawPath} ---\nReason: path is outside the project root\n`;
  }

  if (!fs.existsSync(resolved)) {
    return `\n\n--- FILE NOT FOUND: ${rawPath} ---\n`;
  }

  const stat = fs.statSync(resolved);
  if (!stat.isFile()) {
    return `\n\n--- NOT A FILE: ${rawPath} ---\n`;
  }

  const content = fs.readFileSync(resolved, "utf8");
  const clipped = content.length > maxChars
    ? `${content.slice(0, maxChars)}\n\n[TRUNCATED]`
    : content;

  return `\n\n--- FILE: ${rel} ---\n${clipped}\n`;
}

const files = filesArg
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);

const fileContext = files.length
  ? files.map(safeReadFile).join("\n")
  : "";

const outputInstruction = wantsJson
  ? "Return valid JSON only. No Markdown."
  : "Return concise Markdown with headings and bullets where helpful.";

const prompt = `
You are a low-cost coding subagent used by Codex.

You are not allowed to modify files.
You are not the final authority.
Your output will be reviewed by a stronger supervising agent.
Be precise. Do not invent facts. Mention uncertainty.

Task:
${task}

Output instruction:
${outputInstruction}

Context:
${fileContext || "[No files provided]"}
`;

const anthropicMessageModels = new Set([
  "minimax-m2.7",
  "minimax-m2.5",
]);

async function callChatCompletions() {
  const res = await fetch("https://opencode.ai/zen/go/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      messages: [
        {
          role: "system",
          content: "You are a careful low-cost coding subagent. You only provide analysis and suggestions. You never claim to have changed files.",
        },
        {
          role: "user",
          content: prompt,
        },
      ],
      temperature: 0.2,
    }),
  });

  const text = await res.text();
  if (!res.ok) {
    throw new Error(`OpenCode chat/completions error ${res.status}:\n${text}`);
  }

  let data;
  try {
    data = JSON.parse(text);
  } catch {
    return text;
  }

  return data.choices?.[0]?.message?.content ?? JSON.stringify(data, null, 2);
}

async function callMessages() {
  const res = await fetch("https://opencode.ai/zen/go/v1/messages", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      max_tokens: 2048,
      messages: [
        {
          role: "user",
          content: prompt,
        },
      ],
    }),
  });

  const text = await res.text();
  if (!res.ok) {
    throw new Error(`OpenCode messages error ${res.status}:\n${text}`);
  }

  let data;
  try {
    data = JSON.parse(text);
  } catch {
    return text;
  }

  if (Array.isArray(data.content)) {
    return data.content.map((part) => part.text ?? "").join("\n").trim();
  }

  return data.content ?? JSON.stringify(data, null, 2);
}

try {
  const result = anthropicMessageModels.has(model)
    ? await callMessages()
    : await callChatCompletions();

  console.log(result);
} catch (err) {
  console.error(String(err?.message ?? err));
  process.exit(1);
}
