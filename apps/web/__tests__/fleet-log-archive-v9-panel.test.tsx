import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLogArchiveV9Panel } from "@/components/fleet-log-archive-v9-panel";
describe("FleetLogArchiveV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetLogArchiveV9Panel archives={50} sizeTb={100} />);
    expect(container.textContent).toContain("Log Archive v9");
}); });
