import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSpringbootPanel } from "@/components/fleet-springboot-panel";
describe("FleetSpringbootPanel", () => { it("renders", () => {
    const { container } = render(<FleetSpringbootPanel services={20} up={20} beans={5000} heapPct={55} />);
    expect(container.textContent).toContain("Spring Boot");
    expect(container.textContent).toContain("5000 beans");
}); });
