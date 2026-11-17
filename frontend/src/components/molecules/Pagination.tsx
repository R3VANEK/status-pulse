type PaginationProps = {
  currentPage: number;
  totalPages: number;
};

const BASE_CLASS =
  "flex size-8 items-center justify-center rounded-control text-[13px]";

export function Pagination({ currentPage, totalPages }: PaginationProps) {
  const pages = Array.from({ length: totalPages }, (_, index) => index + 1);

  return (
    <nav aria-label="Paginacja" className="flex items-center gap-1">
      <button
        type="button"
        aria-label="Poprzednia strona"
        disabled={currentPage === 1}
        className={`${BASE_CLASS} text-fg-muted hover:bg-surface-muted disabled:opacity-40`}
      >
        ‹
      </button>
      {pages.map((page) => (
        <button
          key={page}
          type="button"
          aria-current={page === currentPage ? "page" : undefined}
          className={`${BASE_CLASS} ${
            page === currentPage
              ? "text-fg font-semibold"
              : "text-fg-muted hover:text-fg"
          }`}
        >
          {page}
        </button>
      ))}
      <button
        type="button"
        aria-label="Następna strona"
        disabled={currentPage === totalPages}
        className={`${BASE_CLASS} text-fg-muted hover:bg-surface-muted disabled:opacity-40`}
      >
        ›
      </button>
    </nav>
  );
}
