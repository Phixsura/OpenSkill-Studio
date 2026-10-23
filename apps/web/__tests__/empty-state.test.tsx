import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EmptyState } from "@/components/empty-state";

describe("EmptyState", () => {
  it("renders with CTA", () => {
    const fn = vi.fn();
    const { container } = render(
      <EmptyState icon="📦" title="No apps" description="Create your first app" ctaLabel="Create" onAction={fn} />
    );
    expect(container.textContent).toContain("No apps");
    expect(container.textContent).toContain("Create your first app");
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
  it("renders without CTA", () => {
    const { container } = render(
      <EmptyState icon="🔔" title="All caught up!" description="No notifications" ctaLabel={null} onAction={null} />
    );
    expect(container.textContent).toContain("All caught up!");
    expect(container.querySelector("button")).toBeNull();
  });
});
