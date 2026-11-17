import type { InputHTMLAttributes } from "react";

type SearchInputProps = Omit<InputHTMLAttributes<HTMLInputElement>, "type">;

export function SearchInput({ className = "", ...props }: SearchInputProps) {
  return (
    <div className={`relative ${className}`}>
      <svg
        aria-hidden="true"
        viewBox="0 0 20 20"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        className="text-fg-muted pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2"
      >
        <circle cx="9" cy="9" r="6" />
        <path d="m14 14 3.5 3.5" strokeLinecap="round" />
      </svg>
      <input
        type="search"
        className="border-line bg-surface text-fg placeholder:text-fg-muted focus:border-primary w-full rounded-lg border py-2 pr-3 pl-9 text-sm focus:outline-none"
        {...props}
      />
    </div>
  );
}
