import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookFilterEditor } from "@/components/webhook-filter-editor";

describe("WebhookFilterEditor", () => {
  const filters = [
    { pattern: "app.*", mode: "prefix", description: "All app events" },
  ];
  it("renders filters", () => {
    const { container } = render(<WebhookFilterEditor filters={filters} onAdd={vi.fn()} onRemove={vi.fn()} />);
    expect(container.textContent).toContain("app.*");
    expect(container.textContent).toContain("prefix");
    expect(container.textContent).toContain("Remove");
  });
  it("remove click", () => {
    const fn = vi.fn();
    const { container } = render(<WebhookFilterEditor filters={filters} onAdd={vi.fn()} onRemove={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith(0);
  });
  it("empty state", () => {
    const { container } = render(<WebhookFilterEditor filters={[]} onAdd={vi.fn()} onRemove={vi.fn()} />);
    expect(container.textContent).toContain("No filters");
  });
});
