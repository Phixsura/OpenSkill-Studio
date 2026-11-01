import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFastifyPanel } from "@/components/fleet-fastify-panel";
describe("FleetFastifyPanel", () => { it("renders", () => {
    const { container } = render(<FleetFastifyPanel instances={10} healthy={10} rps={200000} p95={12} />);
    expect(container.textContent).toContain("Fastify");
    expect(container.textContent).toContain("200,000");
}); });
