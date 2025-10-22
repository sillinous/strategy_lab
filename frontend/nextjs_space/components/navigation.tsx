
'use client';

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ModeToggle } from "@/components/ui/mode-toggle";
import { TrendingUp, Target, Activity, BarChart3, Home } from "lucide-react";

const navigation = [
  { name: "Home", href: "/", icon: Home },
  { name: "Strategy Builder", href: "/strategies/new", icon: Target },
  { name: "Strategies", href: "/strategies", icon: Activity },
  { name: "Backtest", href: "/backtest", icon: TrendingUp },
  { name: "Results", href: "/results", icon: BarChart3 },
];

export default function Navigation() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto max-w-7xl">
        <div className="flex h-14 items-center justify-between px-4">
          <div className="flex items-center space-x-6">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-md flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="hidden sm:inline-block font-bold text-lg">Strategy Lab</span>
            </Link>

            <nav className="flex items-center space-x-1">
              {navigation?.map((item) => {
                const Icon = item?.icon;
                return (
                  <Button
                    key={item?.href}
                    variant={pathname === item?.href ? "default" : "ghost"}
                    size="sm"
                    asChild
                    className={cn(
                      "hidden sm:flex",
                      pathname === item?.href && "bg-primary text-primary-foreground"
                    )}
                  >
                    <Link href={item?.href || "#"}>
                      {Icon && <Icon className="h-4 w-4 mr-1" />}
                      {item?.name}
                    </Link>
                  </Button>
                );
              })}
            </nav>
          </div>

          <ModeToggle />
        </div>
      </div>
    </header>
  );
}
