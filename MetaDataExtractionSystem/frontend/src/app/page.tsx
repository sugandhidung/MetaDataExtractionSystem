"use client";

import { useState, useEffect } from "react";
import FileUpload from "@/components/FileUpload";
import ResultsDisplay from "@/components/ResultsDisplay";
import Header from "@/components/Header";
import BatchPanel from "@/components/BatchPanel";
import ProviderBanner from "@/components/ProviderBanner";

export interface ExtractionMetadata {
  agreement_value: string | null;
  agreement_start_date: string | null;
  agreement_end_date: string | null;
  renewal_notice_days: string | null;
  party_one: string | null;
  party_two: string | null;
}

export interface ExtractionResult {
  filename: string;
  status: string;
  error_message: string | null;
  extracted_text_preview: string | null;
  metadata: ExtractionMetadata;
  confidence: string | null;
  provider: string | null;
}

export interface ProviderInfo {
  provider: string | null;
  model: string | null;
  available: boolean;
  help?: string;
}

export default function Home() {
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"upload" | "batch">("upload");
  const [providerInfo, setProviderInfo] = useState<ProviderInfo | null>(null);

  useEffect(() => {
    fetch("/api/provider")
      .then((r) => r.json())
      .then((data: ProviderInfo) => setProviderInfo(data))
      .catch(() => setProviderInfo({ provider: null, model: null, available: false }));
  }, []);

  const handleExtract = async (file: File) => {
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/extract", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error: ${response.status}`);
      }

      const data: ExtractionResult = await response.json();
      setResult(data);

      if (data.status === "error" && data.error_message) {
        setError(data.error_message);
      }
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "An unexpected error occurred";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative">
      {/* Background gradient effects */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-brand-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-brand-400/5 rounded-full blur-3xl" />
        <div className="absolute inset-0 bg-[var(--background)] -z-20" />
      </div>

      <Header />

      {/* Provider status banner */}
      <ProviderBanner info={providerInfo} />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        {/* Tab Navigation */}
        <div className="flex justify-center mb-10">
          <div className="glass-card inline-flex p-1 gap-1">
            <button
              onClick={() => setActiveTab("upload")}
              className={`px-6 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                activeTab === "upload"
                  ? "bg-brand-600 text-white shadow-lg"
                  : "text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface)]"
              }`}
            >
              Single Upload
            </button>
            <button
              onClick={() => setActiveTab("batch")}
              className={`px-6 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                activeTab === "batch"
                  ? "bg-brand-600 text-white shadow-lg"
                  : "text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface)]"
              }`}
            >
              Batch Processing
            </button>
          </div>
        </div>

        {activeTab === "upload" ? (
          <div className="space-y-8 animate-fade-in">
            <FileUpload onFileSelect={handleExtract} loading={loading} />

            {error && (
              <div className="glass-card p-5 border !border-red-500/30 animate-slide-up">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 mt-1.5 bg-red-500 rounded-full flex-shrink-0" />
                  <div>
                    <p className="text-red-500 dark:text-red-400 text-sm font-medium">
                      Extraction Error
                    </p>
                    <p className="text-red-500/80 dark:text-red-400/80 text-sm mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {loading && (
              <div className="glass-card p-8 text-center animate-fade-in max-w-2xl mx-auto">
                <div className="inline-flex items-center gap-3">
                  <div className="relative w-5 h-5">
                    <div className="absolute inset-0 rounded-full border-2 border-brand-500/30" />
                    <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-brand-500 animate-spin" />
                  </div>
                  <span className="text-[var(--text-tertiary)] text-sm">
                    Analyzing document with AI
                    {providerInfo?.provider
                      ? ` (${providerInfo.provider})`
                      : ""}
                    ...
                  </span>
                </div>
              </div>
            )}

            {result && !loading && result.status !== "error" && (
              <ResultsDisplay result={result} />
            )}
          </div>
        ) : (
          <BatchPanel providerInfo={providerInfo} />
        )}
      </main>

      <footer className="border-t border-[var(--card-border)] py-6 text-center">
        <p className="text-xs text-[var(--text-faint)]">
          MetaExtract &mdash; AI-powered document metadata extraction &middot;
          Non-rule-based approach
        </p>
      </footer>
    </div>
  );
}
