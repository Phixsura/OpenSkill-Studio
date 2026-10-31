import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DashBuilder } from "@/components/dash-builder";

describe("DashBuilder", () => {
  it("renders builder", () => {
    const { container } = render(
      <DashBuilder title="System Overview" onAddPanel={vi.fn()} panels={[
        { id: 0, title: "CPU", type: "gauge", metric: "cpu_pct", width: 4 },
        { id: 1, title: "Requests", type: "chart", metric: "rps", width: 8 },
      ]} />
    );
    expect(container.textContent).toContain("System Overview");
    expect(container.textContent).toContain("2 panels");
    expect(container.textContent).toContain("CPU");
    expect(container.textContent).toContain("cpu_pct");
    expect(container.textContent).toContain("Requests");
    expect(container.textContent).toContain("+ Panel");
  });
});
