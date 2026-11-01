import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiStreamProcPanel } from "@/components/fleet-ai-stream-proc-panel";
describe("FleetAiStreamProcPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiStreamProcPanel processors={8} active={8} eps={5000000} partitions={512} lag={50} />);
    expect(container.textContent).toContain("Stream Processor");
}); });
