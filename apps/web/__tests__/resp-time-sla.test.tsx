import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RespTimeSlaPanel } from "@/components/resp-time-sla";

describe("RespTimeSlaPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RespTimeSlaPanel slaPct={50} met={1} breached={1} results={[
        { endpoint: "/users", p99Ms: 200, targetMs: 500, withinSla: true, marginMs: 300 },
        { endpoint: "/orders", p99Ms: 600, targetMs: 500, withinSla: false, marginMs: -100 },
      ]} />
    );
    expect(container.textContent).toContain("Response Time SLA");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("1 met");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("200ms / 500ms");
    expect(container.textContent).toContain("/orders");
  });
});
