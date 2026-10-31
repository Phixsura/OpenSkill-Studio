import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIIPGeolocationTrackerCard from "../src/components/api-developer-api-ip-geolocation-tracker-card";

const countries = [
  { country: "US", request_count: 5000, unique_ip_count: 120, error_count: 5 },
  { country: "DE", request_count: 2000, unique_ip_count: 45, error_count: 0 },
];

describe("APIDeveloperAPIIPGeolocationTrackerCard", () => {
  it("shows geo data", () => {
    const { container } = render(<APIDeveloperAPIIPGeolocationTrackerCard countries={countries} totalCountries={15} totalUniqueIPs={500} appName="App" />);
    expect(container.textContent).toContain("IP Geolocation");
    expect(container.textContent).toContain("15 countries");
    expect(container.textContent).toContain("500 unique IPs");
    expect(container.textContent).toContain("US");
    expect(container.textContent).toContain("5,000 reqs");
    expect(container.textContent).toContain("5 err");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIIPGeolocationTrackerCard countries={[]} totalCountries={0} totalUniqueIPs={0} appName="App" />);
    expect(container.textContent).toContain("No geo data");
  });
});
