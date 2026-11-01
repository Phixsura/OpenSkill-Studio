import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRlEffectPanel } from "@/components/fleet-rl-effect-panel";
describe("FleetRlEffectPanel", () => { it("renders", () => {
    const { container } = render(<FleetRlEffectPanel totalRequests={100000} blocked={1000} falsePositives={10} precision={99} effective={true} />);
    expect(container.textContent).toContain("Rate Limiter");
    expect(container.textContent).toContain("99% precision");
}); });
