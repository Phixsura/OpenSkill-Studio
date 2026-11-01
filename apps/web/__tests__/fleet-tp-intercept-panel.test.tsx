import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTpInterceptPanel } from "@/components/fleet-tp-intercept-panel";
describe("FleetTpInterceptPanel", () => { it("renders", () => {
    const { container } = render(<FleetTpInterceptPanel total={10} active={5} personal={3} globalInt={2} />);
    expect(container.textContent).toContain("Intercepts");
    expect(container.textContent).toContain("3 personal");
}); });
