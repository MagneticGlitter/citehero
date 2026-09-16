import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { join } from "node:path";

const PROJECT_ROOT = process.env.CITEHERO_PROJECT_ROOT ?? "/home/magneticglitter/school/citehero";
const DEFAULT_BASE_DIR = process.env.CITEHERO_BASE_DIR ?? join(PROJECT_ROOT, "data", "ocr");

function runBinary(binary: string, args: string[], cwd: string): string {
  return execFileSync(binary, args, {
    cwd,
    encoding: "utf8",
    maxBuffer: 50 * 1024 * 1024,
    env: { ...process.env, CITEHERO_BASE_DIR: DEFAULT_BASE_DIR },
  }).trim();
}

function runCitehero(args: string[], cwd: string): string {
  const configured = process.env.CITEHERO_BIN;
  if (configured) return runBinary(configured, args, cwd);
  try {
    return runBinary("citehero", args, cwd);
  } catch (error) {
    const mainPy = join(PROJECT_ROOT, "main.py");
    if (!existsSync(mainPy)) throw error;
    const python = process.env.PYTHON ?? process.env.PYTHON_EXECUTABLE ?? "python";
    return runBinary(python, [mainPy, ...args], PROJECT_ROOT);
  }
}

function withBaseDir(params: { base_dir?: string }, args: string[]): string[] {
  return ["--base-dir", params.base_dir ?? DEFAULT_BASE_DIR, ...args];
}

function summarizeIfNeeded(readingId: string, baseDir: string, cwd: string): void {
  const studyPath = join(baseDir, readingId, "summaries", "study_materials.md");
  if (existsSync(studyPath)) return;
  runCitehero(["summarize", "--base-dir", baseDir, "--reading-id", readingId], cwd);
}

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "literature_rag",
    label: "Literature RAG",
    description: "Return grounded literature answers in Question / Response / Evidence format.",
    parameters: Type.Object({
      reading_id: Type.String({ description: "Reading identifier" }),
      question: Type.String({ description: "User question" }),
      top_k: Type.Optional(Type.Number({ description: "Number of evidence chunks", default: 5 })),
      base_dir: Type.Optional(Type.String({ description: "OCR data directory", default: DEFAULT_BASE_DIR })),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      const cwd = ctx.cwd ?? process.cwd();
      const output = runCitehero(
        [
          "ask",
          ...withBaseDir(params, []),
          "--reading-id",
          params.reading_id,
          "--question",
          params.question,
          "--top-k",
          String(params.top_k ?? 5),
        ],
        cwd,
      );
      return {
        content: [{ type: "text", text: output }],
        details: { format: "question/response/evidence" },
      };
    },
  });

  pi.registerTool({
    name: "literature_study",
    label: "Literature Study Materials",
    description: "Build markdown study materials from summary.json and study_materials.md.",
    parameters: Type.Object({
      reading_id: Type.String({ description: "Reading identifier" }),
      base_dir: Type.Optional(Type.String({ description: "OCR data directory", default: DEFAULT_BASE_DIR })),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      const cwd = ctx.cwd ?? process.cwd();
      const baseDir = params.base_dir ?? DEFAULT_BASE_DIR;
      summarizeIfNeeded(params.reading_id, baseDir, cwd);
      const output = runCitehero(["study", "--base-dir", baseDir, "--reading-id", params.reading_id], cwd);
      return {
        content: [{ type: "text", text: output }],
        details: { format: "markdown-study-materials" },
      };
    },
  });
}
