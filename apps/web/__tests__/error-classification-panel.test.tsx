import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorClassificationPanel } from "@/components/error-classification-panel";

describe("ErrorClassificationPanel", () => {
  it("renders classifications", () => {
    const { container } = render(
      <ErrorClassificationPanel total={10} hasCritical={true}
        byCategory={{ server: 3, auth: 4, validation: 3 }}
        bySeverity={{ critical: 3, high: 4, low: 3 }} />
    );
    expect(container.textContent).toContain("Error Classification");
    expect(container.textContent).toContain("10 errors");
    expect(container.textContent).toContain("Critical");
    expect(container.textContent).toContain("server");
    expect(container.textContent).toContain("auth");
  });
});
