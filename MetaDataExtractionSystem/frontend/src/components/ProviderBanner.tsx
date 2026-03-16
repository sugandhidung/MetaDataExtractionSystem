"use client";

import { ProviderInfo } from "@/app/page";

interface Props {
  info: ProviderInfo | null;
}

export default function ProviderBanner({ info }: Props) {
  if (info === null) return null; // still loading

  if (info.available) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 mb-6">
        <div className="flex items-center justify-center gap-2 px-4 py-2 bg-green-500/5 border border-green-500/20 rounded-xl text-sm">
          <span className="w-2 h-2 bg-green-400 rounded-full" />
          <span className="text-green-400/90">
            Connected to <strong>{info.provider}</strong>
            {info.model ? ` (${info.model})` : ""}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 mb-6">
      <div className="px-4 py-3 bg-red-500/5 border border-red-500/20 rounded-xl text-sm">
        <div className="flex items-start gap-2">
          <span className="w-2 h-2 mt-1.5 bg-red-400 rounded-full flex-shrink-0" />
          <div>
            <p className="text-red-600 dark:text-red-400 font-medium">
              No LLM provider configured
            </p>
            <p className="text-red-500/70 dark:text-red-400/70 mt-1">
              Set one of the following environment variables on the backend, then
              restart:
            </p>
            <ul className="text-red-500/60 dark:text-red-400/60 mt-1 space-y-0.5 list-disc list-inside">
              <li>
                <code className="text-red-600/80 dark:text-red-300/80">OPENAI_API_KEY</code> — for
                OpenAI GPT models
              </li>
              <li>
                <code className="text-red-600/80 dark:text-red-300/80">GROQ_API_KEY</code> — for
                Groq (free at console.groq.com)
              </li>
              <li>
                Run <code className="text-red-600/80 dark:text-red-300/80">Ollama</code> locally on
                port 11434
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
