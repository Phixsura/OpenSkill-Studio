import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EmptyStateCard } from "@/components/empty-state-card";

describe("EmptyStateCard", () => {
  it("renders with CTA", () => {
    const onAction = vi.fn();
    const { container, getByText } = render(
      <EmptyStateCard icon="📱" title="No apps yet"
        description="Create your first app" cta="Create App" onAction={onAction} />
    );
    expect(container.textContent).toContain("No apps yet");
    expect(container.textContent).toContain("Create your first app");
    fireEvent.click(getByText("Create App"));
    expect(onAction).toHaveBeenCalled();
  });

  it("renders without CTA", () => {
    const { container } = render(
      <EmptyStateCard icon="📋" title="No logs" description="Logs will appear soon" cta={null} onAction={null} />
    );
    expect(container.textContent).toContain("No logs");
    expect(container.querySelectorAll("button")).toHaveLength(0);
  });
});
