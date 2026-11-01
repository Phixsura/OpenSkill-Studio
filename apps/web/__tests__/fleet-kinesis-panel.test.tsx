import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetKinesisPanel } from "@/components/fleet-kinesis-panel";
describe("FleetKinesisPanel", () => { it("renders", () => {
    const { container } = render(<FleetKinesisPanel streams={5} active={5} shards={50} recordsPerSec={250000} />);
    expect(container.textContent).toContain("Kinesis");
    expect(container.textContent).toContain("250,000");
}); });
