import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRespSizePanel } from "@/components/fleet-resp-size-panel";
describe("FleetRespSizePanel", () => { it("renders", () => {
    const { container } = render(<FleetRespSizePanel total={20} avgKb={500} largeResponses={3} optimized={false} />);
    expect(container.textContent).toContain("Response Size");
    expect(container.textContent).toContain("3 oversized");
}); });
