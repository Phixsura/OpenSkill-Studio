import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InstallWizardV2 } from "@/components/install-wizard-v2";

describe("InstallWizardV2", () => {
  const steps = [{ key: "perms", title: "Permissions" }, { key: "config", title: "Configure" }, { key: "confirm", title: "Confirm" }];
  it("renders first step", () => {
    const { container } = render(<InstallWizardV2 appName="MyApp" steps={steps} onInstall={vi.fn()} onCancel={vi.fn()} />);
    expect(container.textContent).toContain("Install MyApp");
    expect(container.textContent).toContain("Step 1 of 3");
    expect(container.textContent).toContain("Permissions");
  });
  it("advances", () => {
    const { container } = render(<InstallWizardV2 appName="App" steps={steps} onInstall={vi.fn()} onCancel={vi.fn()} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Next")!);
    expect(container.textContent).toContain("Configure");
  });
});
