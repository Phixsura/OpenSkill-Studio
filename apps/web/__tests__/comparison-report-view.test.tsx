import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ComparisonReportView } from "@/components/comparison-report-view";

const METRICS = { install_count: { a: 200, b: 100, winner: "a" }, health_score: { a: 95, b: 98, winner: "b" } };

describe("ComparisonReportView", () => {
  it("shows app names", () => {
    const { container } = render(<ComparisonReportView appA="App A" appB="App B" metrics={METRICS} recommendation="A leads" sharedPermissions={["read:cohorts"]} />);
    expect(container.textContent).toContain("App A vs App B");
  });
  it("shows metrics", () => {
    const { container } = render(<ComparisonReportView appA="A" appB="B" metrics={METRICS} recommendation="X" sharedPermissions={[]} />);
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("98");
  });
  it("shows recommendation", () => {
    const { container } = render(<ComparisonReportView appA="A" appB="B" metrics={{}} recommendation="Both comparable" sharedPermissions={[]} />);
    expect(container.textContent).toContain("Both comparable");
  });
});
