import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TrustScoreShield } from "@/components/trust-score-shield";

describe("TrustScoreShield", () => {
  const details = [
    { signal: "verified_developer", weight: 20, met: true },
    { signal: "security_scan_clean", weight: 20, met: true },
    { signal: "code_signed", weight: 15, met: false },
  ];
  it("renders", () => {
    const { container } = render(
      <TrustScoreShield score={75} trustLevel="medium" badge="" details={details}
        metCount={2} totalSignals={3} />
    );
    expect(container.textContent).toContain("🛡️");
    expect(container.textContent).toContain("75/100");
    expect(container.textContent).toContain("medium Trust");
    expect(container.textContent).toContain("2/3");
    expect(container.textContent).toContain("Verified Developer");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("⬜");
  });
});
