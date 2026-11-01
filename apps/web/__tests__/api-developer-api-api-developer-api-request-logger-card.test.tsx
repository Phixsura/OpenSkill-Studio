import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiRequestLoggerCard from "../src/components/api-developer-api-api-developer-api-request-logger-card";

const logs = [
  { log_id: "l1", method: "GET", path: "/api/users", status_code: 200, duration_ms: 45, consumer_id: "c1" },
  { log_id: "l2", method: "POST", path: "/api/orders", status_code: 500, duration_ms: 120, consumer_id: "c2" },
];

describe("APIDeveloperAPIApiDeveloperApiRequestLoggerCard", () => {
  it("shows request logs", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiRequestLoggerCard logs={logs} totalCount={5000} errorCount={50} appName="App" />);
    expect(container.textContent).toContain("Request Logger");
    expect(container.textContent).toContain("5,000 logs");
    expect(container.textContent).toContain("50 errors");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("500");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiRequestLoggerCard logs={[]} totalCount={0} errorCount={0} appName="App" />);
    expect(container.textContent).toContain("No request logs");
  });
});
