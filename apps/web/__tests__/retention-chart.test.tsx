import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RetentionChart } from "@/components/retention-chart";

describe("RetentionChart", () => {
  it("renders cohorts", () => {
    const cohorts = [
      { month: "2026-01", installed: 100, retained: 80, retention_rate: 80 },
      { month: "2026-02", installed: 50, retained: 40, retention_rate: 80 },
    ];
    const { container } = render(<RetentionChart cohorts={cohorts} />);
    expect(container.textContent).toContain("2026-01");
    expect(container.textContent).toContain("80%");
  });
  it("empty state", () => {
    const { container } = render(<RetentionChart cohorts={[]} />);
    expect(container.textContent).toContain("No retention data");
  });
});
