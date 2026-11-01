import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppInstallButton } from "@/components/app-install-button";

describe("AppInstallButton", () => {
  it("renders install", () => {
    const onInstall = vi.fn();
    const { container, getByText } = render(
      <AppInstallButton appName="Slack" installed={false} activeInstalls={5000}
        onInstall={onInstall} onUninstall={vi.fn()} />
    );
    expect(container.textContent).toContain("Install");
    expect(container.textContent).toContain("5,000");
    fireEvent.click(getByText("Install"));
    expect(onInstall).toHaveBeenCalled();
  });

  it("renders uninstall", () => {
    const onUninstall = vi.fn();
    const { getByText } = render(
      <AppInstallButton appName="Slack" installed={true} activeInstalls={5000}
        onInstall={vi.fn()} onUninstall={onUninstall} />
    );
    fireEvent.click(getByText("Uninstall"));
    expect(onUninstall).toHaveBeenCalled();
  });
});
