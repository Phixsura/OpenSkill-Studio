import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookFilterBuilder } from "@/components/webhook-filter-builder";

describe("WebhookFilterBuilder", () => {
  const conditions = [
    { field: "data.amount", operator: "gt", value: 100 },
    { field: "type", operator: "eq", value: "payment" },
  ];
  it("renders", () => {
    const { container } = render(
      <WebhookFilterBuilder name="High Value" conditions={conditions}
        onAdd={vi.fn()} onRemove={vi.fn()} onSave={vi.fn()} />
    );
    expect(container.textContent).toContain("Webhook Filter: High Value");
    expect(container.textContent).toContain("data.amount");
    expect(container.textContent).toContain(">");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("Save Filter");
  });
  it("remove", () => {
    const fn = vi.fn();
    const { container } = render(
      <WebhookFilterBuilder name="X" conditions={conditions}
        onAdd={vi.fn()} onRemove={fn} onSave={vi.fn()} />
    );
    const removeBtns = Array.from(container.querySelectorAll("button")).filter(b => b.textContent === "×");
    fireEvent.click(removeBtns[0]);
    expect(fn).toHaveBeenCalledWith(0);
  });
});
