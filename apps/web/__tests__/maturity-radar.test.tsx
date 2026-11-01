import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MaturityRadar } from "@/components/maturity-radar";

describe("MaturityRadar", () => {
  it("renders maturity", () => {
    const { container } = render(
      <MaturityRadar overallLevel={4} overallName="Measured" averageScore={4.0}
        strengths={["CI/CD", "DX"]} improvements={[]}
        dimensions={[
          { dimension: "ci_cd", name: "CI/CD", level: 5, levelName: "Optimized", maxLevel: 5 },
          { dimension: "security", name: "Security", level: 4, levelName: "Measured", maxLevel: 5 },
        ]} />
    );
    expect(container.textContent).toContain("Platform Maturity");
    expect(container.textContent).toContain("4");
    expect(container.textContent).toContain("Measured");
    expect(container.textContent).toContain("CI/CD");
    expect(container.textContent).toContain("L5 Optimized");
    expect(container.textContent).toContain("Strengths: CI/CD, DX");
  });
});
