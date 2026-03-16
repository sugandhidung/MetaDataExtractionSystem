"use client";

import { ExtractionResult } from "@/app/page";

interface ResultsDisplayProps {
  result: ExtractionResult;
}

const FIELD_CONFIG = [
  {
    key: "agreement_value",
    label: "Agreement Value",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    format: (v: string) => `${v}`,
  },
  {
    key: "agreement_start_date",
    label: "Start Date",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
  },
  {
    key: "agreement_end_date",
    label: "End Date",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
  },
  {
    key: "renewal_notice_days",
    label: "Renewal Notice",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    format: (v: string) => `${v} days`,
  },
  {
    key: "party_one",
    label: "Party One (Landlord)",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    ),
  },
  {
    key: "party_two",
    label: "Party Two (Tenant)",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    ),
  },
];

function ConfidenceBadge({ confidence }: { confidence: string | null }) {
  const config = {
    high: { bg: "bg-green-500/10", border: "border-green-500/30", text: "text-green-400", dot: "bg-green-400" },
    medium: { bg: "bg-yellow-500/10", border: "border-yellow-500/30", text: "text-yellow-400", dot: "bg-yellow-400" },
    low: { bg: "bg-red-500/10", border: "border-red-500/30", text: "text-red-400", dot: "bg-red-400" },
  };
  const c = config[(confidence as keyof typeof config) || "low"];
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${c.bg} ${c.border} ${c.text} border`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
      {confidence?.charAt(0).toUpperCase()}
      {confidence?.slice(1)} Confidence
    </span>
  );
}

export default function ResultsDisplay({ result }: ResultsDisplayProps) {
  const metadata = result.metadata;

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-slide-up">
      {/* Header Card */}
      <div className="glass-card p-5 glow-success">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-green-500/10 flex items-center justify-center">
              <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <p className="text-[var(--text-primary)] font-medium text-sm">{result.filename}</p>
              <p className="text-[var(--text-faint)] text-xs">
                Extraction complete
                {result.provider ? ` via ${result.provider}` : ""}
              </p>
            </div>
          </div>
          <ConfidenceBadge confidence={result.confidence} />
        </div>
      </div>

      {/* Metadata Fields */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {FIELD_CONFIG.map((field) => {
          const value = metadata[field.key as keyof typeof metadata];
          const displayValue = value
            ? field.format
              ? field.format(value)
              : value
            : null;
          return (
            <div
              key={field.key}
              className={`glass-card p-4 transition-all duration-200 ${
                value ? "hover:border-brand-500/30" : "opacity-60"
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`mt-0.5 ${value ? "text-brand-400" : "text-[var(--text-faint)]"}`}>
                  {field.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-[var(--text-tertiary)] font-medium uppercase tracking-wider mb-1">
                    {field.label}
                  </p>
                  {displayValue ? (
                    <p className="text-[var(--text-primary)] font-medium text-sm break-words" title={displayValue}>
                      {displayValue}
                    </p>
                  ) : (
                    <p className="text-[var(--text-faint)] text-sm italic">Not found</p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Text Preview */}
      {result.extracted_text_preview && (
        <details className="glass-card group">
          <summary className="p-4 cursor-pointer flex items-center justify-between text-sm text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] transition-colors">
            <span className="font-medium">Extracted Text Preview</span>
            <svg className="w-4 h-4 transition-transform group-open:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </summary>
          <div className="px-4 pb-4">
            <pre className="text-xs text-[var(--text-tertiary)] whitespace-pre-wrap font-mono leading-relaxed bg-[var(--surface)] rounded-lg p-3 max-h-64 overflow-y-auto">
              {result.extracted_text_preview}
            </pre>
          </div>
        </details>
      )}
    </div>
  );
}
