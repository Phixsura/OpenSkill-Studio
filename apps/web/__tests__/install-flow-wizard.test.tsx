import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InstallFlowWizard } from "@/components/install-flow-wizard";

describe("InstallFlowWizard", () => {
  it("shows consent step", () => {
    const { container } = render(<InstallFlowWizard currentStep="consent" extensionName="My Ext" permissions={["read:data", "write:data"]} />);
    expect(container.textContent).toContain("Install My Ext");
    expect(container.textContent).toContain("read:data");
    expect(container.textContent).toContain("Grant & Continue");
  });
  it("shows complete step", () => {
    const { container } = render(<InstallFlowWizard currentStep="complete" extensionName="My Ext" permissions={[]} />);
    expect(container.textContent).toContain("Installed Successfully");
  });
});
