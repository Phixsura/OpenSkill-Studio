import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InstallFlowWizard } from "@/components/install-flow-wizard";

describe("InstallFlowWizard", () => {
  it("renders wizard", () => {
    const onAdvance = vi.fn();
    const { container, getByText } = render(
      <InstallFlowWizard appName="Slack Bot" appIcon="💬" developer="Acme"
        currentStep={0} hasDangerous={true}
        permissions={[{ name: "deploy", description: "Deploy apps", risk: "high" }]}
        steps={[
          { id: "review", title: "Review Permissions", status: "current" },
          { id: "activate", title: "Activate", status: "pending" },
        ]} onAdvance={onAdvance} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Install Slack Bot");
    expect(container.textContent).toContain("Acme");
    expect(container.textContent).toContain("deploy");
    expect(container.textContent).toContain("high-risk");
    fireEvent.click(getByText("Continue"));
    expect(onAdvance).toHaveBeenCalled();
  });
});
