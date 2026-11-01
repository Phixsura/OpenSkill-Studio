import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APISecurityScanCard from "../src/components/api-security-scan-card";

const findings = [
  { finding_id: "f1", check_name: "TLS Check", severity: "high", resolved: false },
  { finding_id: "f2", check_name: "CORS Policy", severity: "medium", resolved: true },
];

describe("APISecurityScanCard", () => {
  it("renders score and unresolved", () => {
    const { container } = render(<APISecurityScanCard findings={findings} score={85} appName="App" />);
    expect(container.textContent).toContain("85");
    expect(container.textContent).toContain("1 unresolved");
  });

  it("shows findings with severity", () => {
    const { container } = render(<APISecurityScanCard findings={findings} score={85} appName="App" />);
    expect(container.textContent).toContain("TLS Check");
    expect(container.textContent).toContain("high");
  });

  it("shows clean state", () => {
    const { container } = render(<APISecurityScanCard findings={[]} score={100} appName="App" />);
    expect(container.textContent).toContain("No findings");
  });
});
