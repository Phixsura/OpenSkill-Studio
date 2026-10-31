import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPlaygroundV9Panel } from "@/components/fleet-playground-v9-panel";
describe("FleetPlaygroundV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetPlaygroundV9Panel active={20} cpuHours={160} />);
    expect(container.textContent).toContain("Playground v9");
}); });
