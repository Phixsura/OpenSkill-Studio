import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OrgAppSettings } from "@/components/org-app-settings";

describe("OrgAppSettings", () => {
  it("shows settings", () => {
    const { container } = render(<OrgAppSettings autoUpgrade={true} allowThirdParty={true} maxApps={50} requireApproval={false} onSave={vi.fn()} />);
    expect(container.textContent).toContain("Auto-upgrade");
    expect(container.textContent).toContain("50");
  });
  it("shows on/off", () => {
    const { container } = render(<OrgAppSettings autoUpgrade={false} allowThirdParty={true} maxApps={10} requireApproval={true} onSave={vi.fn()} />);
    expect(container.textContent).toContain("Off");
    expect(container.textContent).toContain("Yes");
  });
});
