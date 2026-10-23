import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookFilterBuilder } from "@/components/webhook-filter-builder";

describe("WebhookFilterBuilder", () => {
  it("renders conditions", () => {
    const conditions = [{ field: "level", operator: "eq", value: "error" }];
    const { container } = render(<WebhookFilterBuilder conditions={conditions} onAdd={vi.fn()} onRemove={vi.fn()} />);
    expect(container.textContent).toContain("level eq error");
  });
  it("empty state", () => {
    const { container } = render(<WebhookFilterBuilder conditions={[]} onAdd={vi.fn()} onRemove={vi.fn()} />);
    expect(container.textContent).toContain("No filters");
  });
  it("remove", () => {
    const fn = vi.fn();
    const conditions = [{ field: "x", operator: "eq", value: "y" }];
    const { container } = render(<WebhookFilterBuilder conditions={conditions} onAdd={vi.fn()} onRemove={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith(0);
  });
});
