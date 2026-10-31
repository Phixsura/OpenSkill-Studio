import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCeleryPanel } from "@/components/fleet-celery-panel";
describe("FleetCeleryPanel", () => { it("renders", () => {
    const { container } = render(<FleetCeleryPanel workers={20} online={20} activeTasks={100} reserved={50} />);
    expect(container.textContent).toContain("Celery");
    expect(container.textContent).toContain("100 active");
}); });
