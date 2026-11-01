import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MiddlewareChainViewer } from "@/components/middleware-chain-viewer";

describe("MiddlewareChainViewer", () => {
  it("renders", () => {
    const { container } = render(
      <MiddlewareChainViewer completed={true}
        steps={[
          { name: "logging", status: "applied" },
          { name: "auth", status: "applied" },
          { name: "rate_limit", status: "applied" },
        ]} />
    );
    expect(container.textContent).toContain("Middleware Chain");
    expect(container.textContent).toContain("Complete");
    expect(container.textContent).toContain("logging");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("rate_limit");
  });
});
