"use client";

import ThemeToggle from "./ThemeToggle";

export default function Header() {
  return (
    <header className="pt-12 pb-8 px-4 text-center relative">
      {/* Theme toggle — top right */}
      <div className="absolute top-4 right-4 sm:top-6 sm:right-6">
        <ThemeToggle />
      </div>

      <div className="max-w-3xl mx-auto">
        {/* Logo */}
        <div className="mb-6 inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-brand-600/10 border border-brand-500/20 float-animation">
          <svg
            className="w-8 h-8 text-brand-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>

        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-4">
          <span className="gradient-text">Meta</span>
          <span className="text-[var(--text-primary)]">Extract</span>
        </h1>

        <p className="text-[var(--text-tertiary)] text-lg max-w-xl mx-auto leading-relaxed">
          Extract metadata from rental agreements instantly.
          Upload a <span className="text-[var(--text-secondary)]">.docx</span> or{" "}
          <span className="text-[var(--text-secondary)]">scanned image</span> to get started.
        </p>

        <div className="flex flex-wrap justify-center gap-2 mt-6">
          {[
            "AI-Powered",
            "Multi-LLM",
            "OCR Support",
            "DOCX & PNG",
            "Instant Results",
          ].map((feature) => (
            <span
              key={feature}
              className="px-3 py-1 text-xs font-medium text-[var(--text-tertiary)] border border-[var(--card-border)] rounded-full bg-[var(--card-bg)]"
            >
              {feature}
            </span>
          ))}
        </div>
      </div>
    </header>
  );
}
