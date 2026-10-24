import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetD1Panel } from "@/components/fleet-d1-panel";
describe("FleetD1Panel", () => { it("renders", () => {
    const { container } = render(<FleetD1Panel databases={10} active={10} rowsRead={50000000} rowsWritten={2000000} />);
    expect(container.textContent).toContain("D1");
}); });
