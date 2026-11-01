import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReferralDashboard } from "@/components/referral-dashboard";

describe("ReferralDashboard", () => {
  it("renders", () => {
    const { container } = render(
      <ReferralDashboard code="ref_abc123" signups={5} totalRewards="$25.00" onCopyCode={vi.fn()} />
    );
    expect(container.textContent).toContain("ref_abc123");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("$25.00");
  });
  it("copy button", () => {
    const fn = vi.fn();
    const { container } = render(<ReferralDashboard code="x" signups={0} totalRewards="$0" onCopyCode={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Copy")!);
    expect(fn).toHaveBeenCalled();
  });
});
