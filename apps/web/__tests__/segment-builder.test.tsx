import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SegmentBuilder } from "@/components/segment-builder";

describe("SegmentBuilder", () => {
  const rules = [
    { field: "plan", operator: "eq", value: "pro", label: "plan eq pro" },
    { field: "login_count", operator: "gt", value: 50, label: "login_count gt 50" },
  ];
  it("renders segment", () => {
    const { container } = render(
      <SegmentBuilder name="Power Users" rules={rules} matchPct={85} onRemoveRule={vi.fn()} />
    );
    expect(container.textContent).toContain("Power Users");
    expect(container.textContent).toContain("plan");
    expect(container.textContent).toContain("equals");
    expect(container.textContent).toContain("85%");
  });
  it("remove rule", () => {
    const fn = vi.fn();
    const { container } = render(
      <SegmentBuilder name="Seg" rules={rules} matchPct={100} onRemoveRule={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith(0);
  });
});
