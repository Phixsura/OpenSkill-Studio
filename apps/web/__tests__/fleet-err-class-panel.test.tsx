import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetErrClassPanel } from "@/components/fleet-err-class-panel";
describe("FleetErrClassPanel", () => { it("renders", () => {
    const { container } = render(<FleetErrClassPanel total={100} clientErrors={60} serverErrors={40} />);
    expect(container.textContent).toContain("Error Classification");
    expect(container.textContent).toContain("60 client");
}); });
