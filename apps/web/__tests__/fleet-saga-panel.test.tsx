import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSagaPanel } from "@/components/fleet-saga-panel";
describe("FleetSagaPanel", () => { it("renders", () => {
    const { container } = render(<FleetSagaPanel total={10} completed={7} compensating={2} failed={1} healthy={false} />);
    expect(container.textContent).toContain("Sagas");
    expect(container.textContent).toContain("Saga issues");
}); });
