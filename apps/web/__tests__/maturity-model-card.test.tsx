import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MaturityModelCard } from "@/components/maturity-model-card";

describe("MaturityModelCard", () => {
  it("renders", () => {
    const { container } = render(
      <MaturityModelCard service="api" level="L4" maturityPct={92} totalScore={23} maxScore={25}
        dimensions={[
          { dimension: "observability", score: 5, max: 5, description: "Logging" },
          { dimension: "security", score: 4, max: 5, description: "Auth" },
        ]} />
    );
    expect(container.textContent).toContain("Maturity: api");
    expect(container.textContent).toContain("L4");
    expect(container.textContent).toContain("23/25");
    expect(container.textContent).toContain("92%");
    expect(container.textContent).toContain("observability");
    expect(container.textContent).toContain("5/5");
  });
});
