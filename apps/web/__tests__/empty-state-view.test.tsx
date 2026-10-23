import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EmptyStateView } from "@/components/empty-state-view";

describe("EmptyStateView", () => {
  it("renders", () => {
    const { container } = render(
      <EmptyStateView title="No Apps Yet" icon="📦" description="Create your first app."
        ctaLabel="Create App" ctaUrl="/apps/new" onCta={vi.fn()} />
    );
    expect(container.textContent).toContain("📦");
    expect(container.textContent).toContain("No Apps Yet");
    expect(container.textContent).toContain("Create your first app.");
    expect(container.textContent).toContain("Create App");
  });
  it("cta click", () => {
    const fn = vi.fn();
    const { container } = render(
      <EmptyStateView title="X" icon="📦" description="Y" ctaLabel="Go" ctaUrl="" onCta={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
