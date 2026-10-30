import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-request-geo-restriction-card";

describe("RequestGeoRestrictionCard", () => {
  it("shows policy", () => {
    const { container } = render(<Card consumerId="c1" mode="allowlist" countries={["US", "CA"]} topCountries={[{ code: "US", count: 500 }]} appName="App" />);
    expect(container.textContent).toContain("Geo Restriction");
    expect(container.textContent).toContain("allowlist");
    expect(container.textContent).toContain("US");
    expect(container.textContent).toContain("CA");
    expect(container.textContent).toContain("500");
  });
  it("shows blocklist", () => {
    const { container } = render(<Card consumerId="c1" mode="blocklist" countries={["RU"]} topCountries={[]} appName="App" />);
    expect(container.textContent).toContain("blocklist");
    expect(container.textContent).toContain("RU");
  });
});
