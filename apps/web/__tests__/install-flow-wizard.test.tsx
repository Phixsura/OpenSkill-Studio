import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InstallFlowWizard } from "@/components/install-flow-wizard";

describe("InstallFlowWizard", () => {
  const steps = [
    { id: "permissions", label: "Permissions", icon: "🔐" },
    { id: "confirm", label: "Confirm", icon: "✅" },
  ];
  it("renders wizard", () => {
    const { container } = render(
      <InstallFlowWizard appName="SuperApp" steps={steps} currentStep={0}
        permissions={["read:data"]} onNext={vi.fn()} onBack={vi.fn()} onInstall={vi.fn()} />
    );
    expect(container.textContent).toContain("Install SuperApp");
    expect(container.textContent).toContain("Permissions");
    expect(container.textContent).toContain("read:data");
    expect(container.textContent).toContain("Next");
  });
});
