import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiClientSdkV9Panel } from "@/components/fleet-api-client-sdk-v9-panel";
describe("FleetApiClientSdkV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiClientSdkV9Panel sdks={10} downloads={500000} />);
    expect(container.textContent).toContain("Client SDK v9");
}); });
