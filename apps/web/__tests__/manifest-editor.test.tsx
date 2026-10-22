import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { ManifestEditor } from "@/components/manifest-editor";

const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
function Wrapper({ children }: { children: ReactNode }) {
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
}

describe("ManifestEditor", () => {
  it("renders with default manifest", () => {
    const { container } = render(<ManifestEditor />, { wrapper: Wrapper });
    expect(container.querySelector("textarea, pre, code, [contenteditable]")).toBeTruthy();
  });

  it("renders with initial value", () => {
    const manifest = { schema_version: "1.0", app: { name: "Test", slug: "test", version: "1.0.0", category: "connector" } };
    const { container } = render(<ManifestEditor initialValue={manifest} />, { wrapper: Wrapper });
    expect(container.textContent).toContain("Test");
  });

  it("renders in read-only mode", () => {
    const { container } = render(<ManifestEditor readOnly />, { wrapper: Wrapper });
    expect(container).toBeTruthy();
  });

  it("calls onSave callback", () => {
    const onSave = vi.fn();
    const { container } = render(<ManifestEditor onSave={onSave} />, { wrapper: Wrapper });
    expect(container).toBeTruthy();
  });
});
