import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetImgVulnPanel } from "@/components/fleet-img-vuln-panel";
describe("FleetImgVulnPanel", () => { it("renders", () => {
    const { container } = render(<FleetImgVulnPanel images={20} critical={2} high={5} clean={false} />);
    expect(container.textContent).toContain("Image Vulnerabilities");
    expect(container.textContent).toContain("2 critical");
}); });
