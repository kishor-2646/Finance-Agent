"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import ImportCsv from "./ImportCsv";
import Insights from "./Insights";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const CATEGORIES = [
    "Food", "Groceries", "Transport", "Shopping", "Bills", "Entertainment",
    "Health", "Personal Care", "Education", "Transfer", "Other",
];

type Draft = {
    date: string;
    amount: string;
    merchant: string;
    payment_app: string;
    category: string;
    category_source: string | null;
    confidence: string | null;
};

type Expense = {
    id: number;
    txn_date: string;
    amount: string;
    merchant: string | null;
    category: string;
    payment_app: string | null;
};

async function errorText(res: Response): Promise<string> {
    try {
        const body = await res.json();
        if (typeof body.detail === "string") return body.detail;
        if (Array.isArray(body.detail)) return body.detail.map((d: { msg: string }) => d.msg).join("; ");
    } catch { }
    return `Request failed (${res.status})`;
}

export default function Home() {
    const [file, setFile] = useState<File | null>(null);
    const [draft, setDraft] = useState<Draft | null>(null);
    const [extracting, setExtracting] = useState(false);
    const [saving, setSaving] = useState(false);
    const [duplicate, setDuplicate] = useState(false);
    const [message, setMessage] = useState<{ kind: "error" | "ok"; text: string } | null>(null);
    const [expenses, setExpenses] = useState<Expense[]>([]);

    const loadExpenses = useCallback(async () => {
        try {
            const res = await fetch(`${API}/expenses?limit=100`);
            if (res.ok) setExpenses(await res.json());
        } catch {
            setMessage({ kind: "error", text: "Cannot reach the backend. Is uvicorn running on port 8000?" });
        }
    }, []);

    useEffect(() => {
        let cancelled = false;
        fetch(`${API}/expenses?limit=100`)
            .then((res) => (res.ok ? res.json() : null))
            .then((rows) => {
                if (!cancelled && rows) setExpenses(rows);
            })
            .catch(() => {
                if (!cancelled) setMessage({ kind: "error", text: "Cannot reach the backend. Is uvicorn running on port 8000?" });
            });
        return () => {
            cancelled = true;
        };
    }, []);

    const preview = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);
    useEffect(() => {
        return () => {
            if (preview) URL.revokeObjectURL(preview);
        };
    }, [preview]);

    function pick(f: File | null) {
        setFile(f);
        setDraft(null);
        setDuplicate(false);
        setMessage(null);
    }

    async function extract() {
        if (!file) return;
        setExtracting(true);
        setMessage(null);
        setDuplicate(false);
        try {
            const form = new FormData();
            form.append("file", file);
            const res = await fetch(`${API}/extract`, { method: "POST", body: form });
            if (!res.ok) throw new Error(await errorText(res));
            const d = await res.json();
            setDraft({
                date: d.date ?? "",
                amount: d.amount != null ? String(d.amount) : "",
                merchant: d.merchant ?? "",
                payment_app: d.payment_app ?? "",
                category: CATEGORIES.includes(d.category) ? d.category : "Other",
                category_source: d.category_source ?? null,
                confidence: d.confidence ?? null,
            });
            if (d.confidence === "low" || d.amount == null || !d.date) {
                setMessage({ kind: "error", text: "Some fields could not be read. Please fill them in before saving." });
            }
        } catch (e) {
            setMessage({ kind: "error", text: e instanceof Error ? e.message : "Extraction failed" });
        } finally {
            setExtracting(false);
        }
    }

    async function save(force = false) {
        if (!draft) return;
        setSaving(true);
        setMessage(null);
        try {
            const res = await fetch(`${API}/expenses${force ? "?force=true" : ""}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    date: draft.date || null,
                    amount: draft.amount === "" ? null : Number(draft.amount),
                    merchant: draft.merchant || null,
                    payment_app: draft.payment_app || null,
                    category: draft.category,
                    category_source: draft.category_source,
                    confidence: draft.confidence,
                    source: "screenshot",
                }),
            });
            if (res.status === 409) {
                setDuplicate(true);
                setMessage({ kind: "error", text: await errorText(res) });
                return;
            }
            if (!res.ok) throw new Error(await errorText(res));
            setMessage({ kind: "ok", text: "Expense saved." });
            setDraft(null);
            setFile(null);
            setDuplicate(false);
            await loadExpenses();
        } catch (e) {
            setMessage({ kind: "error", text: e instanceof Error ? e.message : "Save failed" });
        } finally {
            setSaving(false);
        }
    }

    async function remove(id: number) {
        const res = await fetch(`${API}/expenses/${id}`, { method: "DELETE" });
        if (res.ok) setExpenses((rows) => rows.filter((r) => r.id !== id));
    }

    const total = expenses.reduce((sum, e) => sum + Number(e.amount), 0);
    const input =
        "w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500";

    return (
        <main className="mx-auto max-w-5xl px-4 py-8 text-slate-900">
            <h1 className="text-2xl font-semibold">Finance Agent</h1>
            <p className="mt-1 text-sm text-slate-600">
                Upload a payment screenshot, check what was read, and save it. Use mock or redacted screenshots only.
            </p>

            {message && (
                <div
                    role="status"
                    className={`mt-4 rounded-md border px-3 py-2 text-sm ${message.kind === "ok"
                            ? "border-emerald-300 bg-emerald-50 text-emerald-800"
                            : "border-amber-300 bg-amber-50 text-amber-900"
                        }`}
                >
                    {message.text}
                </div>
            )}

            <section className="mt-6 grid gap-6 md:grid-cols-2">
                <div className="rounded-lg border border-slate-200 bg-white p-4">
                    <h2 className="text-sm font-medium">1. Screenshot</h2>
                    <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => pick(e.target.files?.[0] ?? null)}
                        className="mt-3 block w-full text-sm file:mr-3 file:rounded-md file:border-0 file:bg-indigo-600 file:px-3 file:py-2 file:text-sm file:text-white hover:file:bg-indigo-700"
                    />
                    {preview && (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={preview} alt="Selected screenshot" className="mt-3 max-h-80 rounded-md border border-slate-200 object-contain" />
                    )}
                    <button
                        onClick={extract}
                        disabled={!file || extracting}
                        className="mt-3 w-full rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        {extracting ? "Reading screenshot…" : "Extract details"}
                    </button>
                </div>

                <div className="rounded-lg border border-slate-200 bg-white p-4">
                    <h2 className="text-sm font-medium">2. Review and save</h2>
                    {!draft ? (
                        <p className="mt-3 text-sm text-slate-500">Extracted details will appear here for you to check and edit.</p>
                    ) : (
                        <form
                            className="mt-3 space-y-3"
                            onSubmit={(e) => {
                                e.preventDefault();
                                save(false);
                            }}
                        >
                            <label className="block text-sm">
                                Date
                                <input type="date" className={input} value={draft.date} onChange={(e) => setDraft({ ...draft, date: e.target.value })} />
                            </label>
                            <label className="block text-sm">
                                Amount (₹)
                                <input type="number" step="0.01" min="0" className={input} value={draft.amount} onChange={(e) => setDraft({ ...draft, amount: e.target.value })} />
                            </label>
                            <label className="block text-sm">
                                Merchant
                                <input className={input} value={draft.merchant} onChange={(e) => setDraft({ ...draft, merchant: e.target.value })} />
                            </label>
                            <label className="block text-sm">
                                Payment app
                                <input className={input} value={draft.payment_app} onChange={(e) => setDraft({ ...draft, payment_app: e.target.value })} />
                            </label>
                            <label className="block text-sm">
                                Category
                                <select className={input} value={draft.category} onChange={(e) => setDraft({ ...draft, category: e.target.value, category_source: "user" })}>
                                    {CATEGORIES.map((c) => (
                                        <option key={c}>{c}</option>
                                    ))}
                                </select>
                            </label>
                            <div className="flex gap-2">
                                <button
                                    type="submit"
                                    disabled={saving}
                                    className="flex-1 rounded-md bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
                                >
                                    {saving ? "Saving…" : "Save expense"}
                                </button>
                                {duplicate && (
                                    <button
                                        type="button"
                                        onClick={() => save(true)}
                                        disabled={saving}
                                        className="rounded-md border border-slate-300 px-3 py-2 text-sm hover:bg-slate-50"
                                    >
                                        Save anyway
                                    </button>
                                )}
                            </div>
                        </form>
                    )}
                </div>
            </section>

            <section className="mt-8 rounded-lg border border-slate-200 bg-white p-4">
                <div className="flex items-baseline justify-between">
                    <h2 className="text-sm font-medium">Saved expenses</h2>
                    <span className="text-sm text-slate-600">
                        {expenses.length} items · ₹{total.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </span>
                </div>
                {expenses.length === 0 ? (
                    <p className="mt-3 text-sm text-slate-500">Nothing saved yet.</p>
                ) : (
                    <div className="mt-3 overflow-x-auto">
                        <table className="w-full text-left text-sm">
                            <thead className="text-xs uppercase text-slate-500">
                                <tr>
                                    <th className="py-2 pr-4">Date</th>
                                    <th className="py-2 pr-4">Merchant</th>
                                    <th className="py-2 pr-4">Category</th>
                                    <th className="py-2 pr-4 text-right">Amount</th>
                                    <th className="py-2" />
                                </tr>
                            </thead>
                            <tbody>
                                {expenses.map((e) => (
                                    <tr key={e.id} className="border-t border-slate-100">
                                        <td className="py-2 pr-4 whitespace-nowrap">{e.txn_date}</td>
                                        <td className="py-2 pr-4">{e.merchant ?? "—"}</td>
                                        <td className="py-2 pr-4">{e.category}</td>
                                        <td className="py-2 pr-4 text-right tabular-nums">₹{Number(e.amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
                                        <td className="py-2 text-right">
                                            <button onClick={() => remove(e.id)} className="text-xs text-red-600 hover:underline">
                                                Delete
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </section>

            <ImportCsv onDone={loadExpenses} />
            <Insights refreshKey={expenses.length} />
        </main>
    );
}