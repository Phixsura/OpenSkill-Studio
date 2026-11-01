import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GwCircuitDash } from "@/components/gw-circuit-dash";

describe("GwCircuitDash", () => {
  it("renders", () => {
    const { container } = render(
      <GwCircuitDash openCount={1} total={3}
        circuits={[
          { service: "auth-svc", state: "closed", failures: 0 },
          { service: "payment-svc", state: "open", failures: 5 },
          { service: "user-svc", state: "half-open", failures: 2 },
        ]} />
    );
    expect(container.textContent).toContain("Circuit Breakers");
    expect(container.textContent).toContain("1/3 open");
    expect(container.textContent).toContain("auth-svc");
    expect(container.textContent).toContain("closed");
    expect(container.textContent).toContain("payment-svc");
    expect(container.textContent).toContain("5 failures");
  });
});
