import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { QuickInstallButton } from "@/components/quick-install-button";

describe("QuickInstallButton", () => {
  it("shows quick install", () => {
    const { container } = render(<QuickInstallButton quickInstall={true} stepsRequired={1} onInstall={vi.fn()} />);
    expect(container.textContent).toContain("Install Now");
  });
  it("shows steps", () => {
    const { container } = render(<QuickInstallButton quickInstall={false} stepsRequired={3} onInstall={vi.fn()} />);
    expect(container.textContent).toContain("3 steps");
  });
  it("shows loading", () => {
    const { container } = render(<QuickInstallButton quickInstall={true} stepsRequired={1} onInstall={vi.fn()} loading />);
    expect(container.textContent).toContain("Installing");
  });
});
