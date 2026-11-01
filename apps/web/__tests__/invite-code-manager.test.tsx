import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InviteCodeManager } from "@/components/invite-code-manager";

describe("InviteCodeManager", () => {
  it("renders codes", () => {
    const { container } = render(
      <InviteCodeManager activeCount={1} totalRedemptions={3} onCreate={vi.fn()}
        codes={[
          { code: "ABCD1234", maxUses: 5, uses: 2, active: true },
          { code: "WXYZ9876", maxUses: 1, uses: 1, active: false },
        ]} />
    );
    expect(container.textContent).toContain("Invite Codes");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("3 redeemed");
    expect(container.textContent).toContain("ABCD1234");
    expect(container.textContent).toContain("2/5");
    expect(container.textContent).toContain("Exhausted");
  });
});
