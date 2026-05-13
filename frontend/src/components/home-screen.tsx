"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { MapPin, Sparkles, Star, UtensilsCrossed } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { FoodHero } from "@/components/food-hero";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { ThemedSelect } from "@/components/themed-select";
import { getHealth, getLocations, postRecommendations } from "@/lib/api";
import type { RecommendationResponse } from "@/lib/types";

const QUICK_CUISINES = ["North Indian", "South Indian", "Korean", "Thai"] as const;
/** Used when `/api/locations` is unavailable so the dropdown still works offline. */
const FALLBACK_LOCATIONS = [
  "Bellandur",
  "BTM Layout",
  "HSR Layout",
  "Indiranagar",
  "Jayanagar",
  "Koramangala",
  "MG Road",
  "Marathahalli",
  "Sarjapur Road",
  "Whitefield",
] as const;
const RATING_OPTIONS = [
  { value: "3", label: "3.0+" },
  { value: "3.5", label: "3.5+" },
  { value: "4", label: "4.0+" },
  { value: "4.5", label: "4.5+" },
] as const;

function formatCuisines(c: unknown): string {
  if (Array.isArray(c)) return c.map(String).join(", ");
  if (c == null) return "";
  return String(c);
}

export function HomeScreen() {
  const [location, setLocation] = useState("");
  const [budgetMax, setBudgetMax] = useState(1500);
  const [minRating, setMinRating] = useState("");
  const [cuisines, setCuisines] = useState<string[]>([]);
  const [cuisineDraft, setCuisineDraft] = useState("");
  const [extra, setExtra] = useState("");

  const health = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    retry: 1,
    refetchOnWindowFocus: false,
  });

  const locationsQuery = useQuery({
    queryKey: ["locations"],
    queryFn: getLocations,
    retry: 1,
    staleTime: 30 * 60 * 1000,
    refetchOnWindowFocus: false,
  });

  const apiStatus = health.isLoading ? "loading" : health.isError ? "error" : "ok";

  const mutation = useMutation({
    mutationFn: postRecommendations,
  });

  const canSubmit = useMemo(() => location.trim().length > 0, [location]);

  const locationOptions = useMemo(() => {
    const api = locationsQuery.data?.locations;
    const hasApi = Array.isArray(api) && api.length > 0;
    const base = hasApi ? [...api] : [...FALLBACK_LOCATIONS];
    const set = new Set(base.map((s) => s.trim()).filter(Boolean));
    const cur = location.trim();
    if (cur) set.add(cur);
    return Array.from(set).sort((a, b) => a.localeCompare(b, undefined, { sensitivity: "base" }));
  }, [locationsQuery.data, location]);

  const locationSelectOptions = useMemo(
    () => [{ value: "", label: "Select location" }, ...locationOptions.map((loc) => ({ value: loc, label: loc }))],
    [locationOptions],
  );

  const ratingSelectOptions = useMemo(
    () => [{ value: "", label: "Any" }, ...RATING_OPTIONS.map((o) => ({ value: o.value, label: o.label }))],
    [],
  );

  useEffect(() => {
    if (locationOptions.length === 0) return;
    const cur = location.trim();
    if (!cur) return;
    if (!locationOptions.some((o) => o === cur)) {
      const byCase = locationOptions.find((o) => o.toLowerCase() === cur.toLowerCase());
      setLocation(byCase ?? locationOptions[0]);
    }
  }, [locationOptions, location]);

  const budgetPct = Math.min(100, Math.max(0, (budgetMax / 5000) * 100));

  function addCuisine(name: string) {
    const t = name.trim();
    if (!t) return;
    setCuisines((prev) => (prev.some((c) => c.toLowerCase() === t.toLowerCase()) ? prev : [...prev, t]));
  }

  function removeCuisine(name: string) {
    setCuisines((prev) => prev.filter((c) => c !== name));
  }

  function onCuisineKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      const parts = cuisineDraft
        .split(/[,]+/)
        .map((s) => s.trim())
        .filter(Boolean);
      parts.forEach(addCuisine);
      setCuisineDraft("");
    }
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const mr = minRating.trim() ? Number(minRating) : null;
    mutation.mutate({
      preferences: {
        location: location.trim(),
        budget: { min: 0, max: budgetMax },
        cuisines: [...cuisines],
        minimum_rating: mr != null && Number.isFinite(mr) ? mr : null,
        additional_preferences: extra.trim() || null,
      },
      top_k: 5,
    });
  }

  const data = mutation.data as RecommendationResponse | undefined;

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader apiStatus={apiStatus} />

      <FoodHero />

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 pb-8 pt-8 sm:px-6 sm:pt-10">
        <section className="rounded-3xl border border-zomato-border bg-zomato-card p-6 shadow-xl sm:p-8 md:p-10">
          <div className="mb-8 max-w-2xl">
            <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">Find your next meal.</h1>
            <p className="mt-2 text-base text-zomato-muted sm:text-lg">
              Tell Zomato AI what you&apos;re craving and let us handle the rest.
            </p>
          </div>

          <form onSubmit={onSubmit} className="space-y-8">
            <div className="grid gap-6 md:grid-cols-2">
              <div className="md:col-span-1">
                <label htmlFor="location" className="mb-2 block text-xs font-semibold uppercase tracking-wider text-zomato-muted">
                  Location
                </label>
                <ThemedSelect
                  id="location"
                  value={location}
                  onChange={setLocation}
                  options={locationSelectOptions}
                  aria-busy={locationsQuery.isLoading}
                  leading={<MapPin className="h-5 w-5 text-zinc-500" aria-hidden />}
                />
              </div>

              <div className="md:col-span-1">
                <label htmlFor="minRating" className="mb-2 block text-xs font-semibold uppercase tracking-wider text-zomato-muted">
                  Minimum rating
                </label>
                <ThemedSelect
                  id="minRating"
                  value={minRating}
                  onChange={setMinRating}
                  options={ratingSelectOptions}
                  leading={<Star className="h-5 w-5 text-brand-green" aria-hidden />}
                />
              </div>
            </div>

            <div>
              <label htmlFor="budget" className="mb-2 block text-xs font-semibold uppercase tracking-wider text-zomato-muted">
                Budget max (for two)
              </label>
              <div className="relative pt-2">
                <output
                  className="pointer-events-none absolute -top-1 z-10 min-w-[3.5rem] -translate-x-1/2 rounded-lg bg-brand-green px-2.5 py-1 text-center text-xs font-bold text-zomato-dark shadow-lg"
                  style={{ left: `${budgetPct}%` }}
                  htmlFor="budget"
                >
                  ₹{budgetMax}
                </output>
                <input
                  id="budget"
                  name="budget"
                  type="range"
                  min={0}
                  max={5000}
                  step={100}
                  value={budgetMax}
                  onChange={(e) => setBudgetMax(Number(e.target.value))}
                  className="budget-slider w-full"
                  style={{
                    background: `linear-gradient(to right, #26D367 0%, #26D367 ${budgetPct}%, #2A2A2A ${budgetPct}%, #2A2A2A 100%)`,
                  }}
                  aria-valuemin={0}
                  aria-valuemax={5000}
                  aria-valuenow={budgetMax}
                  aria-valuetext={`₹${budgetMax}`}
                />
                <div className="mt-2 flex justify-between text-[11px] font-medium text-zinc-600">
                  <span>₹0</span>
                  <span>₹1000</span>
                  <span>₹2000</span>
                  <span>₹3000</span>
                  <span>₹4000</span>
                  <span>₹5000</span>
                </div>
              </div>
            </div>

            <div>
              <label htmlFor="cuisines" className="mb-2 block text-xs font-semibold uppercase tracking-wider text-zomato-muted">
                Cuisines <span className="font-normal normal-case text-zinc-600">(optional)</span>
              </label>
              <div className="relative">
                <UtensilsCrossed className="pointer-events-none absolute left-3 top-3.5 h-5 w-5 text-zinc-500" aria-hidden />
                <input
                  id="cuisines"
                  name="cuisine-tags"
                  autoComplete="off"
                  className="w-full rounded-xl border border-zomato-border bg-zomato-dark py-3.5 pl-11 pr-4 text-sm text-white outline-none ring-brand-green/30 transition placeholder:text-zinc-600 focus:border-brand-green focus:ring-2"
                  placeholder="Add cuisines (optional)"
                  value={cuisineDraft}
                  onChange={(e) => setCuisineDraft(e.target.value)}
                  onKeyDown={onCuisineKeyDown}
                  onBlur={() => {
                    if (cuisineDraft.trim()) {
                      cuisineDraft
                        .split(/[,]+/)
                        .map((s) => s.trim())
                        .filter(Boolean)
                        .forEach(addCuisine);
                      setCuisineDraft("");
                    }
                  }}
                />
              </div>
              <div className="mt-3 flex flex-wrap items-center gap-2">
                {cuisines.map((c) => (
                  <button
                    key={c}
                    type="button"
                    onClick={() => removeCuisine(c)}
                    className="inline-flex items-center gap-1.5 rounded-full bg-brand-green px-3 py-1.5 text-xs font-semibold text-zomato-dark transition hover:bg-brand-green-dim"
                  >
                    {c}
                    <span className="text-zomato-dark/80" aria-hidden>
                      ×
                    </span>
                  </button>
                ))}
                {QUICK_CUISINES.filter((q) => !cuisines.some((c) => c.toLowerCase() === q.toLowerCase())).map((q) => (
                  <button
                    key={q}
                    type="button"
                    onClick={() => addCuisine(q)}
                    className="rounded-full border border-zomato-border bg-zomato-dark px-3 py-1.5 text-xs font-medium text-zomato-muted transition hover:border-zinc-600 hover:text-white"
                  >
                    + {q}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label htmlFor="extra" className="mb-2 block text-xs font-semibold uppercase tracking-wider text-zomato-muted">
                Additional preferences <span className="font-normal normal-case text-zinc-600">(optional)</span>
              </label>
              <textarea
                id="extra"
                name="extra"
                rows={4}
                className="w-full resize-y rounded-xl border border-zomato-border bg-zomato-dark px-4 py-3 text-sm text-white outline-none ring-brand-green/30 transition placeholder:text-zinc-600 focus:border-brand-green focus:ring-2"
                placeholder="Additional notes (optional)"
                value={extra}
                onChange={(e) => setExtra(e.target.value)}
              />
            </div>

            {health.isError && (
              <p className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-200" role="alert">
                Can&apos;t reach the API. Start the backend:{" "}
                <code className="rounded bg-zomato-dark px-1.5 py-0.5 text-xs">python -m uvicorn backend.app.main:app --reload --port 8000</code>
              </p>
            )}

            {mutation.isError && (
              <p className="rounded-lg border border-zomato-red/40 bg-zomato-red/10 px-4 py-3 text-sm text-red-200" role="alert">
                {mutation.error instanceof Error ? mutation.error.message : "Something went wrong."}
              </p>
            )}

            <button
              type="submit"
              disabled={!canSubmit || mutation.isPending}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-zomato-red py-4 text-base font-semibold text-white shadow-lg transition hover:bg-zomato-red-hover disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Sparkles className="h-5 w-5" strokeWidth={2} aria-hidden />
              {mutation.isPending ? "Finding recommendations…" : "Get recommendations"}
            </button>
          </form>
        </section>

        {data && (
          <section className="mt-12 space-y-4" aria-live="polite">
            <div className="flex flex-wrap items-end justify-between gap-2 border-b border-zomato-border pb-3">
              <h2 className="text-xl font-semibold text-white">Your picks</h2>
              <p className="text-xs text-zomato-muted">
                {data.metadata.model} · {data.metadata.processing_time_ms.toFixed(0)} ms · {data.metadata.shortlist_size}{" "}
                candidates
              </p>
            </div>
            <ol className="grid gap-4 sm:grid-cols-2">
              {data.recommendations.map((r) => (
                <li
                  key={`${r.rank}-${r.restaurant_name}`}
                  className="rounded-2xl border border-zomato-border bg-zomato-card p-5 transition hover:border-brand-green/40"
                >
                  <p className="text-xs font-semibold uppercase tracking-wide text-brand-green">#{r.rank}</p>
                  <h3 className="mt-1 text-lg font-semibold text-white">{r.restaurant_name}</h3>
                  <p className="mt-1 text-sm text-zomato-muted">
                    {[r.city, r.rating != null ? `★ ${r.rating}` : null, r.cost_estimate != null ? `~₹${r.cost_estimate}` : null]
                      .filter(Boolean)
                      .join(" · ")}
                  </p>
                  {formatCuisines(r.cuisines) ? (
                    <p className="mt-1 text-xs text-zinc-500">{formatCuisines(r.cuisines)}</p>
                  ) : null}
                  <p className="mt-3 text-sm leading-relaxed text-zinc-300">{r.reason}</p>
                </li>
              ))}
            </ol>
          </section>
        )}

        <SiteFooter />
      </main>
    </div>
  );
}
