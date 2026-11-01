import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SreDashboard } from "@/components/sre-dashboard";

describe("SreDashboard", () => {
  it("renders SRE metrics", () => {
    const { container } = render(
      <SreDashboard burnRate={1.0} consumedPct={50} expectedPct={50}
        alert="none" healthy={true} toilPct={37.5} toilTarget={50}
        withinBudget={true} />
    );
    expect(container.textContent).toContain("SRE Dashboard");
    expect(container.textContent).toContain("burn rate: 1x");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Error Budget");
    expect(container.textContent).toContain("Toil Budget");
    expect(container.textContent).toContain("37.5%");
  });
});
