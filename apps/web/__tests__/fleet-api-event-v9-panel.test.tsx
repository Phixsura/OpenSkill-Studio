import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiEventV9Panel } from "@/components/fleet-api-event-v9-panel";
describe("FleetApiEventV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiEventV9Panel types={50} published={100000} />);
    expect(container.textContent).toContain("API Event v9");
}); });
