import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEnvPromoterV9Panel } from "@/components/fleet-env-promoter-v9-panel";
describe("FleetEnvPromoterV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetEnvPromoterV9Panel promotions={50} blocked={0} />);
    expect(container.textContent).toContain("Env Promoter v9");
}); });
