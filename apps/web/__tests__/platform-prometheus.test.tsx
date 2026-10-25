import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformPrometheus } from "@/components/platform-prometheus";
describe("PlatformPrometheus", () => { it("renders", () => {
    const { container } = render(<PlatformPrometheus />);
    expect(container.textContent).toContain("PROMETHEUS");
    expect(container.textContent).toContain("BROKEN");
}); });
