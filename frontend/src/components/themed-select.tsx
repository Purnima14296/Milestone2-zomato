"use client";

import { ChevronDown } from "lucide-react";
import type { ReactNode } from "react";
import { useCallback, useEffect, useId, useRef, useState } from "react";

export type ThemedSelectOption = { value: string; label: string };

type ThemedSelectProps = {
  id: string;
  value: string;
  onChange: (value: string) => void;
  options: ThemedSelectOption[];
  disabled?: boolean;
  "aria-busy"?: boolean;
  leading?: ReactNode;
};

export function ThemedSelect({
  id,
  value,
  onChange,
  options,
  disabled = false,
  "aria-busy": ariaBusy,
  leading,
}: ThemedSelectProps) {
  const [open, setOpen] = useState(false);
  const [highlight, setHighlight] = useState(0);
  const rootRef = useRef<HTMLDivElement>(null);
  const listId = useId();

  const selected = options.find((o) => o.value === value);
  const selectedLabel = selected?.label ?? "";
  const isPlaceholder = value === "";

  const openMenu = useCallback(() => {
    if (disabled) return;
    const idx = Math.max(
      0,
      options.findIndex((o) => o.value === value),
    );
    setHighlight(idx);
    setOpen(true);
  }, [disabled, options, value]);

  const closeMenu = useCallback(() => setOpen(false), []);

  useEffect(() => {
    if (!open) return;
    function onDocMouseDown(e: MouseEvent) {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) closeMenu();
    }
    document.addEventListener("mousedown", onDocMouseDown);
    return () => document.removeEventListener("mousedown", onDocMouseDown);
  }, [open, closeMenu]);

  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") {
        e.preventDefault();
        closeMenu();
        return;
      }
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setHighlight((h) => Math.min(h + 1, options.length - 1));
      }
      if (e.key === "ArrowUp") {
        e.preventDefault();
        setHighlight((h) => Math.max(h - 1, 0));
      }
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        const o = options[highlight];
        if (o) {
          onChange(o.value);
          closeMenu();
        }
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, highlight, options, onChange, closeMenu]);

  return (
    <div ref={rootRef} className="relative">
      {leading ? (
        <span className="pointer-events-none absolute left-3 top-1/2 z-10 -translate-y-1/2" aria-hidden>
          {leading}
        </span>
      ) : null}
      <button
        id={id}
        type="button"
        disabled={disabled}
        aria-busy={ariaBusy}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={open ? listId : undefined}
        className="flex w-full items-center justify-between rounded-xl border border-zomato-border bg-zomato-dark py-3.5 pl-11 pr-10 text-left text-sm text-white outline-none ring-brand-green/30 transition hover:border-zinc-600 focus-visible:border-brand-green focus-visible:ring-2 disabled:cursor-not-allowed disabled:opacity-50 data-[open=true]:border-brand-green data-[open=true]:ring-2"
        data-open={open}
        onClick={() => (open ? closeMenu() : openMenu())}
      >
        <span className={`min-w-0 truncate ${isPlaceholder ? "text-zinc-500" : "text-white"}`}>
          {selectedLabel || "—"}
        </span>
        <ChevronDown
          className={`pointer-events-none absolute right-3 top-1/2 h-5 w-5 shrink-0 -translate-y-1/2 text-zinc-500 transition-transform ${open ? "rotate-180" : ""}`}
          aria-hidden
        />
      </button>

      {open && options.length > 0 ? (
        <ul
          id={listId}
          role="listbox"
          aria-labelledby={id}
          className="absolute left-0 right-0 z-[100] mt-1 max-h-60 overflow-auto rounded-xl border border-zomato-border bg-zomato-card py-1 shadow-2xl ring-1 ring-black/40"
        >
          {options.map((o, i) => {
            const isSelected = o.value === value;
            const isHi = i === highlight;
            return (
              <li key={`${id}-${o.value || "__none"}-${i}`} role="presentation" className="px-1">
                <button
                  type="button"
                  role="option"
                  aria-selected={isSelected}
                  tabIndex={-1}
                  className={`w-full rounded-lg px-3 py-2.5 text-left text-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-green/60 ${
                    isHi
                      ? "bg-brand-green/25 text-white"
                      : isSelected
                        ? "bg-brand-green/10 text-white hover:bg-brand-green/20"
                        : "text-zinc-200 hover:bg-brand-green/20 hover:text-white"
                  }`}
                  onMouseEnter={() => setHighlight(i)}
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => {
                    onChange(o.value);
                    closeMenu();
                  }}
                >
                  {o.label}
                </button>
              </li>
            );
          })}
        </ul>
      ) : null}
    </div>
  );
}
