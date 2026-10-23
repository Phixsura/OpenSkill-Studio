import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SecretScanResults } from "@/components/secret-scan-results";

describe("SecretScanResults", () => {
  it("clean", () => {
    const { container } = render(<SecretScanResults findings={[]} clean={true} onRevoke={vi.fn()} />);
    expect(container.textContent).toContain("✅ Clean");
    expect(container.textContent).toContain("No secrets detected");
  });
  it("findings", () => {
    const findings = [{ type: "AWS Key", severity: "critical", preview: "AKIA1234...", filename: "config.py" }];
    const fn = vi.fn();
    const { container } = render(<SecretScanResults findings={findings} clean={false} onRevoke={fn} />);
    expect(container.textContent).toContain("🚨 1 secrets found");
    expect(container.textContent).toContain("AWS Key");
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Revoke")!);
    expect(fn).toHaveBeenCalled();
  });
});
