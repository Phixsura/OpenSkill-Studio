import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PrivacyOverviewCard } from "@/components/privacy-overview-card";

describe("PrivacyOverviewCard", () => {
  it("shows risk level", () => {
    const { container } = render(<PrivacyOverviewCard dataAccess={[]} networkHosts={[]} sandboxed={true} secretsCount={0} privacyUrl="https://x.com" riskLevel="low" />);
    expect(container.textContent).toContain("low risk");
    expect(container.textContent).toContain("Sandboxed");
  });
  it("shows no privacy policy warning", () => {
    const { container } = render(<PrivacyOverviewCard dataAccess={[]} networkHosts={[]} sandboxed={false} secretsCount={2} privacyUrl={null} riskLevel="high" />);
    expect(container.textContent).toContain("No privacy policy");
  });
});
