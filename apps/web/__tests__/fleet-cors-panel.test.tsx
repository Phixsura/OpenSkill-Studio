import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCorsPanel } from "@/components/fleet-cors-panel";
describe("FleetCorsPanel", () => { it("renders", () => {
    const { container } = render(<FleetCorsPanel total={10} wildcardOrigin={2} secure={false} />);
    expect(container.textContent).toContain("CORS Policy");
    expect(container.textContent).toContain("2 with wildcard");
}); });
