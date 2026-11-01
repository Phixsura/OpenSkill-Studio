import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PageHeader } from "@/components/page-header";

describe("PageHeader", () => {
  it("renders full header", () => {
    const { container } = render(
      <PageHeader title="Settings" subtitle="Manage your app"
        breadcrumbs={[{ label: "Home", path: "/" }, { label: "Settings", path: "/settings" }]}
        actions={[{ label: "Save", type: "primary" }]}
        onBreadcrumbClick={vi.fn()} onAction={vi.fn()} />
    );
    expect(container.textContent).toContain("Settings");
    expect(container.textContent).toContain("Manage your app");
    expect(container.textContent).toContain("Home");
    expect(container.textContent).toContain("Save");
  });
  it("action click", () => {
    const fn = vi.fn();
    const { container } = render(
      <PageHeader title="X" breadcrumbs={[]} actions={[{ label: "Save", type: "primary" }]}
        onBreadcrumbClick={vi.fn()} onAction={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Save")!);
    expect(fn).toHaveBeenCalledWith("Save");
  });
});
