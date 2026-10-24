import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ImpactAnalysisCard } from "@/components/impact-analysis-card";

describe("ImpactAnalysisCard", () => {
  it("renders rankings", () => {
    const { container } = render(
      <ImpactAnalysisCard totalServices={5} rankings={[
        { service: "database", blastRadius: 4, impactPct: 80 },
        { service: "auth", blastRadius: 2, impactPct: 40 },
        { service: "cache", blastRadius: 1, impactPct: 20 },
      ]} />
    );
    expect(container.textContent).toContain("Impact Analysis");
    expect(container.textContent).toContain("5 services");
    expect(container.textContent).toContain("database");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("auth");
  });
});
