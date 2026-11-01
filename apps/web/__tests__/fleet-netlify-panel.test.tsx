import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNetlifyPanel } from "@/components/fleet-netlify-panel";
describe("FleetNetlifyPanel", () => { it("renders", () => {
    const { container } = render(<FleetNetlifyPanel sites={30} published={30} deploys={100} functions={50} />);
    expect(container.textContent).toContain("Netlify");
}); });
