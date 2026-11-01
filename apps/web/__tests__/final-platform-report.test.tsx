import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FinalPlatformReport } from "@/components/final-platform-report";
describe("FinalPlatformReport", () => { it("renders", () => {
    const { container } = render(<FinalPlatformReport />);
    expect(container.textContent).toContain("FINAL PLATFORM REPORT");
    expect(container.textContent).toContain("3M+");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
