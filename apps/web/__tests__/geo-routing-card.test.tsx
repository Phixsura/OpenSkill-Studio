import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import GeoRoutingCard from "../src/components/geo-routing-card";

const regions = [
  {
    region_id: "us-east",
    name: "US East",
    endpoint: "https://us.api.com",
    countries: ["US", "CA"],
    request_count: 5000,
    active: true,
  },
  {
    region_id: "eu-west",
    name: "EU West",
    endpoint: "https://eu.api.com",
    countries: ["DE", "FR", "GB"],
    request_count: 3000,
    active: true,
  },
  {
    region_id: "ap-south",
    name: "AP South",
    endpoint: "https://ap.api.com",
    countries: ["IN", "SG"],
    request_count: 500,
    active: false,
  },
];

describe("GeoRoutingCard", () => {
  it("renders header", () => {
    const { container } = render(
      <GeoRoutingCard regions={regions} defaultRegion="us-east" appName="My App" />,
    );
    expect(container.textContent).toContain("Geo Routing");
  });

  it("shows active count", () => {
    const { container } = render(
      <GeoRoutingCard regions={regions} defaultRegion="" appName="App" />,
    );
    expect(container.textContent).toContain("2/3 active");
  });

  it("renders region names", () => {
    const { container } = render(
      <GeoRoutingCard regions={regions} defaultRegion="" appName="App" />,
    );
    expect(container.textContent).toContain("US East");
    expect(container.textContent).toContain("EU West");
  });

  it("shows default label", () => {
    const { container } = render(
      <GeoRoutingCard regions={regions} defaultRegion="us-east" appName="App" />,
    );
    expect(container.textContent).toContain("default");
  });

  it("shows country codes", () => {
    const { container } = render(
      <GeoRoutingCard regions={regions} defaultRegion="" appName="App" />,
    );
    expect(container.textContent).toContain("US");
    expect(container.textContent).toContain("DE");
  });

  it("shows request counts", () => {
    const { container } = render(
      <GeoRoutingCard regions={regions} defaultRegion="" appName="App" />,
    );
    expect(container.textContent).toContain("5.0K req");
  });

  it("shows empty state", () => {
    const { container } = render(<GeoRoutingCard regions={[]} defaultRegion="" appName="App" />);
    expect(container.textContent).toContain("No regions configured");
  });
});
