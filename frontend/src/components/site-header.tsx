"use client";

import { Bell, History, User } from "lucide-react";
import Link from "next/link";

export type ApiDotStatus = "loading" | "ok" | "error";

export function SiteHeader({ apiStatus }: { apiStatus: ApiDotStatus }) {
  const dot =
    apiStatus === "loading"
      ? "bg-zinc-500"
      : apiStatus === "ok"
        ? "bg-brand-green"
        : "bg-zomato-red";

  return (
    <header className="sticky top-0 z-50 border-b border-zomato-border bg-zomato-dark/95 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <Link href="/" className="shrink-0 text-xl font-bold tracking-tight text-zomato-red">
          Zomato AI
        </Link>

        <nav className="hidden flex-1 justify-center md:flex" aria-label="Main">
          <div className="flex items-center gap-10 text-sm font-medium text-zinc-400">
            <span className="relative cursor-default text-white">
              Explore
              <span className="absolute -bottom-1 left-0 right-0 h-0.5 rounded-full bg-zomato-red" />
            </span>
            <button type="button" className="transition hover:text-white">
              History
            </button>
            <button type="button" className="transition hover:text-white">
              Notifications
            </button>
          </div>
        </nav>

        <div className="flex items-center gap-2 sm:gap-3">
          <span
            className="mr-1 hidden items-center gap-1.5 text-[10px] uppercase tracking-wide text-zinc-500 sm:flex"
            title="API connection"
          >
            <span className={`h-2 w-2 rounded-full ${dot}`} aria-hidden />
            <span className="sr-only">API {apiStatus}</span>
          </span>
          <button type="button" className="rounded-full p-2 text-zinc-400 transition hover:bg-zomato-card hover:text-white" aria-label="History">
            <History className="h-5 w-5" />
          </button>
          <button type="button" className="rounded-full p-2 text-zinc-400 transition hover:bg-zomato-card hover:text-white" aria-label="Notifications">
            <Bell className="h-5 w-5" />
          </button>
          <button
            type="button"
            className="flex h-9 w-9 items-center justify-center rounded-full border border-zomato-border bg-zomato-card text-zinc-300 transition hover:border-brand-green hover:text-white"
            aria-label="Account"
          >
            <User className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  );
}
