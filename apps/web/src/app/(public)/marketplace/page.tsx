"use client";

import Link from "next/link";

const CATEGORIES = [
  { icon: "🔌", title: "Connectors", desc: "LMS, HRIS, CRM integrations", href: "/marketplace/apps?category=connector" },
  { icon: "⚡", title: "Workflow Adapters", desc: "AI provider adapters", href: "/marketplace/apps?category=workflow_adapter" },
  { icon: "🖥️", title: "UI Extensions", desc: "Dashboard cards, panels", href: "/marketplace/apps?category=ui_extension" },
  { icon: "📊", title: "Analytics", desc: "Reporting and insights", href: "/marketplace/apps?category=analytics" },
  { icon: "🤖", title: "Automation", desc: "Event-driven workflows", href: "/marketplace/apps?category=automation" },
  { icon: "📦", title: "Content Packs", desc: "Skill & workflow bundles", href: "/marketplace/apps?category=content_pack" },
];

export default function MarketplaceLandingPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-12">
      {/* Hero */}
      <div className="mb-12 text-center">
        <h1 className="text-4xl font-bold">OpenSkill Marketplace</h1>
        <p className="mt-3 text-lg text-gray-600 dark:text-gray-400">
          Extend your training platform with apps, connectors, and integrations
          built by the community
        </p>
        <div className="mt-6 flex justify-center gap-4">
          <Link
            href="/marketplace/apps"
            className="rounded-lg bg-blue-600 px-6 py-2.5 font-medium text-white hover:bg-blue-700"
          >
            Browse Apps
          </Link>
          <Link
            href="/registry"
            className="rounded-lg border px-6 py-2.5 font-medium hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-800"
          >
            Explore Skill Packs
          </Link>
        </div>
      </div>

      {/* Categories */}
      <div className="mb-12">
        <h2 className="mb-6 text-center text-2xl font-semibold">Browse by Category</h2>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
          {CATEGORIES.map((cat) => (
            <Link
              key={cat.title}
              href={cat.href}
              className="group rounded-xl border p-6 text-center transition-all hover:border-blue-500 hover:shadow-md dark:border-gray-700"
            >
              <div className="mb-3 text-4xl">{cat.icon}</div>
              <h3 className="font-semibold group-hover:text-blue-600">{cat.title}</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{cat.desc}</p>
            </Link>
          ))}
        </div>
      </div>

      {/* For Developers */}
      <div className="rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 p-8 text-white md:p-12">
        <div className="grid items-center gap-8 md:grid-cols-2">
          <div>
            <h2 className="text-2xl font-bold md:text-3xl">Build for OpenSkill</h2>
            <p className="mt-3 text-blue-100">
              Create apps, connectors, and extensions that reach thousands of
              training organizations. Our SDK, sandbox runtime, and marketplace
              make it easy to build, test, and distribute.
            </p>
            <div className="mt-6 flex gap-3">
              <Link
                href="/dashboard/developer"
                className="rounded-lg bg-white px-5 py-2 font-medium text-blue-600 hover:bg-blue-50"
              >
                Get Started
              </Link>
              <Link
                href="/dashboard/developer/docs"
                className="rounded-lg border border-white/30 px-5 py-2 font-medium hover:bg-white/10"
              >
                Read the Docs
              </Link>
            </div>
          </div>
          <div className="space-y-3 text-sm">
            <div className="flex items-center gap-3 rounded-lg bg-white/10 p-3">
              <span className="text-lg">📦</span>
              <span>TypeScript & Python SDKs</span>
            </div>
            <div className="flex items-center gap-3 rounded-lg bg-white/10 p-3">
              <span className="text-lg">🔒</span>
              <span>Sandboxed runtime with CPU/memory limits</span>
            </div>
            <div className="flex items-center gap-3 rounded-lg bg-white/10 p-3">
              <span className="text-lg">🔔</span>
              <span>35 event types with HMAC-signed webhooks</span>
            </div>
            <div className="flex items-center gap-3 rounded-lg bg-white/10 p-3">
              <span className="text-lg">🧩</span>
              <span>8 UI extension surfaces</span>
            </div>
            <div className="flex items-center gap-3 rounded-lg bg-white/10 p-3">
              <span className="text-lg">✅</span>
              <span>Automated review & conformance suite</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
