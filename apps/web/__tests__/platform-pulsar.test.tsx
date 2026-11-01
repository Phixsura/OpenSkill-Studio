import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformPulsar } from "@/components/platform-pulsar";
describe("PlatformPulsar", () => { it("renders", () => {
    const { container } = render(<PlatformPulsar />);
    expect(container.textContent).toContain("PULSAR");
    expect(container.textContent).toContain("ALL GREEN");
}); });
