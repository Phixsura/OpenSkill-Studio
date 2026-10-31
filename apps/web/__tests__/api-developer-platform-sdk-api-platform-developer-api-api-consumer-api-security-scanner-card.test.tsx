import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-security-scanner-card";

describe("SecurityScannerCard", () => {
  it("shows scan results", () => {
    const findings = [{ finding_id: "f1", category: "auth", severity: "critical", title: "No TLS", resolved: false }];
    const { container } = render(<Card consumerId="c1" score={75} findings={findings} criticalCount={1} appName="App" />);
    expect(container.textContent).toContain("Security Scanner");
    expect(container.textContent).toContain("75");
    expect(container.textContent).toContain("1 critical");
    expect(container.textContent).toContain("No TLS");
  });
  it("shows no findings", () => {
    const { container } = render(<Card consumerId="c1" score={100} findings={[]} criticalCount={0} appName="App" />);
    expect(container.textContent).toContain("No findings");
  });
});
