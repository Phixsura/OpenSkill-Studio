import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCircuitBreakerV9Panel } from "@/components/fleet-circuit-breaker-v9-panel";
describe("FleetCircuitBreakerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCircuitBreakerV9Panel total={100} open={0} />);
    expect(container.textContent).toContain("Circuit Breaker v9");
}); });
