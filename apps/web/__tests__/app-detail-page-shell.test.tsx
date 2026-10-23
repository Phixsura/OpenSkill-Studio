import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppDetailPageShell } from "@/components/app-detail-page-shell";

describe("AppDetailPageShell", () => {
  const tabs = [{ key: "overview", title: "Overview", default: true }, { key: "reviews", title: "Reviews (50)" }];
  it("renders", () => {
    const { container } = render(
      <AppDetailPageShell appName="SuperApp" developerName="DevCo" verified={true}
        tabs={tabs} installed={false} wishlisted={false} onInstall={vi.fn()} onWishlist={vi.fn()}>
        <p>Content</p>
      </AppDetailPageShell>
    );
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("DevCo");
    expect(container.textContent).toContain("Install");
    expect(container.textContent).toContain("Overview");
    expect(container.textContent).toContain("Content");
  });
  it("install", () => {
    const fn = vi.fn();
    const { container } = render(
      <AppDetailPageShell appName="X" developerName="D" verified={false}
        tabs={tabs} installed={false} wishlisted={false} onInstall={fn} onWishlist={vi.fn()}>
        <p>C</p>
      </AppDetailPageShell>
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Install")!);
    expect(fn).toHaveBeenCalled();
  });
});
