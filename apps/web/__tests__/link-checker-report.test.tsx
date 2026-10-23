import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LinkCheckerReport } from "@/components/link-checker-report";

describe("LinkCheckerReport", () => {
  const results = [
    { url: "https://example.com", valid: true, status: "ok" },
    { url: "https://broken.link", valid: false, status: "404" },
  ];
  it("renders link results", () => {
    const { container } = render(<LinkCheckerReport results={results} valid={1} broken={1} health="warning" />);
    expect(container.textContent).toContain("example.com");
    expect(container.textContent).toContain("1✓ 1✗");
    expect(container.textContent).toContain("ok");
  });
});
