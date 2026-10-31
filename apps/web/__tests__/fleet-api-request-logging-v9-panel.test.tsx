import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiRequestLoggingV9Panel } from "@/components/fleet-api-request-logging-v9-panel";
describe("FleetApiRequestLoggingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiRequestLoggingV9Panel loggers={10} entries={1000000} />);
    expect(container.textContent).toContain("Request Logging v9");
}); });
