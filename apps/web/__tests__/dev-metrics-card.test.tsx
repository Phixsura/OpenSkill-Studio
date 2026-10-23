import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DevMetricsCard } from "@/components/dev-metrics-card";

describe("DevMetricsCard", () => {
  it("renders metrics", () => {
    const { container } = render(
      <DevMetricsCard appCount={5} installsDisplay="80,000" ratingDisplay="4.5 ⭐"
        apiDisplay="1,500,000" supportGrade="A" qualityScore={85} avgResponseHours={3.5} />
    );
    expect(container.textContent).toContain("Developer Metrics");
    expect(container.textContent).toContain("80,000");
    expect(container.textContent).toContain("4.5 ⭐");
    expect(container.textContent).toContain("1,500,000");
    expect(container.textContent).toContain("85/100");
    expect(container.textContent).toContain("A");
  });
});
