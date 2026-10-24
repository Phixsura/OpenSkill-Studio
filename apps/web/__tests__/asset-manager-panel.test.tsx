import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AssetManagerPanel } from "@/components/asset-manager-panel";

describe("AssetManagerPanel", () => {
  it("renders assets", () => {
    const assets = [{ path: "app.js", size: 5120, content_type: "application/javascript", hash: "abc" }];
    const { container } = render(<AssetManagerPanel assets={assets} totalSize={5120} version="2.0" onInvalidate={vi.fn()} />);
    expect(container.textContent).toContain("app.js");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("5.0KB");
  });
});
