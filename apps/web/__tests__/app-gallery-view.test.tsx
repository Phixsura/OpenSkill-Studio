import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppGalleryView } from "@/components/app-gallery-view";

const APPS = [{ name: "App A", slug: "a", category: "connector", installCount: 100 }];

describe("AppGalleryView", () => {
  it("shows title", () => {
    const { container } = render(<AppGalleryView title="Connectors" apps={APPS} sortBy="installs" />);
    expect(container.textContent).toContain("Connectors");
  });
  it("shows apps", () => {
    const { container } = render(<AppGalleryView title="X" apps={APPS} sortBy="installs" />);
    expect(container.textContent).toContain("App A");
  });
  it("has sort select", () => {
    const { container } = render(<AppGalleryView title="X" apps={APPS} sortBy="installs" onSortChange={vi.fn()} />);
    expect(container.querySelector("select")).toBeTruthy();
  });
  it("empty state", () => {
    const { container } = render(<AppGalleryView title="X" apps={[]} sortBy="installs" />);
    expect(container.textContent).toContain("No apps");
  });
});
