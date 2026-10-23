import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SecretScanResults } from "@/components/secret-scan-results";

describe("SecretScanResults", () => {
  it("shows findings", () => {
    const findings = [{ type: "AWS Access Key", severity: "critical", line: 5, file: "config.py", match_preview: "AKIA..." }];
    const { container } = render(<SecretScanResults findings={findings} filesScanned={10} clean={false} />);
    expect(container.textContent).toContain("AWS Access Key");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("config.py:5");
  });
  it("clean scan", () => {
    const { container } = render(<SecretScanResults findings={[]} filesScanned={20} clean={true} />);
    expect(container.textContent).toContain("No secrets detected");
  });
});
