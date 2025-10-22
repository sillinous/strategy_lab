
'use client';

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sparkles, Download, TrendingUp, Target } from "lucide-react";
import { prebuiltApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface PrebuiltStrategy {
  name: string;
  description: string;
  category: string;
  risk_level: string;
  tags: string[];
  expected_win_rate: number;
  expected_sharpe: number;
  config: any;
  optimizable_params: any;
}

export default function PrebuiltStrategies({ onImport }: { onImport?: () => void }) {
  const [strategies, setStrategies] = useState<PrebuiltStrategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStrategy, setSelectedStrategy] = useState<PrebuiltStrategy | null>(null);
  const [importing, setImporting] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadStrategies();
  }, []);

  const loadStrategies = async () => {
    try {
      const data = await prebuiltApi.getAll();
      setStrategies(data || []);
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to load pre-built strategies", 
        variant: "destructive" 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async (strategyName: string) => {
    setImporting(true);
    try {
      await prebuiltApi.import(strategyName);
      toast({ 
        title: "Success", 
        description: `"${strategyName}" imported to your strategies` 
      });
      setSelectedStrategy(null);
      onImport?.();
    } catch (error: any) {
      toast({ 
        title: "Error", 
        description: error?.message || "Failed to import strategy", 
        variant: "destructive" 
      });
    } finally {
      setImporting(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk?.toUpperCase()) {
      case 'LOW':
        return 'bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20';
      case 'MEDIUM':
        return 'bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-yellow-500/20';
      case 'HIGH':
        return 'bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20';
      default:
        return 'bg-gray-500/10 text-gray-700 dark:text-gray-400 border-gray-500/20';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category?.toLowerCase()) {
      case 'trend following':
        return <TrendingUp className="h-4 w-4" />;
      case 'mean reversion':
        return <Target className="h-4 w-4" />;
      default:
        return <Sparkles className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {strategies?.map((strategy) => (
          <Card 
            key={strategy?.name} 
            className="hover:shadow-lg transition-shadow cursor-pointer"
            onClick={() => setSelectedStrategy(strategy)}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    {getCategoryIcon(strategy?.category)}
                    <CardTitle className="text-lg">{strategy?.name}</CardTitle>
                  </div>
                  <CardDescription className="line-clamp-2">
                    {strategy?.description}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Category</span>
                  <Badge variant="outline">{strategy?.category}</Badge>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Risk Level</span>
                  <Badge className={`${getRiskColor(strategy?.risk_level)} border`}>
                    {strategy?.risk_level}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-2 border-t">
                  <div className="text-center">
                    <div className="text-xs text-muted-foreground">Win Rate</div>
                    <div className="text-sm font-semibold">
                      {((strategy?.expected_win_rate || 0) * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-xs text-muted-foreground">Sharpe</div>
                    <div className="text-sm font-semibold">
                      {(strategy?.expected_sharpe || 0).toFixed(2)}
                    </div>
                  </div>
                </div>

                <div className="flex flex-wrap gap-1 pt-2">
                  {strategy?.tags?.slice(0, 3).map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        )) ?? []}
      </div>

      <Dialog open={!!selectedStrategy} onOpenChange={(open) => !open && setSelectedStrategy(null)}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {selectedStrategy && getCategoryIcon(selectedStrategy.category)}
              {selectedStrategy?.name}
            </DialogTitle>
            <DialogDescription>
              {selectedStrategy?.description}
            </DialogDescription>
          </DialogHeader>

          {selectedStrategy && (
            <div className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium mb-1">Category</div>
                  <Badge variant="outline">{selectedStrategy.category}</Badge>
                </div>
                <div>
                  <div className="text-sm font-medium mb-1">Risk Level</div>
                  <Badge className={`${getRiskColor(selectedStrategy.risk_level)} border`}>
                    {selectedStrategy.risk_level}
                  </Badge>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 p-4 bg-muted rounded-lg">
                <div>
                  <div className="text-sm text-muted-foreground">Expected Win Rate</div>
                  <div className="text-2xl font-bold">
                    {((selectedStrategy.expected_win_rate || 0) * 100).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Expected Sharpe Ratio</div>
                  <div className="text-2xl font-bold">
                    {(selectedStrategy.expected_sharpe || 0).toFixed(2)}
                  </div>
                </div>
              </div>

              <div>
                <div className="text-sm font-medium mb-2">Indicators Used</div>
                <div className="flex flex-wrap gap-2">
                  {selectedStrategy.config?.indicators?.map((indicator: any, index: number) => (
                    <Badge key={index} variant="secondary">
                      {indicator?.type}
                      {indicator?.period && ` (${indicator.period})`}
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium">Entry Condition</div>
                <div className="p-3 bg-green-500/10 text-green-700 dark:text-green-400 rounded text-sm font-mono">
                  {selectedStrategy.config?.entry_rules?.description}
                </div>
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium">Exit Condition</div>
                <div className="p-3 bg-red-500/10 text-red-700 dark:text-red-400 rounded text-sm font-mono">
                  {selectedStrategy.config?.exit_rules?.description}
                </div>
              </div>

              <div>
                <div className="text-sm font-medium mb-2">Tags</div>
                <div className="flex flex-wrap gap-2">
                  {selectedStrategy.tags?.map((tag) => (
                    <Badge key={tag} variant="outline">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-4 border-t">
                <Button variant="outline" onClick={() => setSelectedStrategy(null)}>
                  Cancel
                </Button>
                <Button 
                  onClick={() => handleImport(selectedStrategy.name)}
                  disabled={importing}
                >
                  <Download className="h-4 w-4 mr-2" />
                  {importing ? 'Importing...' : 'Import Strategy'}
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
