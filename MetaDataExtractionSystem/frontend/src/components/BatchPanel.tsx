"use client";

import { useState } from "react";
import { ProviderInfo } from "@/app/page";

interface BatchPrediction {
  "File Name": string;
  "Aggrement Value": string;
  "Aggrement Start Date": string;
  "Aggrement End Date": string;
  "Renewal Notice (Days)": string;
  "Party One": string;
  "Party Two": string;
  _error?: string;
}

interface EvalField {
  field: string;
  true_count: number;
  false_count: number;
  total: number;
  recall: number;
}

interface EvalResult {
  per_field_recall: EvalField[];
  overall_recall: number;
}

interface BatchPanelProps {
  providerInfo: ProviderInfo | null;
}

const FIELDS = [
  { key: "Aggrement Value", label: "Agreement Value" },
  { key: "Aggrement Start Date", label: "Start Date" },
  { key: "Aggrement End Date", label: "End Date" },
  { key: "Renewal Notice (Days)", label: "Renewal Notice" },
  { key: "Party One", label: "Party One" },
  { key: "Party Two", label: "Party Two" },
] as const;

export default function BatchPanel({ providerInfo }: BatchPanelProps) {
  const [folder, setFolder] = useState<"train" | "test">("train");
  const [predictions, setPredictions] = useState<BatchPrediction[]>([]);
  const [evalResult, setEvalResult] = useState<EvalResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [evalLoading, setEvalLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [provider, setProvider] = useState<string | null>(null);

  const providerAvailable = providerInfo?.available ?? false;

  const runExtraction = async () => {
    if (!providerAvailable) {
      setError(
        "No LLM provider configured. Set OPENAI_API_KEY, GROQ_API_KEY, or run Ollama locally."
      );
      return;
    }
    setLoading(true);
    setError(null);
    setPredictions([]);
    setEvalResult(null);

    try {
      const res = await fetch("/api/batch-extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ folder }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Server error: ${res.status}`);
      }
      const data = await res.json();
      setPredictions(data.predictions || []);
      setProvider(data.provider || null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Batch extraction failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const runEvaluation = async () => {
    if (!providerAvailable) {
      setError(
        "No LLM provider configured. Set OPENAI_API_KEY, GROQ_API_KEY, or run Ollama locally."
      );
      return;
    }
    setEvalLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ folder }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Server error: ${res.status}`);
      }
      const data: EvalResult = await res.json();
      setEvalResult(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Evaluation failed";
      setError(msg);
    } finally {
      setEvalLoading(false);
    }
  };

  const downloadCSV = async () => {
    try {
      const res = await fetch("/api/predict-test-csv", { method: "POST" });
      if (!res.ok) throw new Error("Download failed");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "test_predictions.csv";
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Download failed";
      setError(msg);
    }
  };

  const hasErrors = predictions.some((p) => p._error);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Controls */}
      <div className="glass-card p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            {/* Folder selector */}
            <div className="inline-flex rounded-xl overflow-hidden border border-[var(--card-border)]">
              <button
                onClick={() => setFolder("train")}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  folder === "train"
                    ? "bg-brand-600 text-white"
                    : "text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface)]"
                }`}
              >
                Train Set
              </button>
              <button
                onClick={() => setFolder("test")}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  folder === "test"
                    ? "bg-brand-600 text-white"
                    : "text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface)]"
                }`}
              >
                Test Set
              </button>
            </div>

            {/* Provider pill */}
            {providerInfo && (
              <span
                className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                  providerAvailable
                    ? "bg-green-500/10 text-green-400 border border-green-500/20"
                    : "bg-red-500/10 text-red-400 border border-red-500/20"
                }`}
              >
                {providerAvailable
                  ? `${providerInfo.provider} (${providerInfo.model})`
                  : "No LLM"}
              </span>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={runExtraction}
              disabled={loading || evalLoading}
              className="px-5 py-2.5 bg-brand-600 text-white text-sm font-medium rounded-xl
                         hover:bg-brand-500 disabled:opacity-50 disabled:cursor-not-allowed
                         transition-all duration-200 shadow-lg shadow-brand-600/20"
            >
              {loading ? (
                <span className="inline-flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Extracting...
                </span>
              ) : (
                "Run Extraction"
              )}
            </button>

            <button
              onClick={runEvaluation}
              disabled={loading || evalLoading}
              className="px-5 py-2.5 bg-[var(--surface)] text-[var(--text-secondary)] text-sm font-medium rounded-xl
                         border border-[var(--card-border)] hover:bg-brand-500/10 hover:text-[var(--text-primary)]
                         disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {evalLoading ? "Evaluating..." : "Evaluate Recall"}
            </button>

            {folder === "test" && (
              <button
                onClick={downloadCSV}
                disabled={loading || evalLoading}
                className="px-5 py-2.5 bg-[var(--surface)] text-[var(--text-secondary)] text-sm font-medium rounded-xl
                           border border-[var(--card-border)] hover:bg-brand-500/10 hover:text-[var(--text-primary)]
                           disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                Download CSV
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="glass-card p-4 border !border-red-500/30 animate-slide-up">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 mt-1.5 bg-red-500 rounded-full flex-shrink-0" />
            <div>
              <p className="text-red-500 dark:text-red-400 text-sm font-medium">Error</p>
              <p className="text-red-500/80 dark:text-red-400/80 text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Evaluation Results */}
      {evalResult && (
        <div className="glass-card p-6 animate-slide-up">
          <h3 className="text-[var(--text-primary)] font-semibold text-base mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Per-Field Recall
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
            {evalResult.per_field_recall.map((field) => (
              <div key={field.field} className="bg-[var(--surface)] rounded-xl p-3 border border-[var(--card-border)]">
                <p className="text-xs text-[var(--text-tertiary)] font-medium mb-1">{field.field}</p>
                <div className="flex items-end gap-2">
                  <span className="text-xl font-bold text-[var(--text-primary)]">
                    {(field.recall * 100).toFixed(0)}%
                  </span>
                  <span className="text-xs text-[var(--text-faint)] mb-0.5">
                    {field.true_count}/{field.total}
                  </span>
                </div>
                <div className="mt-2 h-1.5 bg-[var(--card-border)] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-brand-500 rounded-full transition-all duration-500"
                    style={{ width: `${field.recall * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between pt-3 border-t border-[var(--card-border)]">
            <span className="text-sm text-[var(--text-tertiary)]">Overall Recall</span>
            <span className="text-lg font-bold text-brand-400">
              {(evalResult.overall_recall * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      )}

      {/* Predictions Table */}
      {predictions.length > 0 && (
        <div className="glass-card overflow-hidden animate-slide-up">
          <div className="px-5 py-3 border-b border-[var(--card-border)] flex items-center justify-between">
            <h3 className="text-[var(--text-primary)] font-semibold text-sm">
              Extraction Results ({predictions.length} files)
            </h3>
            {provider && (
              <span className="text-xs text-[var(--text-faint)]">Provider: {provider}</span>
            )}
          </div>

          {hasErrors && (
            <div className="px-5 py-2.5 bg-yellow-500/5 border-b border-yellow-500/20">
              <p className="text-xs text-yellow-400">
                Some files had extraction errors. Check the Error column for details.
              </p>
            </div>
          )}

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--card-border)]">
                  <th className="text-left py-3 px-4 text-xs text-[var(--text-tertiary)] font-medium uppercase tracking-wider">
                    File Name
                  </th>
                  {FIELDS.map((f) => (
                    <th
                      key={f.key}
                      className="text-left py-3 px-4 text-xs text-[var(--text-tertiary)] font-medium uppercase tracking-wider whitespace-nowrap"
                    >
                      {f.label}
                    </th>
                  ))}
                  {hasErrors && (
                    <th className="text-left py-3 px-4 text-xs text-red-500 dark:text-red-400 font-medium uppercase tracking-wider">
                      Error
                    </th>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--card-border)]">
                {predictions.map((pred, idx) => {
                  const hasRowError = !!pred._error;
                  return (
                    <tr
                      key={idx}
                      className={`hover:bg-brand-500/5 transition-colors ${
                        hasRowError ? "bg-red-500/[0.03]" : ""
                      }`}
                    >
                      <td className="py-3 px-4 text-[var(--text-secondary)] font-medium max-w-[200px] truncate" title={pred["File Name"]}>
                        {pred["File Name"]}
                      </td>
                      {FIELDS.map((f) => {
                        const val = pred[f.key as keyof BatchPrediction] as string;
                        return (
                          <td key={f.key} className="py-3 px-4 whitespace-nowrap">
                            {val ? (
                              <span className="text-[var(--text-primary)]">{val}</span>
                            ) : (
                              <span className={`${hasRowError ? "text-red-500/50 dark:text-red-500/50" : "text-[var(--text-faint)]"}`}>
                                {hasRowError ? "\u2014" : "\u2014"}
                              </span>
                            )}
                          </td>
                        );
                      })}
                      {hasErrors && (
                        <td className="py-3 px-4 max-w-[200px]">
                          {pred._error ? (
                            <span className="text-red-400 text-xs break-words" title={pred._error}>
                              {pred._error.length > 80
                                ? pred._error.slice(0, 80) + "..."
                                : pred._error}
                            </span>
                          ) : (
                            <span className="text-green-500/50 text-xs">OK</span>
                          )}
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!loading && predictions.length === 0 && !evalResult && !error && (
        <div className="glass-card p-12 text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-brand-600/10 flex items-center justify-center">
            <svg className="w-8 h-8 text-brand-500/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <p className="text-[var(--text-tertiary)] text-sm mb-1">No results yet</p>
          <p className="text-[var(--text-faint)] text-xs">
            Select a dataset and click &ldquo;Run Extraction&rdquo; to process all files
          </p>
        </div>
      )}
    </div>
  );
}
