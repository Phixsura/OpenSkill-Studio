import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CtxPropagatePanel } from "@/components/ctx-propagate-panel";
describe("CtxPropagatePanel", () => {
  it("renders", () => {
    const { container } = render(
      <CtxPropagatePanel activeCount={1}
        contexts={[{ requestId: "req-abc", traceId: "trace-xyz", userId: "u1", baggage: { flag: "on" } }]} />
    );
    expect(container.textContent).toContain("Context Propagation");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("req-abc");
    expect(container.textContent).toContain("trace-xyz");
    expect(container.textContent).toContain("flag=on");
  });
});
