import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiRequestCorrelationIdCard from "../src/components/api-developer-api-api-developer-api-api-request-correlation-id-card";

const records = [{ correlation_id: "corr-abc", origin_service: "gateway", hops: ["gateway", "auth", "users"], hop_count: 3, completed: true }];

describe("APIDeveloperAPIApiDeveloperApiApiRequestCorrelationIdCard", () => {
  it("shows correlations", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiRequestCorrelationIdCard records={records} activeCount={2} appName="App" />);
    expect(container.textContent).toContain("Correlation IDs");
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("corr-abc");
    expect(container.textContent).toContain("3 hops");
    expect(container.textContent).toContain("gateway");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiRequestCorrelationIdCard records={[]} activeCount={0} appName="App" />);
    expect(container.textContent).toContain("No correlations");
  });
});
