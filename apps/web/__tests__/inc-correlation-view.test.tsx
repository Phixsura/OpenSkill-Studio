import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncCorrelationView } from "@/components/inc-correlation-view";

describe("IncCorrelationView", () => {
  it("renders", () => {
    const { container } = render(
      <IncCorrelationView totalIncidents={5} hasCorrelations={true}
        correlations={[
          { tag: "database", incidents: ["inc1", "inc2", "inc3"], count: 3 },
          { tag: "timeout", incidents: ["inc1", "inc4"], count: 2 },
        ]} />
    );
    expect(container.textContent).toContain("Incident Correlation");
    expect(container.textContent).toContain("5 incidents");
    expect(container.textContent).toContain("2 groups");
    expect(container.textContent).toContain("database");
    expect(container.textContent).toContain("3 incidents");
    expect(container.textContent).toContain("inc1, inc2, inc3");
  });
});
