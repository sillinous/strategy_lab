
'use client';

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Edit2, Trash2, Plus, Target, Zap } from "lucide-react";
import { Strategy } from "@/lib/types";
import { strategyApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import OptimizationDialog from "./optimization-dialog";

export default function StrategyList() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [optimizingStrategy, setOptimizingStrategy] = useState<{ id: string; name: string } | null>(null);
  const { toast } = useToast();

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
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!window?.confirm?.(`Are you sure you want to delete "${name}"?`)) {
      return;
    }

    try {
      const success = await strategyApi.delete(id);
      if (success) {
        toast({ title: "Success", description: "Strategy deleted successfully" });
        setStrategies(prev => prev?.filter(s => s?.id !== id) || []);
      } else {
        throw new Error('Failed to delete strategy');
      }
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to delete strategy", 
        variant: "destructive" 
      });
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!strategies?.length) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Target className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">No strategies found</h3>
          <p className="text-muted-foreground text-center mb-4">
            Create your first trading strategy to get started with backtesting
          </p>
          <Button asChild>
            <Link href="/strategies/new">
              <Plus className="h-4 w-4 mr-1" />
              Create Strategy
            </Link>
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button asChild>
          <Link href="/strategies/new">
            <Plus className="h-4 w-4 mr-1" />
            New Strategy
          </Link>
        </Button>
      </div>

      <div className="grid gap-4">
        {strategies?.map((strategy) => (
          <Card key={strategy?.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-xl">{strategy?.name}</CardTitle>
                  <CardDescription className="mt-1">
                    {strategy?.description || 'No description provided'}
                  </CardDescription>
                </div>
                <div className="flex space-x-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setOptimizingStrategy({ 
                      id: strategy?.id || '', 
                      name: strategy?.name || '' 
                    })}
                  >
                    <Zap className="h-4 w-4 mr-1" />
                    Optimize
                  </Button>
                  <Button variant="outline" size="sm" asChild>
                    <Link href={`/strategies/edit/${strategy?.id}`}>
                      <Edit2 className="h-4 w-4 mr-1" />
                      Edit
                    </Link>
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleDelete(strategy?.id || '', strategy?.name || '')}
                  >
                    <Trash2 className="h-4 w-4 mr-1" />
                    Delete
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <h4 className="text-sm font-medium mb-2">Indicators</h4>
                  <div className="flex flex-wrap gap-2">
                    {strategy?.indicators?.map((indicator, index) => (
                      <Badge key={index} variant="secondary">
                        {indicator?.type?.toUpperCase()} 
                        {indicator?.parameters?.period ? ` (${indicator.parameters.period})` : ''}
                      </Badge>
                    )) ?? <span className="text-sm text-muted-foreground">No indicators</span>}
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-medium mb-2">Buy Conditions</h4>
                    <div className="space-y-1">
                      {strategy?.buy_conditions?.map((condition, index) => (
                        <div key={index} className="text-xs bg-green-500/10 text-green-700 dark:text-green-400 px-2 py-1 rounded">
                          {condition?.indicator} {condition?.operator} {condition?.value}
                        </div>
                      )) ?? <span className="text-xs text-muted-foreground">No buy conditions</span>}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium mb-2">Sell Conditions</h4>
                    <div className="space-y-1">
                      {strategy?.sell_conditions?.map((condition, index) => (
                        <div key={index} className="text-xs bg-red-500/10 text-red-700 dark:text-red-400 px-2 py-1 rounded">
                          {condition?.indicator} {condition?.operator} {condition?.value}
                        </div>
                      )) ?? <span className="text-xs text-muted-foreground">No sell conditions</span>}
                    </div>
                  </div>
                </div>
                
                <div className="flex justify-between items-center pt-2 text-xs text-muted-foreground">
                  <span>
                    Created: {new Date(strategy?.created_at || '').toLocaleDateString()}
                  </span>
                  <Button size="sm" asChild>
                    <Link href={`/backtest?strategy=${strategy?.id}`}>
                      Run Backtest
                    </Link>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )) ?? []}
      </div>

      {optimizingStrategy && (
        <OptimizationDialog
          strategyId={optimizingStrategy.id}
          strategyName={optimizingStrategy.name}
          open={!!optimizingStrategy}
          onOpenChange={(open) => !open && setOptimizingStrategy(null)}
          onComplete={loadStrategies}
        />
      )}
    </div>
  );
}
