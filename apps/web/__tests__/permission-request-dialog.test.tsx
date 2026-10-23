import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PermissionRequestDialog } from "@/components/permission-request-dialog";

describe("PermissionRequestDialog", () => {
  it("renders dialog", () => {
    const onApprove = vi.fn();
    const { container, getByText } = render(
      <PermissionRequestDialog appName="Slack Bot" maxRisk="high" onApprove={onApprove} onDeny={vi.fn()}
        details={[
          { permission: "read:profile", label: "Read Profile", risk: "low", granted: false },
          { permission: "deploy", label: "Deploy", risk: "high", granted: false },
        ]} />
    );
    expect(container.textContent).toContain("Slack Bot requests access");
    expect(container.textContent).toContain("Read Profile");
    expect(container.textContent).toContain("Deploy");
    expect(container.textContent).toContain("high");
    fireEvent.click(getByText("Approve"));
    expect(onApprove).toHaveBeenCalled();
  });
});
