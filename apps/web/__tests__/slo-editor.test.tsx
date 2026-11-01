import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SloEditor } from "@/components/slo-editor";

describe("SloEditor", () => {
  it("renders", () => {
    const { container } = render(
      <SloEditor avgTarget={99.45} onAdd={vi.fn()} onDelete={vi.fn()}
        slos={[
          { name: "Uptime", metric: "availability", targetPct: 99.9, errorBudgetPct: 0.1, windowDays: 30 },
          { name: "Latency", metric: "p99_ms", targetPct: 99.0, errorBudgetPct: 1.0, windowDays: 30 },
        ]} />
    );
    expect(container.textContent).toContain("SLO Editor");
    expect(container.textContent).toContain("2 SLOs");
    expect(container.textContent).toContain("99.45%");
    expect(container.textContent).toContain("Uptime");
    expect(container.textContent).toContain("99.9%");
    expect(container.textContent).toContain("budget: 0.1%");
  });
});
