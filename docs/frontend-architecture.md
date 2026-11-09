# Frontend Architecture

## 1. Overview

The **Status Pulse frontend** is a Single Page Application (SPA) built with React, written in TypeScript, and bundled using Vite.

### Technology stack

- **React 19** – Component-based UI development.
- **TypeScript** – Static typing and type safety.
- **Vite** – Development server and build tool.
- **TanStack Router** – File-based, type-safe routing.
- **TanStack Query** – Server-state management and data fetching.
- **Tailwind CSS v4** – Utility-first styling.
- **ESLint** – Code quality and linting.
- **Prettier** – Code formatting.

## 2. Folder Structure

The frontend follows a modular, component-based structure.

```text
frontend/
├── public/                     # Static files served as-is
├── src/
│   ├── api/                    # Backend communication
│   │   └── orders.ts
│   ├── components/             # Reusable UI components
│   │   └── ProgramsList.tsx
│   ├── routes/                 # File-based application routes
│   │   ├── __root.tsx
│   │   ├── index.tsx
│   │   └── orders.tsx
│   ├── assets/                 # Imported images, icons and fonts
│   ├── App.tsx
│   ├── App.css
│   ├── index.css               # Global styles and theme
│   ├── main.tsx                # Application entry point
│   └── routeTree.gen.ts        # Generated route tree
├── index.html
├── vite.config.ts
└── package.json
```

### Static assets

There are two locations for static assets:

- **`src/assets/`** – Images, icons, fonts and other assets imported directly into components. These are processed by Vite during the build.
- **`public/`** – Static files served directly without processing, retaining their original filenames.

Prefer `src/assets/` for application resources and `public/` for files requiring stable, direct URLs.

## 3. Routing

The application uses **TanStack Router with file-based routing**.

Routes are automatically generated from the files inside `src/routes/`. Each route file represents a URL, so there is no need to manually maintain a central route configuration.

The router plugin scans the directory and generates `src/routeTree.gen.ts`. This file should never be edited manually.

### Route conventions

| File         | URL       | Purpose                   |
| ------------ | --------- | ------------------------- |
| `__root.tsx` | Root      | Shared application layout |
| `index.tsx`  | `/`       | Homepage                  |
| `orders.tsx` | `/orders` | Orders page               |
| `about.tsx`  | `/about`  | About page                |

- `<Outlet />` renders the currently matched child route.
- `Link` provides client-side navigation without reloading the application.

## 4. Querying the Backend

The application uses **TanStack Query** to handle communication with the backend and manage server state.

### API layer

Backend communication is separated from UI components and organized inside `src/api/`. Each module contains the API functions responsible for a particular resource.

### Query management

Queries are defined declaratively using `queryOptions()`, combining a query key and query function.

Components consume these queries through `useQuery()`.

TanStack Query handles caching, loading states, error handling, background refetching and data synchronization.

Common query states include `isPending`, `isSuccess`, `isError` and `isFetching`.

Local UI state, such as modal visibility or selected tabs, should remain managed through React state rather than TanStack Query.

## 5. Styling and Theming

Tailwind follows a utility-first approach, allowing styling directly within component markup without requiring separate CSS files for every component.

### Global styles and theme

`src/index.css` is the central place for global styling and the application's visual identity.

If we want to complete or modify the project theme, we should do it here.

This includes:

- Primary and secondary colors.
- Background, surface and text colors.
- Typography and font families.
- Borders and border radii.

### Styling conventions

- Prefer Tailwind utility classes for component styling.
- Keep global design tokens in `index.css`.
- Avoid hardcoding colors and design values across components.
- Use custom CSS only when Tailwind utilities are insufficient.

If manual theme switching is introduced later, we can extend the existing theme with a class-based strategy.

## 6. Component Design

We should aim to reuse as many of the elements of website as much as possible. To do this, we use components. In order to better store their declarations, use **Atomic Design**

It divides components into five levels:

- **Atoms:** Basic building blocks, such as buttons, inputs, labels and icons.
- **Molecules:** Small combinations of atoms, such as search bars and form fields.
- **Organisms:** Larger UI sections, such as headers, sidebars, tables and program lists.
- **Templates:** Page-level layouts defining the structure and positioning of organisms.
- **Pages:** Complete application screens, typically represented by files inside `src/routes/`.
