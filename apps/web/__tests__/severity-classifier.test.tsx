import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SeverityClassifier } from "@/components/severity-classifier";

describe("SeverityClassifier", () => {
  it("renders", () => {
    const { container } = render(
      <SeverityClassifier severity="critical" matchedSymptoms={["data_loss"]}
        responseTimeMin={15} escalate={true} totalIncidents={10}
        distribution={{ critical: 2, high: 3, medium: 3, low: 2 }} />
    );
    expect(container.textContent).toContain("Severity Classifier");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("Escalate");
    expect(container.textContent).toContain("15min");
    expect(container.textContent).toContain("data_loss");
  });
});
