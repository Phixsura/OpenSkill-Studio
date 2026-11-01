import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetResourceTaggingV9Panel } from "@/components/fleet-resource-tagging-v9-panel";
describe("FleetResourceTaggingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetResourceTaggingV9Panel total={1000} compliant={980} />);
    expect(container.textContent).toContain("Resource Tagging v9");
}); });
