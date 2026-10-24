import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIdempotencyPanel } from "@/components/fleet-idempotency-panel";
describe("FleetIdempotencyPanel", () => { it("renders", () => {
    const { container } = render(<FleetIdempotencyPanel total={20} withIdemp={15} replayed={50} coveragePct={75} />);
    expect(container.textContent).toContain("Idempotency");
    expect(container.textContent).toContain("75%");
}); });
