import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ContentValidatorPanel } from "@/components/content-validator-panel";

const passedReport = { passed: true, score: 100, violations: [], warnings: [] };
const failedReport = {
  passed: false, score: 40,
  violations: [
    { violationType: "prohibited_content", severity: "high" as const, field: "description",
      message: "Prohibited content detected", suggestion: "Remove flagged content" },
    { violationType: "trademark", severity: "medium" as const, field: "name",
      message: "Potential trademark issue" },
  ],
  warnings: ["description: Consider a more detailed description"],
};

describe("ContentValidatorPanel", () => {
  it("renders passed report", () => {
    const { container } = render(<ContentValidatorPanel report={passedReport} />);
    expect(container.textContent).toContain("Passed");
    expect(container.textContent).toContain("100/100");
  });

  it("renders violations", () => {
    const { container } = render(<ContentValidatorPanel report={failedReport} />);
    expect(container.textContent).toContain("Failed");
    expect(container.textContent).toContain("Prohibited content");
    expect(container.textContent).toContain("Remove flagged content");
  });

  it("shows warnings", () => {
    const { container } = render(<ContentValidatorPanel report={failedReport} />);
    expect(container.textContent).toContain("more detailed description");
  });

  it("calls onRescan", () => {
    const onRescan = vi.fn();
    const { getByText } = render(<ContentValidatorPanel report={passedReport} onRescan={onRescan} />);
    fireEvent.click(getByText("Rescan"));
    expect(onRescan).toHaveBeenCalled();
  });
});
