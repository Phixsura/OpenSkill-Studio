import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetReplicaSetV9Panel } from "@/components/fleet-replica-set-v9-panel";
describe("FleetReplicaSetV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetReplicaSetV9Panel sets={20} ready={60} />);
    expect(container.textContent).toContain("Replica Set v9");
}); });
