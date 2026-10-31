import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiRequestDeduplicationCard from "../src/components/api-developer-api-api-request-deduplication-card";

describe("APIDeveloperAPIApiRequestDeduplicationCard", () => {
  it("shows dedup stats", () => {
    const { container } = render(<APIDeveloperAPIApiRequestDeduplicationCard stats={{ active_keys: 500, duplicate_hits: 150 }} appName="App" />);
    expect(container.textContent).toContain("Request Deduplication");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("150");
    expect(container.textContent).toContain("23%");
  });
});
