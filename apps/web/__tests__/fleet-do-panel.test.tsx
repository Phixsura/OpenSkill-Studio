import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDoPanel } from "@/components/fleet-do-panel";
describe("FleetDoPanel", () => { it("renders", () => {
    const { container } = render(<FleetDoPanel namespaces={5} activeObjects={50000} storageMb={2000} requests={25000000} />);
    expect(container.textContent).toContain("Durable Objects");
}); });
