
'use client';

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calendar, TrendingUp } from "lucide-react";
import { Strategy, BacktestRequest } from "@/lib/types";
import { strategyApi, backtestApi } from "@/lib/api";
import { useToast } from '@/hooks/use-toast';

export default function BacktestForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();
  
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<BacktestRequest>({
    strategy_id: searchParams?.get('strategy') || '',
    symbol: 'AAPL',
    start_date: '2023-01-01',
    end_date: '2024-01-01',
    initial_capital: 10000,
  });

  useEffect(() => {
    loadStrategies();
  }, []);

  const loadStrategies = async () => {
    try {
      const data = await strategyApi.getAll();
      setStrategies(data || []);
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to load strategies", 
        variant: "destructive" 
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData?.strategy_id) {
      toast({ title: "Error", description: "Please select a strategy", variant: "destructive" });
      return;
    }
    
    if (!formData?.symbol?.trim()) {
      toast({ title: "Error", description: "Please enter a symbol", variant: "destructive" });
      return;
    }

    setLoading(true);
    try {
      const result = await backtestApi.run(formData);
      
      if (result?.id) {
        toast({ title: "Success", description: "Backtest completed successfully" });
        router.push(`/results?backtest=${result.id}`);
      } else {
        throw new Error('Backtest failed');
      }
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to run backtest. Please check your parameters.", 
        variant: "destructive" 
      });
    } finally {
      setLoading(false);
    }
  };

  const selectedStrategy = strategies?.find(s => s?.id === formData?.strategy_id);

  return (
    <div className="max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Strategy Selection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Strategy Configuration
            </CardTitle>
            <CardDescription>Select the strategy you want to backtest</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Trading Strategy *</Label>
              <Select 
                value={formData?.strategy_id || "all"} 
                onValueChange={(value) => setFormData(prev => ({ ...prev, strategy_id: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a strategy to backtest" />
                </SelectTrigger>
                <SelectContent>
                  {strategies?.map((strategy) => (
                    <SelectItem key={strategy?.id} value={strategy?.id || "all"}>
                      {strategy?.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedStrategy && (
              <div className="p-3 bg-muted/50 rounded-lg">
                <h4 className="font-medium mb-1">{selectedStrategy?.name}</h4>
                <p className="text-sm text-muted-foreground">
                  {selectedStrategy?.description || 'No description provided'}
                </p>
                <div className="mt-2 text-xs">
                  <span className="font-medium">Indicators:</span>{' '}
                  {selectedStrategy?.indicators?.map(i => i?.type).join(', ') || 'None'}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Market Parameters */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Market Parameters
            </CardTitle>
            <CardDescription>Configure the market data and testing period</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="symbol">Symbol *</Label>
              <Input
                id="symbol"
                placeholder="e.g., AAPL, TSLA, SPY"
                value={formData?.symbol || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, symbol: e.target.value.toUpperCase() }))}
                required
              />
              <p className="text-xs text-muted-foreground">
                Enter the stock symbol you want to test against
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="start_date">Start Date *</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={formData?.start_date || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, start_date: e.target.value }))}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="end_date">End Date *</Label>
                <Input
                  id="end_date"
                  type="date"
                  value={formData?.end_date || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, end_date: e.target.value }))}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="initial_capital">Initial Capital</Label>
              <Input
                id="initial_capital"
                type="number"
                min="1000"
                step="1000"
                placeholder="10000"
                value={formData?.initial_capital || ''}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  initial_capital: parseInt(e.target.value) || 10000 
                }))}
              />
              <p className="text-xs text-muted-foreground">
                The amount of capital to start the backtest with (USD)
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Submit */}
        <div className="flex justify-center">
          <Button 
            type="submit" 
            disabled={loading || !formData?.strategy_id || !formData?.symbol}
            className="min-w-[200px]"
          >
            {loading ? 'Running Backtest...' : 'Run Backtest'}
          </Button>
        </div>
      </form>
    </div>
  );
}
