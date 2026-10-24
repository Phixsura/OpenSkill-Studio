import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTlsInspectorV9Panel } from "@/components/fleet-tls-inspector-v9-panel";
describe("FleetTlsInspectorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetTlsInspectorV9Panel endpoints={100} tls13={95} />);
    expect(container.textContent).toContain("TLS Inspector v9");
}); });
