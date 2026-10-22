import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InstallFlowPage } from "@/components/install-flow-page";

describe("InstallFlowPage", () => {
  it("shows app and org", () => {
    const { container } = render(<InstallFlowPage appName="App" orgName="Org" flowType="quick" permissionCount={3} hasConfig={false} />);
    expect(container.textContent).toContain("Install App");
    expect(container.textContent).toContain("Org");
  });
  it("shows config required", () => {
    const { container } = render(<InstallFlowPage appName="X" orgName="O" flowType="standard" permissionCount={0} hasConfig={true} />);
    expect(container.textContent).toContain("Configuration required");
  });
});
