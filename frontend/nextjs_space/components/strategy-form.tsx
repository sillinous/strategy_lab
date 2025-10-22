
'use client';

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Trash2, Plus } from "lucide-react";
import { Strategy, FormData, INDICATOR_TYPES, OPERATORS } from "@/lib/types";
import { strategyApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface StrategyFormProps {
  strategy?: Strategy;
}

export default function StrategyForm({ strategy }: StrategyFormProps) {
  const router = useRouter();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    name: strategy?.name || '',
    description: strategy?.description || '',
    indicators: strategy?.indicators || [],
    buy_conditions: strategy?.buy_conditions || [],
    sell_conditions: strategy?.sell_conditions || [],
  });

  const addIndicator = () => {
    setFormData(prev => ({
      ...prev,
      indicators: [...(prev?.indicators || []), { type: '', parameters: {} }],
    }));
  };

  const removeIndicator = (index: number) => {
    setFormData(prev => ({
      ...prev,
      indicators: prev?.indicators?.filter((_, i) => i !== index) || [],
    }));
  };

  const updateIndicator = (index: number, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      indicators: prev?.indicators?.map((indicator, i) => 
        i === index ? { ...indicator, [field]: value } : indicator
      ) || [],
    }));
  };

  const addCondition = (type: 'buy' | 'sell') => {
    const field = type === 'buy' ? 'buy_conditions' : 'sell_conditions';
    setFormData(prev => ({
      ...prev,
      [field]: [...(prev?.[field] || []), { indicator: '', operator: '', value: 0 }],
    }));
  };

  const removeCondition = (type: 'buy' | 'sell', index: number) => {
    const field = type === 'buy' ? 'buy_conditions' : 'sell_conditions';
    setFormData(prev => ({
      ...prev,
      [field]: prev?.[field]?.filter((_, i) => i !== index) || [],
    }));
  };

  const updateCondition = (type: 'buy' | 'sell', index: number, field: string, value: any) => {
    const conditionField = type === 'buy' ? 'buy_conditions' : 'sell_conditions';
    setFormData(prev => ({
      ...prev,
      [conditionField]: prev?.[conditionField]?.map((condition, i) => 
        i === index ? { ...condition, [field]: value } : condition
      ) || [],
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData?.name?.trim()) {
      toast({ title: "Error", description: "Strategy name is required", variant: "destructive" });
      return;
    }

    setLoading(true);
    try {
      let result;
      if (strategy?.id) {
        result = await strategyApi.update(strategy.id, formData);
      } else {
        result = await strategyApi.create(formData);
      }

      if (result) {
        toast({ 
          title: "Success", 
          description: `Strategy ${strategy?.id ? 'updated' : 'created'} successfully` 
        });
        router.push('/strategies');
      } else {
        throw new Error('Failed to save strategy');
      }
    } catch (error) {
      toast({ 
        title: "Error", 
        description: `Failed to ${strategy?.id ? 'update' : 'create'} strategy`, 
        variant: "destructive" 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Basic Information */}
      <Card>
        <CardHeader>
          <CardTitle>Strategy Details</CardTitle>
          <CardDescription>Basic information about your trading strategy</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Strategy Name *</Label>
            <Input
              id="name"
              value={formData?.name || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="Enter strategy name"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData?.description || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Describe your strategy"
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      {/* Indicators */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle>Technical Indicators</CardTitle>
            <CardDescription>Configure the indicators your strategy will use</CardDescription>
          </div>
          <Button type="button" onClick={addIndicator} size="sm">
            <Plus className="h-4 w-4 mr-1" />
            Add Indicator
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {formData?.indicators?.map((indicator, index) => (
            <div key={index} className="p-4 border rounded-lg space-y-3">
              <div className="flex justify-between items-center">
                <h4 className="font-medium">Indicator {index + 1}</h4>
                <Button 
                  type="button" 
                  variant="outline" 
                  size="sm"
                  onClick={() => removeIndicator(index)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Type</Label>
                  <Select 
                    value={indicator?.type || "all"} 
                    onValueChange={(value) => updateIndicator(index, 'type', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select indicator type" />
                    </SelectTrigger>
                    <SelectContent>
                      {INDICATOR_TYPES?.map((type) => (
                        <SelectItem key={type?.value} value={type?.value || "all"}>
                          {type?.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label>Period</Label>
                  <Input
                    type="number"
                    placeholder="e.g., 14"
                    value={indicator?.parameters?.period || ''}
                    onChange={(e) => updateIndicator(index, 'parameters', 
                      { ...indicator?.parameters, period: parseInt(e.target.value) || 0 })}
                  />
                </div>
              </div>
            </div>
          )) ?? []}
        </CardContent>
      </Card>

      {/* Buy Conditions */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle>Buy Conditions</CardTitle>
            <CardDescription>Define when to enter long positions</CardDescription>
          </div>
          <Button type="button" onClick={() => addCondition('buy')} size="sm">
            <Plus className="h-4 w-4 mr-1" />
            Add Condition
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {formData?.buy_conditions?.map((condition, index) => (
            <div key={index} className="p-4 border rounded-lg space-y-3">
              <div className="flex justify-between items-center">
                <h4 className="font-medium">Buy Condition {index + 1}</h4>
                <Button 
                  type="button" 
                  variant="outline" 
                  size="sm"
                  onClick={() => removeCondition('buy', index)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Indicator</Label>
                  <Input
                    placeholder="e.g., rsi, sma_20"
                    value={condition?.indicator || ''}
                    onChange={(e) => updateCondition('buy', index, 'indicator', e.target.value)}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label>Operator</Label>
                  <Select 
                    value={condition?.operator || "all"} 
                    onValueChange={(value) => updateCondition('buy', index, 'operator', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select operator" />
                    </SelectTrigger>
                    <SelectContent>
                      {OPERATORS?.map((op) => (
                        <SelectItem key={op?.value} value={op?.value || "all"}>
                          {op?.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label>Value</Label>
                  <Input
                    type="number"
                    step="0.01"
                    placeholder="e.g., 30"
                    value={condition?.value || ''}
                    onChange={(e) => updateCondition('buy', index, 'value', 
                      parseFloat(e.target.value) || 0)}
                  />
                </div>
              </div>
            </div>
          )) ?? []}
        </CardContent>
      </Card>

      {/* Sell Conditions */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle>Sell Conditions</CardTitle>
            <CardDescription>Define when to exit positions</CardDescription>
          </div>
          <Button type="button" onClick={() => addCondition('sell')} size="sm">
            <Plus className="h-4 w-4 mr-1" />
            Add Condition
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {formData?.sell_conditions?.map((condition, index) => (
            <div key={index} className="p-4 border rounded-lg space-y-3">
              <div className="flex justify-between items-center">
                <h4 className="font-medium">Sell Condition {index + 1}</h4>
                <Button 
                  type="button" 
                  variant="outline" 
                  size="sm"
                  onClick={() => removeCondition('sell', index)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Indicator</Label>
                  <Input
                    placeholder="e.g., rsi, sma_20"
                    value={condition?.indicator || ''}
                    onChange={(e) => updateCondition('sell', index, 'indicator', e.target.value)}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label>Operator</Label>
                  <Select 
                    value={condition?.operator || "all"} 
                    onValueChange={(value) => updateCondition('sell', index, 'operator', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select operator" />
                    </SelectTrigger>
                    <SelectContent>
                      {OPERATORS?.map((op) => (
                        <SelectItem key={op?.value} value={op?.value || "all"}>
                          {op?.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label>Value</Label>
                  <Input
                    type="number"
                    step="0.01"
                    placeholder="e.g., 70"
                    value={condition?.value || ''}
                    onChange={(e) => updateCondition('sell', index, 'value', 
                      parseFloat(e.target.value) || 0)}
                  />
                </div>
              </div>
            </div>
          )) ?? []}
        </CardContent>
      </Card>

      {/* Submit Button */}
      <div className="flex justify-end space-x-4">
        <Button 
          type="button" 
          variant="outline"
          onClick={() => router.push('/strategies')}
        >
          Cancel
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? 'Saving...' : strategy?.id ? 'Update Strategy' : 'Create Strategy'}
        </Button>
      </div>
    </form>
  );
}
