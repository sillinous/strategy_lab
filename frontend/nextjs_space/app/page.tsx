
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { TrendingUp, BarChart3, Target, Activity } from "lucide-react";

export default function HomePage() {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4 py-12">
        <h1 className="text-4xl font-bold tracking-tight">Strategy Lab</h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Professional trading strategy development and backtesting platform for algorithmic traders
        </p>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="text-center">
            <Target className="h-12 w-12 mx-auto text-primary mb-2" />
            <CardTitle>Strategy Builder</CardTitle>
            <CardDescription>Create and configure custom trading strategies with indicators</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link href="/strategies/new">Build Strategy</Link>
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="text-center">
            <Activity className="h-12 w-12 mx-auto text-primary mb-2" />
            <CardTitle>Strategy Library</CardTitle>
            <CardDescription>Manage your saved strategies and their configurations</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline" className="w-full">
              <Link href="/strategies">View Strategies</Link>
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="text-center">
            <TrendingUp className="h-12 w-12 mx-auto text-primary mb-2" />
            <CardTitle>Backtesting</CardTitle>
            <CardDescription>Test your strategies against historical market data</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline" className="w-full">
              <Link href="/backtest">Run Backtest</Link>
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="text-center">
            <BarChart3 className="h-12 w-12 mx-auto text-primary mb-2" />
            <CardTitle>Results Analysis</CardTitle>
            <CardDescription>Analyze performance metrics and trading results</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline" className="w-full">
              <Link href="/results">View Results</Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Quick Stats */}
      <Card className="bg-muted/50">
        <CardHeader>
          <CardTitle className="text-center">Platform Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            <div>
              <div className="text-3xl font-bold text-primary">∞</div>
              <p className="text-sm text-muted-foreground">Unlimited Strategies</p>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary">⚡</div>
              <p className="text-sm text-muted-foreground">Fast Backtesting</p>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary">📊</div>
              <p className="text-sm text-muted-foreground">Detailed Analytics</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
