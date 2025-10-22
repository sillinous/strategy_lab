'use client';

import { useState } from "react";
import StrategyList from "@/components/strategy-list";
import PrebuiltStrategies from "@/components/prebuilt-strategies";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Sparkles, FolderOpen } from "lucide-react";

export default function StrategiesPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleStrategyImported = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Trading Strategies</h1>
          <p className="text-muted-foreground">
            Create, import, and optimize your trading strategies
          </p>
        </div>
      </div>
      
      <Tabs defaultValue="my-strategies" className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="my-strategies" className="flex items-center gap-2">
            <FolderOpen className="h-4 w-4" />
            My Strategies
          </TabsTrigger>
          <TabsTrigger value="prebuilt" className="flex items-center gap-2">
            <Sparkles className="h-4 w-4" />
            Pre-built Strategies
          </TabsTrigger>
        </TabsList>

        <TabsContent value="my-strategies" className="mt-6">
          <StrategyList key={refreshKey} />
        </TabsContent>

        <TabsContent value="prebuilt" className="mt-6">
          <div className="space-y-4">
            <div className="p-4 bg-blue-500/10 rounded-lg border border-blue-500/20">
              <h3 className="font-semibold text-blue-700 dark:text-blue-400 mb-1">
                🚀 Ready-to-Use Strategies
              </h3>
              <p className="text-sm text-muted-foreground">
                Import proven trading strategies and let the system autonomously optimize them 
                for better performance. Each strategy can be tweaked and evolved to maximize returns.
              </p>
            </div>
            <PrebuiltStrategies onImport={handleStrategyImported} />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
