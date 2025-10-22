
'use client';

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TrendingUp, TrendingDown, DollarSign, Percent, Target, BarChart3 } from "lucide-react";
import { BacktestResult } from "@/lib/types";
import { backtestApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import EquityCurveChart from "./equity-curve-chart";
import TradesTable from "./trades-table";

export default function ResultsDashboard() {
  const searchParams = useSearchParams();
  const { toast } = useToast();
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const backtestId = searchParams?.get('backtest');
    if (backtestId) {
      loadResults(backtestId);
    }
  }, [searchParams]);

  const loadResults = async (backtestId: string) => {
    setLoading(true);
    try {
      const data = await backtestApi.getResults(backtestId);
      setResult(data);
      if (!data) {
        toast({ 
          title: "Not Found", 
          description: "Backtest results not found", 
          variant: "destructive" 
        });
      }
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to load backtest results", 
        variant: "destructive" 
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!result) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <BarChart3 className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">No backtest results found</h3>
          <p className="text-muted-foreground text-center mb-4">
            Run a backtest to see performance metrics and analysis
          </p>
          <Button asChild>
            <a href="/backtest">Run New Backtest</a>
          </Button>
        </CardContent>
      </Card>
    );
  }

  const isProfit = (result?.total_return || 0) > 0;
  const winRatePercent = ((result?.win_rate || 0) * 100).toFixed(1);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold">Backtest Results</h2>
          <p className="text-muted-foreground">
            {result?.symbol} • {result?.start_date} to {result?.end_date}
          </p>
        </div>
        <Badge variant={isProfit ? "default" : "destructive"} className="text-sm">
          {isProfit ? "Profitable" : "Loss"}
        </Badge>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Return</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${(result?.total_return || 0).toLocaleString('en-US', { 
                minimumFractionDigits: 2, 
                maximumFractionDigits: 2 
              })}
            </div>
            <p className="text-xs text-muted-foreground">
              {((result?.total_return_percentage || 0) * 100).toFixed(2)}% return
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{winRatePercent}%</div>
            <p className="text-xs text-muted-foreground">
              {result?.winning_trades} of {result?.total_trades} trades
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Max Drawdown</CardTitle>
            <TrendingDown className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {((result?.max_drawdown || 0) * 100).toFixed(2)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Maximum portfolio decline
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sharpe Ratio</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(result?.sharpe_ratio || 0).toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">
              Risk-adjusted returns
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Equity Curve Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Equity Curve</CardTitle>
          <CardDescription>Portfolio value over time</CardDescription>
        </CardHeader>
        <CardContent>
          <EquityCurveChart data={result?.equity_curve || []} />
        </CardContent>
      </Card>

      {/* Trades Table */}
      <Card>
        <CardHeader>
          <CardTitle>Trade History</CardTitle>
          <CardDescription>All trades executed during the backtest</CardDescription>
        </CardHeader>
        <CardContent>
          <TradesTable trades={result?.trades || []} />
        </CardContent>
      </Card>
    </div>
  );
}
