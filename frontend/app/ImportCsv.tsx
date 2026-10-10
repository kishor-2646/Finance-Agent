"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Result = {
  imported: number;
  skipped_duplicates: number;
  skipped_credits: number;
  invalid_rows: number;
  invalid_examples: string[];
};

export default function ImportCsv({ onDone }: { onDone: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function upload() {
    if (!file) return;
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API}/statements/import`, { method: "POST", body: form });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(typeof body.detail === "string" ? body.detail : `Import failed (${res.status})`);
      setResult(body);
      setFile(null);
      onDone();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Import failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mt-8 rounded-lg border border-slate-200 bg-white p-4">
      <h2 className="text-sm font-medium">Import a bank statement (CSV)</h2>
      <p className="mt-1 text-sm text-slate-600">
        Needs a header row with a date, a description or narration, and an amount or debit column. Credits are skipped,
        and rows you already saved are not added twice. Use a mock or redacted file.
      </p>
      <div className="mt-3 flex flex-wrap items-center gap-3">
        <input
          type="file"
          accept=".csv,text/csv"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="text-sm file:mr-3 file:rounded-md file:border-0 file:bg-slate-700 file:px-3 file:py-2 file:text-sm file:text-white hover:file:bg-slate-800"
        />
        <button
          onClick={upload}
          disabled={!file || busy}
          className="rounded-md bg-slate-800 px-3 py-2 text-sm font-medium text-white hover:bg-slate-900 disabled:opacity-50"
        >
          {busy ? "Importing…" : "Import"}
        </button>
      </div>
      {error && <p className="mt-3 text-sm text-amber-800">{error}</p>}
      {result && (
        <div className="mt-3 text-sm text-slate-700" role="status">
          <p>
            Imported <strong>{result.imported}</strong> · duplicates skipped {result.skipped_duplicates} · credits skipped{" "}
            {result.skipped_credits} · unreadable rows {result.invalid_rows}
          </p>
          {result.invalid_examples.length > 0 && (
            <ul className="mt-1 list-disc pl-5 text-xs text-slate-500">
              {result.invalid_examples.map((x) => (
                <li key={x}>{x}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </section>
  );
}
