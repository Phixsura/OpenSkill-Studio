import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ComplianceScannerPanel } from "@/components/compliance-scanner-panel";

const mockReport = {
  score: 75, passed: false,
  checks: [
    { name: "manifest", level: "pass" as const, message: "manifest.json present", category: "quality" },
    { name: "readme", level: "fail" as const, message: "Missing README.md", category: "quality" },
    { name: "eval", level: "fail" as const, message: "Forbidden pattern eval(", category: "security" },
  ],
};

describe("ComplianceScannerPanel", () => {
  it("renders report", () => {
    const { container } = render(<ComplianceScannerPanel report={mockReport} />);
    expect(container.textContent).toContain("75/100");
    expect(container.textContent).toContain("Missing README.md");
  });

  it("calls onScan", () => {
    const onScan = vi.fn();
    const { getByText } = render(<ComplianceScannerPanel report={null} onScan={onScan} />);
    fireEvent.click(getByText("Scan"));
    expect(onScan).toHaveBeenCalled();
  });
});
