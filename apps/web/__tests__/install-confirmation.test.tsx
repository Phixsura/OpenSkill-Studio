import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InstallConfirmation } from "@/components/install-confirmation";

describe("InstallConfirmation", () => {
  it("shows app and org", () => {
    const { container } = render(<InstallConfirmation appName="App" developerName="Dev" verified={true} orgName="Org"
      permissions={["read:cohorts"]} highRisk={[]} onConfirm={vi.fn()} onCancel={vi.fn()} />);
    expect(container.textContent).toContain("Install App?");
    expect(container.textContent).toContain("Org");
  });
  it("shows high risk", () => {
    const { container } = render(<InstallConfirmation appName="X" developerName="D" verified={false} orgName="O"
      permissions={["write:settings"]} highRisk={["write:settings"]} onConfirm={vi.fn()} onCancel={vi.fn()} />);
    expect(container.textContent).toContain("⚠️");
  });
});
