import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiPlaygroundCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-playground-card";

const requests = [
  { request_id: "r1", method: "GET", path: "/api/users", status_code: 200, duration_ms: 45, saved: true },
  { request_id: "r2", method: "POST", path: "/api/orders", status_code: 500, duration_ms: 120, saved: false },
];

describe("Card", () => {
  it("shows playground", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiPlaygroundCard requests={requests} stats={{ total: 50, saved: 5, errors: 3 }} appName="App" />);
    expect(container.textContent).toContain("API Playground");
    expect(container.textContent).toContain("50 requests");
    expect(container.textContent).toContain("5 saved");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("500");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiPlaygroundCard requests={[]} stats={{ total: 0, saved: 0, errors: 0 }} appName="App" />);
    expect(container.textContent).toContain("No playground requests");
  });
});
