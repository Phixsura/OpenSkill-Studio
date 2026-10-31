import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetImageBuilderV9Panel } from "@/components/fleet-image-builder-v9-panel";
describe("FleetImageBuilderV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetImageBuilderV9Panel builds={100} avgTime={52} />);
    expect(container.textContent).toContain("Image Builder v9");
}); });
