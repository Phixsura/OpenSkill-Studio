import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DependencyScannerCard from "../src/components/dependency-scanner-card";

const cleanScan = {
  scanned_count: 42,
  critical_count: 0,
  high_count: 0,
  medium_count: 0,
  low_count: 0,
  findings: [],
};

const vulnScan = {
  scanned_count: 15,
  critical_count: 1,
  high_count: 1,
  medium_count: 1,
  low_count: 0,
  findings: [
    {
      package_name: "lodash",
      version: "4.17.21",
      vuln_id: "CVE-2026-001",
      severity: "critical" as const,
      title: "Prototype pollution",
      fixable: true,
      fix_version: "4.17.22",
    },
    {
      package_name: "express",
      version: "4.18.0",
      vuln_id: "CVE-2026-002",
      severity: "high" as const,
      title: "Path traversal",
      fixable: true,
      fix_version: "4.18.1",
    },
    {
      package_name: "axios",
      version: "1.5.0",
      vuln_id: "CVE-2026-003",
      severity: "medium" as const,
      title: "SSRF bypass",
      fixable: false,
      fix_version: null,
    },
  ],
};

describe("DependencyScannerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<DependencyScannerCard scan={cleanScan} appName="My App" />);
    expect(container.textContent).toContain("Dependency Scan");
    expect(container.textContent).toContain("My App");
  });

  it("shows scanned count", () => {
    const { container } = render(<DependencyScannerCard scan={cleanScan} appName="App" />);
    expect(container.textContent).toContain("42 packages scanned");
  });

  it("shows all-clear for clean scan", () => {
    const { container } = render(<DependencyScannerCard scan={cleanScan} appName="App" />);
    expect(container.textContent).toContain("No vulnerabilities found");
  });

  it("shows severity counts", () => {
    const { container } = render(<DependencyScannerCard scan={vulnScan} appName="App" />);
    expect(container.textContent).toContain("Critical");
    expect(container.textContent).toContain("High");
    expect(container.textContent).toContain("Medium");
  });

  it("renders finding details", () => {
    const { container } = render(<DependencyScannerCard scan={vulnScan} appName="App" />);
    expect(container.textContent).toContain("lodash@4.17.21");
    expect(container.textContent).toContain("CVE-2026-001");
    expect(container.textContent).toContain("Prototype pollution");
  });

  it("shows fix version when available", () => {
    const { container } = render(<DependencyScannerCard scan={vulnScan} appName="App" />);
    expect(container.textContent).toContain("Fix: 4.17.22");
  });

  it("shows no-fix label when unfixable", () => {
    const { container } = render(<DependencyScannerCard scan={vulnScan} appName="App" />);
    expect(container.textContent).toContain("No fix");
  });

  it("renders severity badge labels", () => {
    const { container } = render(<DependencyScannerCard scan={vulnScan} appName="App" />);
    expect(container.textContent).toContain("Critical");
    expect(container.textContent).toContain("High");
    expect(container.textContent).toContain("Medium");
  });
});
