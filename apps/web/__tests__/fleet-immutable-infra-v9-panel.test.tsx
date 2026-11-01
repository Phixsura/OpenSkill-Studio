import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetImmutableInfraV9Panel } from "@/components/fleet-immutable-infra-v9-panel";
describe("FleetImmutableInfraV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetImmutableInfraV9Panel instances={100} immutable={100} />);
    expect(container.textContent).toContain("Immutable Infra v9");
}); });
