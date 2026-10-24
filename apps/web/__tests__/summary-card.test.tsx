import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SummaryCard } from "@/components/summary-card";

describe("SummaryCard", () => {
  const metrics = [
    { label: "Revenue", value: 12500, display: "$12,500.00" },
    { label: "Users", value: 5400, display: "5.4K" },
    { label: "Rating", value: 4.8, display: "4.8" },
  ];
  it("renders", () => {
    const { container } = render(
      <SummaryCard title="Monthly" icon="📈" metrics={metrics} status="ok" link={null} />
    );
    expect(container.textContent).toContain("Monthly");
    expect(container.textContent).toContain("📈");
    expect(container.textContent).toContain("$12,500.00");
    expect(container.textContent).toContain("5.4K");
    expect(container.textContent).toContain("4.8");
  });
});
