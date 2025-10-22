
'use client';

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Zap, TrendingUp, Target, Award, Clock } from "lucide-react";
import { optimizationApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface OptimizationDialogProps {
  strategyId: string;
  strategyName: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onComplete?: () => void;
}

export default function OptimizationDialog({
  strategyId,
  strategyName,
  open,
  onOpenChange,
  onComplete,
}: OptimizationDialogProps) {
  const [optimizing, setOptimizing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [symbol, setSymbol] = useState('AAPL');
  const [period, setPeriod] = useState('1y');
  const [maxIterations, setMaxIterations] = useState(50);
  const [optimizationMetric, setOptimizationMetric] = useState('sharpe_ratio');
  const { toast } = useToast();

  const handleOptimize = async () => {
    setOptimizing(true);
    setResult(null);

    try {
      const optimizationResult = await optimizationApi.optimize(strategyId, {
        symbol,
        period,
        optimization_metric: optimizationMetric,
        max_iterations: maxIterations,
      });

      setResult(optimizationResult);
      toast({
        title: "Optimization Complete",
        description: `Tested ${optimizationResult?.results?.total_tested} variations`,
      });
      onComplete?.();
    } catch (error: any) {
      toast({
        title: "Optimization Failed",
        description: error?.message || "Failed to optimize strategy",
        variant: "destructive",
      });
    } finally {
      setOptimizing(false);
    }
  };

  const handleAutonomousImprove = async () => {
    setOptimizing(true);
    setResult(null);

    try {
      const improvementResult = await optimizationApi.autonomousImprove(strategyId, {
        symbol,
        period,
        max_generations: 3,
      });

      setResult({
        ...improvementResult,
        isAutonomous: true,
      });

      toast({
        title: "Autonomous Improvement Complete",
        description: `Created ${improvementResult?.total_generations} evolved generations`,
      });
      onComplete?.();
    } catch (error: any) {
      toast({
        title: "Improvement Failed",
        description: error?.message || "Failed to improve strategy",
        variant: "destructive",
      });
    } finally {
      setOptimizing(false);
    }
  };

  const formatMetricName = (metric: string) => {
    return metric.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-primary" />
            Optimize Strategy: {strategyName}
          </DialogTitle>
          <DialogDescription>
            Automatically test parameter variations to find the best performing configuration
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {!result && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="symbol">Symbol</Label>
                  <Input
                    id="symbol"
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value?.toUpperCase() || '')}
                    placeholder="AAPL"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="period">Period</Label>
                  <Select value={period} onValueChange={setPeriod}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="6mo">6 Months</SelectItem>
                      <SelectItem value="1y">1 Year</SelectItem>
                      <SelectItem value="2y">2 Years</SelectItem>
                      <SelectItem value="5y">5 Years</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="metric">Optimization Metric</Label>
                  <Select value={optimizationMetric} onValueChange={setOptimizationMetric}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sharpe_ratio">Sharpe Ratio</SelectItem>
                      <SelectItem value="total_return">Total Return</SelectItem>
                      <SelectItem value="win_rate">Win Rate</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="iterations">Max Iterations</Label>
                  <Input
                    id="iterations"
                    type="number"
                    value={maxIterations}
                    onChange={(e) => setMaxIterations(parseInt(e.target.value || '50'))}
                    min={10}
                    max={100}
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <Button
                  onClick={handleOptimize}
                  disabled={optimizing}
                  className="flex-1"
                >
                  <Target className="h-4 w-4 mr-2" />
                  {optimizing ? 'Optimizing...' : 'Optimize Parameters'}
                </Button>

                <Button
                  onClick={handleAutonomousImprove}
                  disabled={optimizing}
                  variant="secondary"
                  className="flex-1"
                >
                  <Zap className="h-4 w-4 mr-2" />
                  {optimizing ? 'Evolving...' : 'Autonomous Improve (3 Gen)'}
                </Button>
              </div>

              {optimizing && (
                <div className="space-y-2 text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                  <p className="text-sm text-muted-foreground">
                    This may take a minute... Testing strategies in parallel.
                  </p>
                </div>
              )}
            </>
          )}

          {result && !result.isAutonomous && (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-green-500/10 rounded-lg border border-green-500/20">
                <div className="flex items-center gap-3">
                  <Award className="h-8 w-8 text-green-600" />
                  <div>
                    <div className="font-semibold text-green-700 dark:text-green-400">
                      Optimization Complete!
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Tested {result?.results?.total_tested} variations
                    </div>
                  </div>
                </div>
                <Badge className="bg-green-600 text-white">
                  Best Found
                </Badge>
              </div>

              {result?.results?.top_strategies?.[0] && (
                <>
                  <div className="grid grid-cols-3 gap-4">
                    {Object.entries(result.results.top_strategies[0].metrics)
                      .filter(([key]) => ['sharpe_ratio', 'total_return', 'win_rate'].includes(key))
                      .map(([key, value]: [string, any]) => (
                        <div key={key} className="p-3 bg-muted rounded-lg text-center">
                          <div className="text-xs text-muted-foreground mb-1">
                            {formatMetricName(key)}
                          </div>
                          <div className="text-lg font-bold">
                            {typeof value === 'number' 
                              ? (key.includes('rate') || key.includes('return')) 
                                ? `${(value * 100).toFixed(1)}%`
                                : value.toFixed(2)
                              : value}
                          </div>
                        </div>
                      ))}
                  </div>

                  <div>
                    <div className="text-sm font-medium mb-2">Optimized Parameters</div>
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(result.results.top_strategies[0].parameters || {}).map(
                        ([param, value]: [string, any]) => (
                          <div key={param} className="flex justify-between p-2 bg-muted rounded text-sm">
                            <span className="font-medium">{param}:</span>
                            <span>{value}</span>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                </>
              )}

              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setResult(null)} className="flex-1">
                  Run Another
                </Button>
                <Button onClick={() => onOpenChange(false)} className="flex-1">
                  Close
                </Button>
              </div>
            </div>
          )}

          {result && result.isAutonomous && (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-purple-500/10 rounded-lg border border-purple-500/20">
                <div className="flex items-center gap-3">
                  <Zap className="h-8 w-8 text-purple-600" />
                  <div>
                    <div className="font-semibold text-purple-700 dark:text-purple-400">
                      Autonomous Evolution Complete!
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Created {result?.total_generations} evolved generations
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                {result?.generations?.map((gen: any, index: number) => (
                  <div key={index} className="p-4 bg-muted rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <div className="font-semibold">Generation {gen.generation}</div>
                      <Badge>
                        Sharpe: {gen.metrics?.sharpe_ratio?.toFixed(2) || 'N/A'}
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {gen.strategy_name}
                    </div>
                    <div className="grid grid-cols-3 gap-2 mt-2 text-xs">
                      <div>
                        Return: {((gen.metrics?.total_return || 0) * 100).toFixed(1)}%
                      </div>
                      <div>
                        Win Rate: {((gen.metrics?.win_rate || 0) * 100).toFixed(1)}%
                      </div>
                      <div>
                        Trades: {gen.metrics?.num_trades || 0}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="p-4 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <div className="text-sm font-medium mb-1">✨ What happened?</div>
                <div className="text-sm text-muted-foreground">
                  The system autonomously tested parameter variations, identified the best 
                  performers, and created evolved versions. Check your strategies list for 
                  the new generations!
                </div>
              </div>

              <Button onClick={() => onOpenChange(false)} className="w-full">
                View Evolved Strategies
              </Button>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
