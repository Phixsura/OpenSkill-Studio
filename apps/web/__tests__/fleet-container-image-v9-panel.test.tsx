import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetContainerImageV9Panel } from "@/components/fleet-container-image-v9-panel";
describe("FleetContainerImageV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetContainerImageV9Panel images={500} scanned={500} />);
    expect(container.textContent).toContain("Container Image v9");
}); });
