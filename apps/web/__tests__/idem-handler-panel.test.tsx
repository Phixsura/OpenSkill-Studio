import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IdemHandlerPanel } from "@/components/idem-handler-panel";
describe("IdemHandlerPanel", () => {
  it("renders", () => {
    const { container } = render(
      <IdemHandlerPanel storedResults={500} ttlSeconds={86400} cacheHits={1200} />
    );
    expect(container.textContent).toContain("Idempotent Handler");
    expect(container.textContent).toContain("500 stored");
    expect(container.textContent).toContain("86400s TTL");
    expect(container.textContent).toContain("1200 hits");
  });
});
