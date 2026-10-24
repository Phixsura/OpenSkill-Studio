import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIdpPanel } from "@/components/fleet-idp-panel";
describe("FleetIdpPanel", () => { it("renders", () => {
    const { container } = render(<FleetIdpPanel templates={10} scaffolds={50} docsPages={200} adoptionScore={40} />);
    expect(container.textContent).toContain("Developer Portal");
    expect(container.textContent).toContain("10 templates");
}); });
