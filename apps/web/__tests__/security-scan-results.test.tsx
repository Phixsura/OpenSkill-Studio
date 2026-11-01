import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SecurityScanResults } from "@/components/security-scan-results";

describe("SecurityScanResults", () => {
  it("shows passed state", () => {
    const { container } = render(<SecurityScanResults passed={true} riskLevel="none" findings={[]} />);
    expect(container.textContent).toContain("Passed");
  });

  it("shows failed state", () => {
    const { container } = render(<SecurityScanResults passed={false} riskLevel="high" findings={[{ severity: "high", type: "x", message: "Bad thing" }]} />);
    expect(container.textContent).toContain("Issues Found");
  });

  it("shows findings", () => {
    const findings = [{ severity: "medium", type: "perms", message: "Elevated permissions" }];
    const { container } = render(<SecurityScanResults passed={true} riskLevel="medium" findings={findings} />);
    expect(container.textContent).toContain("Elevated permissions");
  });

  it("shows risk level", () => {
    const { container } = render(<SecurityScanResults passed={true} riskLevel="low" findings={[]} />);
    expect(container.textContent).toContain("low");
  });

  it("shows no issues text", () => {
    const { container } = render(<SecurityScanResults passed={true} riskLevel="none" findings={[]} />);
    expect(container.textContent).toContain("No security issues");
  });
});
