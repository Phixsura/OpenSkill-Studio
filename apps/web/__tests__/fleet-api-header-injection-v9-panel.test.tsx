import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiHeaderInjectionV9Panel } from "@/components/fleet-api-header-injection-v9-panel";
describe("FleetApiHeaderInjectionV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiHeaderInjectionV9Panel endpoints={100} blocked={10} />);
    expect(container.textContent).toContain("Header Injection v9");
}); });
