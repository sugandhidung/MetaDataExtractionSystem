"use client";

import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  loading: boolean;
}

export default function FileUpload({ onFileSelect, loading }: FileUploadProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0 && !loading) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect, loading]
  );

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } =
    useDropzone({
      onDrop,
      accept: {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
          [".docx"],
        "image/png": [".png"],
        "image/jpeg": [".jpg", ".jpeg"],
        "image/tiff": [".tiff"],
        "image/bmp": [".bmp"],
      },
      maxFiles: 1,
      disabled: loading,
      maxSize: 20 * 1024 * 1024,
    });

  return (
    <div className="max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={`
          glass-card p-10 text-center cursor-pointer
          transition-all duration-300 group
          ${isDragActive ? "dropzone-active glow" : "hover:border-brand-500/30"}
          ${loading ? "opacity-50 cursor-not-allowed" : ""}
        `}
      >
        <input {...getInputProps()} />

        <div className="space-y-4">
          <div
            className={`
              mx-auto w-14 h-14 rounded-2xl flex items-center justify-center
              transition-all duration-300
              ${
                isDragActive
                  ? "bg-brand-500/20 scale-110"
                  : "bg-white/[0.03] group-hover:bg-brand-500/10"
              }
            `}
          >
            <svg
              className={`w-7 h-7 transition-colors ${
                isDragActive
                  ? "text-brand-400"
                  : "text-gray-500 group-hover:text-brand-400"
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>

          {isDragActive ? (
            <p className="text-brand-400 font-medium">Drop your file here</p>
          ) : (
            <div>
              <p className="text-[var(--text-secondary)] font-medium">
                Drop a document here, or{" "}
                <span className="text-brand-400">browse</span>
              </p>
              <p className="text-[var(--text-faint)] text-sm mt-1.5">
                Supports .docx and scanned images (.png, .jpg) &middot; Max 20MB
              </p>
            </div>
          )}

          {acceptedFiles.length > 0 && !loading && (
            <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-brand-500/10 border border-brand-500/20 rounded-lg">
              <svg
                className="w-4 h-4 text-brand-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <span className="text-sm text-brand-300">
                {acceptedFiles[0].name}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
