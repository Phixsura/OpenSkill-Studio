import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSessionStoreV9Panel } from "@/components/fleet-session-store-v9-panel";
describe("FleetSessionStoreV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSessionStoreV9Panel active={5000} expired={10} />);
    expect(container.textContent).toContain("Session Store v9");
}); });
