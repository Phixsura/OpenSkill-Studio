import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrClassifyPanel } from "@/components/err-classify-panel";

describe("ErrClassifyPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ErrClassifyPanel total={10} retryable={6} nonRetryable={4}
        byClass={{ transient: 3, server: 3, client: 2, data: 2 }} />
    );
    expect(container.textContent).toContain("Error Classification");
    expect(container.textContent).toContain("10 errors");
    expect(container.textContent).toContain("6 retryable");
    expect(container.textContent).toContain("transient: 3");
    expect(container.textContent).toContain("server: 3");
  });
});
