import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiSdkV9Panel } from "@/components/fleet-api-sdk-v9-panel";
describe("FleetApiSdkV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiSdkV9Panel sdks={10} languages={5} />);
    expect(container.textContent).toContain("API SDK v9");
}); });
