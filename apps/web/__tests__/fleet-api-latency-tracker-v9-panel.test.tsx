import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiLatencyTrackerV9Panel } from "@/components/fleet-api-latency-tracker-v9-panel";
describe("FleetApiLatencyTrackerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiLatencyTrackerV9Panel endpoints={200} p99={100} />);
    expect(container.textContent).toContain("API Latency Tracker v9");
}); });
