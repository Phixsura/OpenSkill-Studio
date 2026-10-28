import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RateQuotaCard from "../src/components/rate-quota-card";

const tiers = [
  {
    tier: "free",
    isCurrent: false,
    requests_per_day: 100,
    requests_per_minute: 10,
    storage_mb: 50,
    webhooks: 5,
  },
  {
    tier: "starter",
    isCurrent: true,
    requests_per_day: 1000,
    requests_per_minute: 60,
    storage_mb: 500,
    webhooks: 20,
  },
  {
    tier: "pro",
    isCurrent: false,
    requests_per_day: 10000,
    requests_per_minute: 300,
    storage_mb: 5000,
    webhooks: 100,
  },
];

describe("RateQuotaCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <RateQuotaCard tiers={tiers} appName="My App" currentTier="starter" />,
    );
    expect(container.textContent).toContain("Rate Quotas");
    expect(container.textContent).toContain("My App");
  });

  it("shows current tier badge", () => {
    const { container } = render(
      <RateQuotaCard tiers={tiers} appName="App" currentTier="starter" />,
    );
    expect(container.textContent).toContain("starter");
  });

  it("renders tier names", () => {
    const { container } = render(
      <RateQuotaCard tiers={tiers} appName="App" currentTier="starter" />,
    );
    expect(container.textContent).toContain("free");
    expect(container.textContent).toContain("starter");
    expect(container.textContent).toContain("pro");
  });

  it("shows current label on active tier", () => {
    const { container } = render(
      <RateQuotaCard tiers={tiers} appName="App" currentTier="starter" />,
    );
    expect(container.textContent).toContain("Current");
  });

  it("shows quota values", () => {
    const { container } = render(
      <RateQuotaCard tiers={tiers} appName="App" currentTier="starter" />,
    );
    expect(container.textContent).toContain("10K"); // pro daily
    expect(container.textContent).toContain("500 MB"); // starter storage
  });

  it("shows formatted numbers", () => {
    const { container } = render(<RateQuotaCard tiers={tiers} appName="App" currentTier="free" />);
    expect(container.textContent).toContain("100"); // free daily
    expect(container.textContent).toContain("1K"); // starter daily
  });
});
