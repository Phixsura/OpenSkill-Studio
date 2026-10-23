import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployStatusBar } from "@/components/deploy-status-bar";

describe("DeployStatusBar", () => {
  const environments = [
    { environment: "development", icon: "🟢", version: "2.1.0", status: "success", deployedAt: "2026-01-04", deployer: "Bob", commit: "abc123" },
    { environment: "production", icon: "🔴", version: "2.0.0", status: "success", deployedAt: "2026-01-03", deployer: "Alice", commit: "def456" },
  ];
  it("renders deploy environments", () => {
    const { container } = render(<DeployStatusBar environments={environments} versionsInSync={false} />);
    expect(container.textContent).toContain("development");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Version mismatch");
  });
});
