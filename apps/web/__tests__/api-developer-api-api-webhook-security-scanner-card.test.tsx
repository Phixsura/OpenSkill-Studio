import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiWebhookSecurityScannerCard from "../src/components/api-developer-api-api-webhook-security-scanner-card";

const findings = [
  { finding_id: "sf-1", severity: "critical", category: "transport", message: "Uses HTTP", destination: "http://a.com" },
  { finding_id: "sf-2", severity: "medium", category: "auth", message: "Short secret", destination: "https://a.com" },
];

describe("APIDeveloperAPIApiWebhookSecurityScannerCard", () => {
  it("shows findings", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookSecurityScannerCard findings={findings} severityBreakdown={{ critical: 1, medium: 1 }} criticalCount={1} appName="App" />);
    expect(container.textContent).toContain("Security Scanner");
    expect(container.textContent).toContain("1 critical");
    expect(container.textContent).toContain("Uses HTTP");
    expect(container.textContent).toContain("Short secret");
  });
  it("shows clean", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookSecurityScannerCard findings={[]} severityBreakdown={{}} criticalCount={0} appName="App" />);
    expect(container.textContent).toContain("No security findings");
  });
});
