import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFlaggerPanel } from "@/components/fleet-flagger-panel";
describe("FleetFlaggerPanel", () => { it("renders", () => {
    const { container } = render(<FleetFlaggerPanel total={10} progressing={3} succeeded={6} failed={1} healthy={false} />);
    expect(container.textContent).toContain("Flagger");
    expect(container.textContent).toContain("1 failed");
}); });
