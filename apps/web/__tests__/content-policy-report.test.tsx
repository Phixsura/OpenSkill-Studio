import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ContentPolicyReport } from "@/components/content-policy-report";

describe("ContentPolicyReport", () => {
  it("renders passed", () => {
    const { container } = render(<ContentPolicyReport passed={true} violations={[]} onFix={vi.fn()} />);
    expect(container.textContent).toContain("Passed");
    expect(container.textContent).toContain("No violations");
  });
  it("renders violations", () => {
    const violations = [{ rule: "impersonation", severity: "critical", detail: "Bad name" }];
    const fn = vi.fn();
    const { container } = render(<ContentPolicyReport passed={false} violations={violations} onFix={fn} />);
    expect(container.textContent).toContain("Failed");
    expect(container.textContent).toContain("Bad name");
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Fix")!);
    expect(fn).toHaveBeenCalledWith("impersonation");
  });
});
