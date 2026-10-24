import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MiddlewareChainViewer } from "@/components/middleware-chain-viewer";

describe("MiddlewareChainViewer", () => {
  it("renders chain", () => {
    const { container } = render(
      <MiddlewareChainViewer enabled={2} total={3} chain={[
        { order: 0, name: "cors", type: "transform", enabled: true },
        { order: 1, name: "auth", type: "auth", enabled: true },
        { order: 2, name: "cache", type: "cache", enabled: false },
      ]} />
    );
    expect(container.textContent).toContain("Middleware Chain");
    expect(container.textContent).toContain("2/3 enabled");
    expect(container.textContent).toContain("cors");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("cache");
  });
});
