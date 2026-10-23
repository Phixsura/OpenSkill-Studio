import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SecretScannerReport } from "@/components/secret-scanner-report";

describe("SecretScannerReport", () => {
  it("clean scan", () => {
    const { container } = render(<SecretScannerReport results={[]} totalFindings={0} filesScanned={10} clean={true} />);
    expect(container.textContent).toContain("No secrets found");
  });
  it("findings", () => {
    const results = [{
      filename: "config.py", count: 1,
      findings: [{ type: "aws_key", line: 5, preview: "AKIA...", severity: "critical" }],
    }];
    const { container } = render(<SecretScannerReport results={results} totalFindings={1} filesScanned={5} clean={false} />);
    expect(container.textContent).toContain("Secrets Detected");
    expect(container.textContent).toContain("config.py");
    expect(container.textContent).toContain("aws_key");
    expect(container.textContent).toContain("critical");
  });
});
