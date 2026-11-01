import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAccessLogV9Panel } from "@/components/fleet-access-log-v9-panel";
describe("FleetAccessLogV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetAccessLogV9Panel sources={10} entries={1000000} />);
    expect(container.textContent).toContain("Access Log v9");
}); });
