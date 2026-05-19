import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { join } from "node:path";

function runPython(args: string[], cwd: string): string {
  const python = process.env.PYTHON ?? process.env.PYTHON_EXECUTABLE ?? "python";
  return execFileSync(python, args, {
    cwd,
    encoding: "utf8",
    maxBuffer: 50 * 1024 * 1024,
    env: process.env,
  }).trim();
}

function projectRoot(cwd: string): string {
  return cwd;
}

function summarizeIfNeeded(readingId: string, cwd: string): void {
  const studyPath = join(cwd, "data", "ocr", readingId, "summaries", "study_materials.md");
  if (existsSync(studyPath)) return;
  runPython(["main.py", "summarize", "--reading-id", readingId], cwd);
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
      base_dir: Type.Optional(Type.String({ description: "OCR data directory", default: "data/ocr" })),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      const cwd = projectRoot(ctx.cwd ?? process.cwd());
      const output = runPython(
        [
          "main.py",
          "ask",
          "--base-dir",
          params.base_dir ?? "data/ocr",
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
      base_dir: Type.Optional(Type.String({ description: "OCR data directory", default: "data/ocr" })),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      const cwd = projectRoot(ctx.cwd ?? process.cwd());
      const baseDir = params.base_dir ?? "data/ocr";
      const readingDir = join(cwd, baseDir, params.reading_id, "summaries", "study_materials.md");
      if (!existsSync(readingDir)) {
        summarizeIfNeeded(params.reading_id, cwd);
      }
      const output = runPython(
        ["main.py", "study", "--base-dir", baseDir, "--reading-id", params.reading_id],
        cwd,
      );
      return {
        content: [{ type: "text", text: output }],
        details: { format: "markdown-study-materials" },
      };
    },
  });
}
