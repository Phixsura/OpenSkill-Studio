import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SecretScanResults } from "@/components/secret-scan-results";

describe("SecretScanResults", () => {
  it("renders findings", () => {
    const { container } = render(
      <SecretScanResults totalFiles={10} totalFindings={1} clean={false} findings={[
        { type: "aws_key", severity: "critical", line: 5, file: "config.py", matchPreview: "AKIAIOSF••••" },
      ]} />
    );
    expect(container.textContent).toContain("Secret Scanner");
    expect(container.textContent).toContain("1 secrets found");
    expect(container.textContent).toContain("10 files scanned");
    expect(container.textContent).toContain("config.py:5");
    expect(container.textContent).toContain("critical");
  });
});
