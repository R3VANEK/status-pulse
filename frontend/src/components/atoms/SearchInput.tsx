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
        className="border-field-line bg-surface-muted text-fg placeholder:text-fg-muted focus:outline-primary rounded-control h-10.5 w-full border pr-3 pl-9 text-[13px] focus:outline-2"
        {...props}
      />
    </div>
  );
}
