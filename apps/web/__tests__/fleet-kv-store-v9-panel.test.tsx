import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetKvStoreV9Panel } from "@/components/fleet-kv-store-v9-panel";
describe("FleetKvStoreV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetKvStoreV9Panel clusters={3} ops={100000} />);
    expect(container.textContent).toContain("KV Store v9");
}); });
