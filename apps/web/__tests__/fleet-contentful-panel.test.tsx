import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetContentfulPanel } from "@/components/fleet-contentful-panel";
describe("FleetContentfulPanel", () => { it("renders", () => {
    const { container } = render(<FleetContentfulPanel spaces={5} active={5} entries={200000} apiCalls={20000000} />);
    expect(container.textContent).toContain("Contentful");
}); });
