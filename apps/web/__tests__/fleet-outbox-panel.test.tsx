import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOutboxPanel } from "@/components/fleet-outbox-panel";
describe("FleetOutboxPanel", () => { it("renders", () => {
    const { container } = render(<FleetOutboxPanel tables={5} pending={105} processed={15000} stuck={1} healthy={false} />);
    expect(container.textContent).toContain("Outbox");
    expect(container.textContent).toContain("1 stuck");
}); });
