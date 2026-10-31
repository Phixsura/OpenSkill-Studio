import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SecretScannerCard from "../src/components/secret-scanner-card";

const findings = [
  {
    finding_id: "f1",
    pattern_name: "aws_key",
    matched_text: "AKIAIOSI...",
    location: "config.yaml",
    severity: "high",
    resolved: false,
  },
  {
    finding_id: "f2",
    pattern_name: "private_key",
    matched_text: "-----BEG...",
    location: "id_rsa",
    severity: "critical",
    resolved: true,
  },
];

describe("SecretScannerCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<SecretScannerCard findings={findings} appName="App" />);
    expect(container.textContent).toContain("Secret Scanner");
    expect(container.textContent).toContain("2 findings");
    expect(container.textContent).toContain("1 unresolved");
  });

  it("shows severity badges", () => {
    const { container } = render(<SecretScannerCard findings={findings} appName="App" />);
    expect(container.textContent).toContain("high");
    expect(container.textContent).toContain("critical");
  });

  it("shows pattern names and locations", () => {
    const { container } = render(<SecretScannerCard findings={findings} appName="App" />);
    expect(container.textContent).toContain("aws_key");
    expect(container.textContent).toContain("config.yaml");
  });

  it("shows resolved indicator", () => {
    const { container } = render(<SecretScannerCard findings={findings} appName="App" />);
    expect(container.textContent).toContain("resolved");
  });

  it("shows clean state", () => {
    const { container } = render(<SecretScannerCard findings={[]} appName="App" />);
    expect(container.textContent).toContain("No secrets detected");
  });
});
