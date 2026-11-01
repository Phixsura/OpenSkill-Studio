import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AdminConsolePanel } from "@/components/admin-console-panel";

const logs = [
  { actionId: "a1", adminId: "admin-1", action: "suspend_extension", targetType: "extension", targetId: "ext-1", reason: "ToS violation", timestamp: Date.now() },
  { actionId: "a2", adminId: "admin-1", action: "feature_extension", targetType: "extension", targetId: "ext-2", reason: "", timestamp: Date.now() },
];

describe("AdminConsolePanel", () => {
  it("renders admin logs", () => {
    const { container } = render(<AdminConsolePanel logs={logs} />);
    expect(container.textContent).toContain("admin-1");
    expect(container.textContent).toContain("suspend extension");
    expect(container.textContent).toContain("ToS violation");
    expect(container.textContent).toContain("ext-2");
  });
});
