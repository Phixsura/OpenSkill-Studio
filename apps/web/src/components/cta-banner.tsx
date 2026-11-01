"use client";

interface CtaBannerProps { title: string; subtitle: string; button: string;
  icon: string; variant: string; onAction: () => void; }

export function CtaBanner({ title, subtitle, button, icon, variant, onAction }: CtaBannerProps) {
  return (
    <div className={`rounded-xl p-6 text-center ${
      variant === "primary" ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white" :
      "bg-gray-50 dark:bg-gray-800 border dark:border-gray-700"
    }`}>
      <p className="text-3xl mb-2">{icon}</p>
      <h3 className="text-lg font-bold mb-1">{title}</h3>
      <p className={`text-sm mb-4 ${variant === "primary" ? "opacity-90" : "text-gray-500"}`}>{subtitle}</p>
      <button onClick={onAction}
        className={`px-6 py-2.5 rounded-lg text-sm font-medium ${
          variant === "primary" ? "bg-white text-gray-900 hover:bg-gray-100" :
          "bg-blue-600 text-white hover:bg-blue-700"
        }`}>{button}</button>
    </div>
  );
}
