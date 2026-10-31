import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceLevelV9Panel } from "@/components/fleet-service-level-v9-panel";
describe("FleetServiceLevelV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceLevelV9Panel total={50} breached={0} />);
    expect(container.textContent).toContain("Service Level v9");
}); });
