import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppDetailSidebar } from "@/components/app-detail-sidebar";

describe("AppDetailSidebar", () => {
  it("renders stats", () => {
    const { container } = render(
      <AppDetailSidebar installCount={2000} activeCount={1800} avgRating={4.5} reviewCount={50}
        screenshots={["s1.png"]} onInstall={vi.fn()} />
    );
    expect(container.textContent).toContain("2,000");
    expect(container.textContent).toContain("4.5 ★");
    expect(container.textContent).toContain("Install App");
  });
  it("install button", () => {
    const fn = vi.fn();
    const { container } = render(
      <AppDetailSidebar installCount={0} activeCount={0} avgRating={0} reviewCount={0}
        screenshots={[]} onInstall={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
