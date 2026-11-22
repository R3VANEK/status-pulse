import { useState } from "react";

export function ActionsMenu() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative inline-block">
      <button
        type="button"
        aria-label="Project actions"
        aria-haspopup="menu"
        aria-expanded={isOpen}
        onClick={() => setIsOpen((open) => !open)}
        className="text-fg-muted hover:bg-surface-muted flex size-8 items-center justify-center rounded-lg"
      >
        <svg
          aria-hidden="true"
          viewBox="0 0 20 20"
          fill="currentColor"
          className="size-5"
        >
          <circle cx="4" cy="10" r="1.5" />
          <circle cx="10" cy="10" r="1.5" />
          <circle cx="16" cy="10" r="1.5" />
        </svg>
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div
            role="menu"
            className="border-line bg-surface-raised absolute right-0 z-20 mt-1 w-36 rounded-lg border py-1 text-left shadow-lg"
          >
            <button
              type="button"
              role="menuitem"
              onClick={() => setIsOpen(false)}
              className="text-fg hover:bg-surface-muted block w-full px-3 py-2 text-left text-sm"
            >
              Edit
            </button>
            <button
              type="button"
              role="menuitem"
              onClick={() => setIsOpen(false)}
              className="text-fg hover:bg-surface-muted block w-full px-3 py-2 text-left text-sm"
            >
              Delete
            </button>
          </div>
        </>
      )}
    </div>
  );
}
