import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/lib/api", () => ({
  api: vi.fn(),
  ApiError: class extends Error {},
}));

import RegistryPage from "@/app/registry/page";
import { api } from "@/lib/api";

const mockApi = vi.mocked(api);

function createWrapper() {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("RegistryPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders page heading", () => {
    mockApi.mockReturnValue(new Promise(() => {}));
    render(<RegistryPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Skill Pack Registry")).toBeDefined();
  });

  it("shows loading state", () => {
    mockApi.mockReturnValue(new Promise(() => {}));
    render(<RegistryPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Loading...")).toBeDefined();
  });

  it("renders pack cards when loaded", async () => {
    mockApi.mockImplementation((path: string) => {
      if (typeof path === "string" && path.includes("/registry/categories")) {
        return Promise.resolve({ data: [] });
      }
      return Promise.resolve({
        data: [
          {
            id: "p1",
            name: "AI Basics",
            slug: "ai-basics",
            summary: "Learn AI fundamentals",
            difficulty: "beginner",
            install_count: 42,
            scenario_tags: ["prompt-eng"],
            tool_tags: [],
            provenance: { author_name: "Jane Doe" },
          },
        ],
        meta: { total: 1 },
      });
    });
    render(<RegistryPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("AI Basics")).toBeDefined();
    expect(screen.getByText("42 installs")).toBeDefined();
    expect(screen.getByText("beginner")).toBeDefined();
    expect(screen.getByText("Jane Doe")).toBeDefined();
    expect(screen.getByText("Learn AI fundamentals")).toBeDefined();
  });

  it("shows error message on failure", async () => {
    mockApi.mockImplementation((path: string) => {
      if (typeof path === "string" && path.includes("/registry/categories")) {
        return Promise.resolve({ data: [] });
      }
      return Promise.reject(new Error("Server error"));
    });
    render(<RegistryPage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText(/Failed to load packs/),
    ).toBeDefined();
  });

  it("shows empty state when no packs match", async () => {
    mockApi.mockImplementation((path: string) => {
      if (typeof path === "string" && path.includes("/registry/categories")) {
        return Promise.resolve({ data: [] });
      }
      return Promise.resolve({ data: [], meta: { total: 0 } });
    });
    render(<RegistryPage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText(/No packs found matching your criteria/),
    ).toBeDefined();
  });

  it("renders search input and filter controls", () => {
    mockApi.mockReturnValue(new Promise(() => {}));
    render(<RegistryPage />, { wrapper: createWrapper() });
    expect(screen.getByPlaceholderText("Search packs...")).toBeDefined();
    expect(screen.getByDisplayValue("All levels")).toBeDefined();
    expect(screen.getByDisplayValue("Newest")).toBeDefined();
  });

  it("updates search input value on change", () => {
    mockApi.mockReturnValue(new Promise(() => {}));
    render(<RegistryPage />, { wrapper: createWrapper() });
    const input = screen.getByPlaceholderText("Search packs...");
    fireEvent.change(input, { target: { value: "design" } });
    expect((input as HTMLInputElement).value).toBe("design");
  });

  it("renders scenario tags on pack cards", async () => {
    mockApi.mockImplementation((path: string) => {
      if (typeof path === "string" && path.includes("/registry/categories")) {
        return Promise.resolve({ data: [] });
      }
      return Promise.resolve({
        data: [
          {
            id: "p2",
            name: "Design Pack",
            slug: "design",
            summary: null,
            difficulty: null,
            install_count: 0,
            scenario_tags: ["ux-design", "prototyping"],
            tool_tags: [],
            provenance: {},
          },
        ],
        meta: { total: 1 },
      });
    });
    render(<RegistryPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("ux-design")).toBeDefined();
    expect(screen.getByText("prototyping")).toBeDefined();
  });
});
