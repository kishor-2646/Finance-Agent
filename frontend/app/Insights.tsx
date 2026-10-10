"use client";

import { useEffect, useState } from "react";
import { BarElement, CategoryScale, Chart as ChartJS, LinearScale, Tooltip } from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip);

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Summary = {
  month: string | null;
  available_months: string[];
  total: number;
  count: number;
  by_category: { category: string; total: number; share: number }[];
  by_month: { month: string; total: number }[];
};

type Tip = { id: string; principle: string; title: string; message: string };
type Advice = { month: string | null; tips: Tip[]; disclaimer: string };

const rupees = (n: number) => `₹${n.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;

export default function Insights({ refreshKey }: { refreshKey: number }) {
  const [month, setMonth] = useState<string>("");
  const [incomeInput, setIncomeInput] = useState("");
  const [income, setIncome] = useState<string>("");
  const [summary, setSummary] = useState<Summary | null>(null);
  const [advice, setAdvice] = useState<Advice | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const q = new URLSearchParams();
    if (month) q.set("month", month);
    const aq = new URLSearchParams(q);
    if (income) aq.set("income", income);

    Promise.all([
      fetch(`${API}/insights/summary?${q}`).then((r) => (r.ok ? r.json() : Promise.reject())),
      fetch(`${API}/insights/advice?${aq}`).then((r) => (r.ok ? r.json() : Promise.reject())),
    ])
      .then(([s, a]) => {
        if (cancelled) return;
        setSummary(s);
        setAdvice(a);
        setError(null);
      })
      .catch(() => {
        if (!cancelled) setError("Could not load insights. Is the backend running?");
      });
    return () => {
      cancelled = true;
    };
  }, [month, income, refreshKey]);

  if (error) return <p className="mt-8 text-sm text-amber-800">{error}</p>;
  if (!summary || !advice) return null;

  const cats = summary.by_category;

  return (
    <section className="mt-8 rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-sm font-medium">Dashboard</h2>
          <p className="text-sm text-slate-600">
            {summary.month ? `${summary.month} · ${summary.count} payments · ${rupees(summary.total)}` : "No data yet"}
          </p>
        </div>
        <div className="flex flex-wrap items-end gap-3">
          {summary.available_months.length > 1 && (
            <label className="text-xs text-slate-600">
              Month
              <select
                className="mt-1 block rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm text-slate-900"
                value={summary.month ?? ""}
                onChange={(e) => setMonth(e.target.value)}
              >
                {summary.available_months.map((m) => (
                  <option key={m}>{m}</option>
                ))}
              </select>
            </label>
          )}
          <form
            className="flex items-end gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              setIncome(incomeInput.trim());
            }}
          >
            <label className="text-xs text-slate-600">
              Monthly income (₹, optional)
              <input
                type="number"
                min="1"
                className="mt-1 block w-40 rounded-md border border-slate-300 px-2 py-1.5 text-sm text-slate-900"
                value={incomeInput}
                onChange={(e) => setIncomeInput(e.target.value)}
              />
            </label>
            <button className="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50">Update</button>
          </form>
        </div>
      </div>

      {cats.length > 0 && (
        <div className="mt-4" style={{ height: Math.max(160, cats.length * 36 + 40) }}>
          <Bar
            data={{
              labels: cats.map((c) => c.category),
              datasets: [{ data: cats.map((c) => c.total), backgroundColor: "#4f46e5", borderRadius: 4 }],
            }}
            options={{
              indexAxis: "y",
              maintainAspectRatio: false,
              plugins: {
                legend: { display: false },
                tooltip: {
                  callbacks: {
                    label: (ctx) => {
                      const c = cats[ctx.dataIndex];
                      return `${rupees(c.total)} (${c.share}%)`;
                    },
                  },
                },
              },
              scales: { x: { ticks: { callback: (v) => rupees(Number(v)) } } },
            }}
          />
        </div>
      )}

      <div className="mt-5 space-y-3">
        <h3 className="text-sm font-medium">Advice</h3>
        {advice.tips.map((t) => (
          <div key={t.id} className="rounded-md border border-slate-200 bg-slate-50 p-3">
            <p className="text-xs uppercase tracking-wide text-indigo-700">{t.principle}</p>
            <p className="mt-0.5 text-sm font-medium">{t.title}</p>
            <p className="mt-1 text-sm text-slate-700">{t.message}</p>
          </div>
        ))}
        <p className="text-xs text-slate-500">{advice.disclaimer}</p>
      </div>
    </section>
  );
}
