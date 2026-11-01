import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ComplianceScoreCard } from "@/components/compliance-score-card";

describe("ComplianceScoreCard", () => {
  it("shows score", () => {
    const results = [
      { id: "a", label: "Valid manifest", category: "structure", passed: true },
      { id: "b", label: "HTTPS only", category: "security", passed: false },
    ];
    const { container } = render(<ComplianceScoreCard score={50} results={results} compliant={false} />);
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Issues found");
    expect(container.textContent).toContain("HTTPS only");
  });
  it("shows compliant", () => {
    const { container } = render(<ComplianceScoreCard score={100} results={[]} compliant={true} />);
    expect(container.textContent).toContain("Compliant");
  });
});
