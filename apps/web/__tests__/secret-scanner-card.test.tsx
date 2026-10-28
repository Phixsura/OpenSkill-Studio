import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SecretScannerCard from "../src/components/secret-scanner-card";

const findings = [
  {
    pattern_name: "aws_key",
    severity: "high" as const,
    location: "aws_access_key",
    snippet: "AKIA***LE",
  },
  {
    pattern_name: "private_key",
    severity: "critical" as const,
    location: "cert",
    snippet: "----***",
  },
];

describe("SecretScannerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <SecretScannerCard findings={findings} scannedFields={10} appName="My App" />,
    );
    expect(container.textContent).toContain("Secret Scanner");
    expect(container.textContent).toContain("My App");
  });

  it("shows findings count", () => {
    const { container } = render(
      <SecretScannerCard findings={findings} scannedFields={10} appName="App" />,
    );
    expect(container.textContent).toContain("2 secrets found");
  });

  it("shows clean badge when no findings", () => {
    const { container } = render(
      <SecretScannerCard findings={[]} scannedFields={10} appName="App" />,
    );
    expect(container.textContent).toContain("Clean");
    expect(container.textContent).toContain("No secrets detected");
  });

  it("renders severity badges", () => {
    const { container } = render(
      <SecretScannerCard findings={findings} scannedFields={10} appName="App" />,
    );
    expect(container.textContent).toContain("high");
    expect(container.textContent).toContain("critical");
  });

  it("shows pattern names and locations", () => {
    const { container } = render(
      <SecretScannerCard findings={findings} scannedFields={10} appName="App" />,
    );
    expect(container.textContent).toContain("aws key");
    expect(container.textContent).toContain("aws_access_key");
  });

  it("shows scanned field count", () => {
    const { container } = render(
      <SecretScannerCard findings={findings} scannedFields={10} appName="App" />,
    );
    expect(container.textContent).toContain("10 fields scanned");
  });
});
