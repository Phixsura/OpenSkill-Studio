import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RespHeaderPanel } from "@/components/resp-header-panel";
describe("RespHeaderPanel", () => {
  it("renders issues", () => {
    const { container } = render(
      <RespHeaderPanel headersCount={2} secure={false} valid={false}
        issues={[
          { header: "X-Frame-Options", issue: "missing_security_header" },
          { header: "CSP", issue: "missing_security_header" },
        ]} />
    );
    expect(container.textContent).toContain("Response Headers");
    expect(container.textContent).toContain("2 headers");
    expect(container.textContent).toContain("Issues");
    expect(container.textContent).toContain("X-Frame-Options");
    expect(container.textContent).toContain("missing_security_header");
  });
});
