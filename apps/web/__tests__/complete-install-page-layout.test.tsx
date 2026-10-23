import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CompleteInstallPageLayout } from "@/components/complete-install-page-layout";

describe("CompleteInstallPageLayout", () => {
  it("renders page", () => {
    const steps = [{ key: "perms", title: "Permissions", required: true }, { key: "confirm", title: "Confirm", required: true }];
    const { container } = render(
      <CompleteInstallPageLayout appName="SuperApp" developerName="DevCo" developerVerified={true}
        canInstall={true} blockers={[]} steps={steps} ctaLabel="Install" onInstall={vi.fn()} />
    );
    expect(container.textContent).toContain("Install SuperApp");
    expect(container.textContent).toContain("DevCo");
    expect(container.textContent).toContain("Permissions");
    expect(container.textContent).toContain("Confirm");
  });
  it("blocked", () => {
    const { container } = render(
      <CompleteInstallPageLayout appName="App" developerName="D" developerVerified={false}
        canInstall={false} blockers={[{ message: "Conflict with AppX" }]} steps={[]}
        ctaLabel="Cannot Install" onInstall={vi.fn()} />
    );
    expect(container.textContent).toContain("Cannot Install");
    expect(container.textContent).toContain("Conflict with AppX");
  });
  it("install click", () => {
    const fn = vi.fn();
    const { container } = render(
      <CompleteInstallPageLayout appName="App" developerName="D" developerVerified={false}
        canInstall={true} blockers={[]} steps={[]} ctaLabel="Install" onInstall={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Install")!);
    expect(fn).toHaveBeenCalled();
  });
});
